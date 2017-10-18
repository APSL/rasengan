import yaml
import requests
import dns.resolver
from termcolor import colored
# import ipdb; ipdb.set_trace()

def check(result, expected, title):
    if result == expected:
        message = colored('OK -> result: {}'.format(result), 'green')
    else:
        message = colored('KO -> expected: {} and get: {}'.format(expected, result), 'red')
    print '{} - {}'.format(title, message)

def check_in(result, expected, title):
    if expected in result:
        message = colored('OK -> Exists the phrase: {}'.format(expected), 'green')
    else:
        message = colored('KO -> Dont exists the phrase: {}'.format(expected), 'red')
    print '{} - {}'.format(title, message)

def check_dns(domain, dns_dict):
    result = []
    anwsers = dns.resolver.query(domain, dns_dict['domain_type'])
    for rdata in anwsers:
        if dns_dict['domain_type'] == 'A':
            result.append(rdata.address)
        else:
            result.append(rdata.target.to_text())
    # result = socket.gethostbyname_ex(domain)[2]
    check(sorted(result), sorted(dns_dict['expected']), 'DNS Check')

def check_url(url, expected):
    r = requests.get('{}'.format(url), allow_redirects=False)

    # Check the status code expected
    check(r.status_code, expected['status_code'], 'Redirect Status Code')

    # If is a redirect check with the next Location
    if r.status_code in [301, 302]:
        check(r.headers['Location'], expected['redirect'], 'Redirect Location for {}'.format(url))

    if expected['status_code'] == 200:
        check_in(r.text, expected['text'], 'Page content')

with open("goldcar.yml", 'r') as ymlfile:
    domains = yaml.safe_load(ymlfile)

for domain, d in domains.items():

    print(colored(domain,'blue'))

    # expected DNS resolution
    if 'dns' in d:
        check_dns(domain, d['dns'])

    # redirect en http
    if 'http' in d:
        check_url('http://{}'.format(domain), d['http'])

    # redirect en https
    if 'https' in d:
        check_url('https://{}'.format(domain), d['https'])

    # 200 -> chequear fragmento de codigo de respuesta
    # subdominio de idioma
