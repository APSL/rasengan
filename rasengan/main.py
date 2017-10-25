import yaml
import requests
import dns.resolver
import sys
import click
import logging
import rasengan.Colorer

# import ipdb; ipdb.set_trace()

# create logger
log = logging.getLogger('rasengan')
errors = 0

def initiate_log(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), 10)
    log.setLevel(numeric_level)
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  "%d/%m/%Y %H:%M")
    ch.setFormatter(formatter)
    log.addHandler(ch)

def check(result, expected, title):
    global errors
    if result == expected:
        message = 'OK -> result: {}'.format(result)
        log.info('{} - {}'.format(title, message))
        return True
    else:
        message = 'KO -> expected: {} and get: {}'.format(expected, result)
        log.error('{} - {}'.format(title, message))
        errors += 1
        return False

def check_in(result, expected, title):
    global errors
    if expected in result:
        message = 'OK -> Exists the phrase: {}'.format(expected)
        log.info('{} - {}'.format(title, message))
        return True
    else:
        message = 'KO -> Dont exists the phrase: {}'.format(expected)
        errors += 1
        log.error('{} - {}'.format(title, message))
        return False


def check_dns(domain, dns_dict):
    global errors
    result = []
    try:
        anwsers = dns.resolver.query(domain, dns_dict['domain_type'])
    except:
        anwsers = []
        result = ['Not a correct domain_type definition']
        errors += 1

    for rdata in anwsers:
        if dns_dict['domain_type'] == 'A':
            result.append(rdata.address)
        else:
            result.append(rdata.target.to_text())
    # result = socket.gethostbyname_ex(domain)[2]
    return check(sorted(result), sorted(dns_dict['expected']), '{} - DNS Check'.format(domain))

def check_url(domain, url, expected):
    global errors
    try:
        r = requests.get('{}'.format(url), allow_redirects=False)
    except:
        log.error('{} - KO - Problem requesting {}'.format(domain, url))
        errors += 1
        return False

    # Check the status code expected
    check(r.status_code, expected['status_code'], '{} - Redirect Status Code for {}'.format(domain, url))

    # If is a redirect check with the next Location
    if r.status_code in [301, 302]:
        check(r.headers['Location'], expected['redirect'], '{} - Redirect Location for {}'.format(domain, url))

    if expected['status_code'] == 200:
        check_in(r.text, expected['text'], '{} - Page content'.format(domain))


@click.command()
@click.option('--config', default='rasengan.yml', help='Name of file to check')
@click.option('--domains', default='',
    help='Check only this list of domain (comma separated)')
@click.option('--loglevel', default='INFO', help='Log level')
def rasengan(config, domains, loglevel):
    """Check all the domains in the file"""

    initiate_log(loglevel)

    selected_domains = [x.strip() for x in domains.split(',')]

    with open(config, 'r') as ymlfile:
        d_domains = yaml.safe_load(ymlfile)

        # Check only one domain if passed by argument in cli
        for domain, d in d_domains.items():
            if domains and (domain not in selected_domains):
                continue

            # expected DNS resolution
            if 'dns' in d:
                check_dns(domain, d['dns'])

            # redirect en http
            if 'http' in d:
                check_url(domain, 'http://{}'.format(domain), d['http'])

            # redirect en https
            if 'https' in d:
                check_url(domain, 'https://{}'.format(domain), d['https'])

            # redirect en http
            if 'http_path' in d:
                for label, d_path in d['http_path'].items():
                    check_url(domain, 'http://{}{}'.format(domain, d_path['path']), d_path)

    if errors > 0:
        sys.exit(1)

if __name__ == '__main__':
    rasengan()
