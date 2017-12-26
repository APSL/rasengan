# Overview

`rasengan`, is a command-line tool for automated testing of multiple kind of integrations tests for domains, with 
a simple and flexible YAML definition syntax.
The yaml file can contain multiple domains and we could check it in a diferent ways:
  - Check the DNS resolution
  - Check redirects
  - Check content
  - Check SSL expiration date
  - Check SSL Qualys grade

The exit of the execution is an error if any of the checks fails.
You can use a mrpe parameter to get MRPE simple and resume output.  


# Install & configure

To install `rasengan`:

    pip install -U git+https://github.com/APSL/rasengan.git


## rasengan.yml

At this file you can specify the different for a domain:

| Field          | Description                                                        |
|----------------|--------------------------------------------------------------------|
| `dns`          | Check the DNS resolution, expect domain_type and result            |
| `ssl`          | Check the SSL status of the domain qualys test and expire date     |
| `http`         | Request the domain from http, expect status_code, redirect or text. The default value for protocol is https, and default path is '/' |

## Usage

    rasengan --help
    Usage: rasengan [OPTIONS]

      Check all the domains in the file

    Options:
      -c, --config TEXT      Name of file to check
      -d, --domains TEXT     Check only this list of domain (comma separated)
      -l, --loglevel TEXT    Log level
      -w, --workers INTEGER  Number of threads to make the requests
      --mrpe / --no-mrpe     MRPE output (disable logging options)
      --help                 Show this message and exit.


## Basic Example
    www.goldcar.es:
      ssl:
        grade: A
        days_to_expire: 10
      dns:
        domain_type: CNAME
        expected: 
          - 'k8pii.x.incapdns.net.'
      http:
        main: 
          status_code: 301
          protocol: http
          redirect: https://www.goldcar.es/
        main_https:
          status_code: 200
          text: Alquiler de coches

## Usage example

    $ rasengan -c rasengan.yml -l INFO --domains www.goldcar.com
    2017-12-24 02:34:32,371 INFO     www.goldcar.com - DNS Check - OK -> result: ['goldcarcom.aws.goldcar.ws.']
    2017-12-24 02:34:32,630 INFO     www.goldcar.com - (From desktop) - Status Code for http://www.goldcar.com/ - OK -> result: 301
    2017-12-24 02:34:32,630 INFO     www.goldcar.com - (From desktop) - Redirect Location for http://www.goldcar.com/ - OK -> result: https://www.goldcar.es/en/
    2017-12-24 02:34:32,810 INFO     www.goldcar.com - SSL Expires at 2019-06-07 16:24:21
    2017-12-24 02:34:32,880 INFO     www.goldcar.com - (From desktop) - Status Code for https://www.goldcar.com/ - OK -> result: 301
    2017-12-24 02:34:32,881 INFO     www.goldcar.com - (From desktop) - Redirect Location for https://www.goldcar.com/ - OK -> result: https://www.goldcar.es/en/
    2017-12-24 02:34:32,884 INFO     www.goldcar.com - (From desktop) - Status Code for https://www.goldcar.com/any_path/ - OK -> result: 301
    2017-12-24 02:34:32,885 INFO     www.goldcar.com - (From desktop) - Redirect Location for https://www.goldcar.com/any_path/ - OK -> result: https://www.goldcar.es/en/
    2017-12-24 02:34:35,367 INFO     www.goldcar.com - SSL Qualys grade - OK -> result: A

    (rasengan) $ echo $?
    0

## Future work

    - Use a option to get output in check_mrpe format. (in progress)
    - Count warnings too (now only errors)

## Acknowledgements
  
`rasengan` makes use of several open-source projects:

  - [click](http://click.pocoo.org/5/), for manage the command-line options.
  - [requests](http://docs.python-requests.org/en/master/), for HTTP requests.
  - [pyyaml](https://github.com/yaml/pyyaml), for the manage the data syntax.
  - [colorlog](https://github.com/borntyping/python-colorlog), for formatting terminal outputs.
  - [dnspython](http://www.dnspython.org/), for manage the DNS queries.
  - [pyOpenSSL](https://pypi.python.org/pypi/pyOpenSSL), for manage the ssl expiration checks.
  - [SSL Qualys API](https://www.ssllabs.com/projects/ssllabs-apis/), for check the grade of security in SSL.