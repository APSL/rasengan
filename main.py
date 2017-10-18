import yaml
import requests
import dns.resolver
from termcolor import colored
import sys

debug = False

# import ipdb; ipdb.set_trace()

def check(result, expected, title):
    print_result = True
    if result == expected:
        message = colored('OK -> result: {}'.format(result), 'green')
        if not debug:
            print_result = False
    else:
        message = colored('KO -> expected: {} and get: {}'.format(expected, result), 'red')
    if print_result:
        print '{} - {}'.format(title, message)

def check_in(result, expected, title):
    print_result = True
    if expected in result:
        if not debug:
            print_result = False
        message = colored('OK -> Exists the phrase: {}'.format(expected), 'green')
    else:
        message = colored('KO -> Dont exists the phrase: {}'.format(expected), 'red')
    if print_result:
        print '{} - {}'.format(title, message)

def check_dns(domain, dns_dict):
    result = []
    try:
        anwsers = dns.resolver.query(domain, dns_dict['domain_type'])
    except:
        anwsers = []
        result = ['Not a correct domain_type definition']

    for rdata in anwsers:
        if dns_dict['domain_type'] == 'A':
            result.append(rdata.address)
        else:
            result.append(rdata.target.to_text())
    # result = socket.gethostbyname_ex(domain)[2]
    check(sorted(result), sorted(dns_dict['expected']), 'DNS Check')

def check_url(url, expected):
    try:
        r = requests.get('{}'.format(url), allow_redirects=False)
    except:
        print(colored('KO - Problem requesting {}'.format(url),'red'))
        return False

    # Check the status code expected
    check(r.status_code, expected['status_code'], 'Redirect Status Code for {}'.format(url))

    # If is a redirect check with the next Location
    if r.status_code in [301, 302]:
        check(r.headers['Location'], expected['redirect'], 'Redirect Location for {}'.format(url))

    if expected['status_code'] == 200:
        check_in(r.text, expected['text'], 'Page content')

with open("goldcar.yml", 'r') as ymlfile:
    domains = yaml.safe_load(ymlfile)

    for domain, d in domains.items():
        # Check only one domain if passed by argument in cli
        if len(sys.argv) > 1:
            if domain != sys.argv[1]:
                continue

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

        # redirect en http
        if 'http_root' in d:
            check_url('http://{}{}'.format(domain, d['http_root']['path']), d['http_root'])

        print
