from .__init__ import __version__
import yaml
import requests
import dns.resolver
import sys
import click
import logging
from concurrent.futures import ThreadPoolExecutor, wait
from rasengan.ssllabsscanner import resultsFromCache    
import OpenSSL
import ssl, socket
from datetime import datetime
import colorlog


resume = {
    'oks': 0,
    'errors': 0,
    'warnings': 0,
    'domains_warning': [],
    'domains_error': []
}

user_agents = {
    'mobile': 'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19',
    'desktop': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'google_desktop': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'google_mobile': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

NAGIOS_CODES = {
    'OK': 0,
    'WARNING': 1,
    'CRITICAL': 2,
    'UNKNOWN': 3,
    'DEPENDENT': 4
}

def initiate_log(loglevel):
    global log
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    handler.setFormatter(formatter)
    log = colorlog.getLogger('rasengan')
    log.addHandler(handler)
    
    numeric_level = getattr(logging, loglevel.upper(), 10)
    log.setLevel(numeric_level)
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)

def check(result, expected, title, domain):
    if result == expected:
        message = 'OK -> result: {}'.format(result)
        log.info('{} - {}'.format(title, message))
        resume['oks'] += 1
        return True
    else:
        message = 'KO -> expected: {} and get: {}'.format(expected, result)
        log.error('{} - {}'.format(title, message))
        resume['errors'] += 1
        resume['domains_error'].append(domain)
        return False

def check_in(result, expected, title, domain):
    if expected in result:
        message = 'OK -> Exists the phrase: {}'.format(expected)
        log.info('{} - {}'.format(title, message))
        resume.oks += 1
        return True
    else:
        message = 'KO -> Dont exists the phrase: {}'.format(expected)
        resume['errors'] += 1
        resume['domains_error'].append(domain)
        log.error('{} - {}'.format(title, message))
        return False


def check_dns(domain, dns_dict):
    result = []
    try:
        anwsers = dns.resolver.query(domain, dns_dict['domain_type'])
    except:
        anwsers = []
        result = ['Not a correct domain_type definition']
        resume['errors'] += 1
        resume['domains_error'].append(domain)
    for rdata in anwsers:
        if dns_dict['domain_type'] == 'A':
            result.append(rdata.address)
        else:
            result.append(rdata.target.to_text())
    # result = socket.gethostbyname_ex(domain)[2]
    return check(sorted(result), sorted(dns_dict['expected']), '{} - DNS Check'.format(domain), domain)

def check_url(domain, data, timeout=1):

    # Montamos la URL con los valores por defecto (https y path a /)
    url = '{}://{}{}'.format( 
        data.get('protocol', 'https'),  
        domain, 
        data.get('path', '/')
    )

    user_agent = data.get('user_agent', 'desktop')
    if user_agent in user_agents:
        ua = user_agents[user_agent]
        text_from = '[{}]'.format(user_agent)
    else:
        ua = user_agent
        text_from = '[{}]'.format(ua)

    try:
        headers = {
            'User-Agent': ua 
        }
        r = requests.get('{}'.format(url), allow_redirects=False, headers=headers, timeout=timeout)
    except:
        log.error('{} - KO - Problem requesting {}'.format(domain, url))
        resume['errors'] += 1
        resume['domains_error'].append(domain)
        return False

    # Check the status code expected
    check(r.status_code, data['status_code'], '{} - {} - Status Code for {}'.format(domain,text_from, url), domain)

    # If is a redirect check with the next Location
    if data['status_code'] in [301, 302]:
        if 'Location' in r.headers:
            check(r.headers['Location'], data['redirect'], '{} - {} - Redirect Location for {}'.format(domain,text_from, url), domain)
        else:
            message = 'KO -> Expect a redirect but not found it: {} - {}'.format(domain, url)
            resume['errors'] += 1
            resume['domains_error'].append(domain)
            log.error('{}'.format(message))

    if data['status_code'] == 200:
        check_in(r.text, data.get('text','<--NOTEXTDEFINED-->'), '{} - {} - Page content for {}'.format(domain,text_from, url), domain)

def check_qualys(domain, data):
    if data['grade']:
        a = resultsFromCache(domain)
        if a['status'] == 'READY':
            grade = a['endpoints'][0]['grade']
            check(grade, data['grade'], '{} - SSL Qualys grade'.format(domain), domain)
        elif a['status'] == 'IN_PROGRESS':
            resume['warnings'] += 1
            resume['domains_warning'].append(domain)
            log.warning('{} - SSL Qualys grade - In progress'.format(domain))

def check_ssl(domain, data):
    if data['days_to_expire']:        
        cert = ssl.get_server_certificate((domain, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        date_cert = datetime.strptime(x509.get_notAfter().decode('ascii'),"%Y%m%d%H%M%SZ")
        expire_in = date_cert - datetime.now()
        if expire_in.days < data['days_to_expire']:
            log.error('{} - SSL Expires at {} (< {})'.format(domain, date_cert, data['days_to_expire']))
            resume['errors'] += 1
            resume['domains_error'].append(domain)
        else:
            log.info('{} - SSL Expires at {}'.format(domain, date_cert))

@click.command()
@click.option('--config', '-c', default='rasengan.yml', help='Name of file to check. Default rasengan.yml')
@click.option('--domains', '-d', default='',
    help='Check only this list of domain (comma separated)')
@click.option('--loglevel', '-l', default='INFO', help='Log level. Default INFO.')
@click.option('--workers', '-w', default=20, help='Number of threads to make the requests. Default 20.')
@click.option('--mrpe/--no-mrpe', default=False, help='MRPE output (disable logging options). Default false. An if True disable loglevel.')
def rasengan(config, domains, loglevel, workers, mrpe):
    """Check all the domains in the file"""

    if mrpe:
        loglevel = 'CRITICAL'
    initiate_log(loglevel)

    executor = ThreadPoolExecutor(max_workers=workers)

    selected_domains = [x.strip() for x in domains.split(',')]

    with open(config, 'r') as ymlfile:
        loaded = yaml.safe_load(ymlfile)

        # Check rasengan version defined in file
        if loaded['version'] != __version__:
            print('Rasegan version problem. Installed {} and expected {}'.format(__version__, loaded['version']))
            sys.exit(NAGIOS_CODES['CRITICAL'])            

        # Check only one domain if passed by argument in cli
        for domain, d in loaded['domains'].items():
            if domains and (domain not in selected_domains):
                continue

            dns_exists = 'dns' in d
            dns_ok = False
            # expected DNS resolution
            if dns_exists:
                dns_ok = check_dns(domain, d['dns'])

            if not dns_exists or dns_ok:
                if 'http' in d:
                    for label, d_path in d['http'].items():
                        executor.submit( check_url, domain, d_path )
                if 'ssl' in d:
                    if 'grade' in d['ssl']:
                        executor.submit( check_qualys, domain, d['ssl'])
                    if 'days_to_expire' in d['ssl']:
                        executor.submit( check_ssl, domain, d['ssl'])
                        
    executor.shutdown(wait=True)

    message = 'Checks OK: {}'.format(resume['oks'])
    message += " -- "

    if resume['errors'] > 0:
        message_error = "Errors: {}, domains: {}".format(resume['errors'], ', '.join(resume['domains_error']))
        message += message_error
        message += " -- "
    
    if resume['warnings'] > 0:
        message_warning = "Warnings: {}, domains: {}".format(resume['warnings'], ', '.join(resume['domains_warning']))
        message += message_warning
        
    if mrpe: 
        print(message)

    if resume['errors'] > 0:
        sys.exit(NAGIOS_CODES['CRITICAL'])

    if resume['warnings'] > 0:
        sys.exit(NAGIOS_CODES['WARNING'])

    sys.exit(NAGIOS_CODES['OK'])

if __name__ == '__main__':
    rasengan()
