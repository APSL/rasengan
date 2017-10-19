# Overview

This tool, `rasengan`, is a CLI that get a list of domains configured in a yaml
file and check it in a diferent ways:
  - Check the DNS resolution
  - Check redirects
  - Check content

The exit of the execution is an error if any of the checks fails.

# Usage example

    (rasengan) $ rasengan --config=check.yml --domains=goldcar.com,www.goldcar.com --loglevel=INFO
    19/10/2017 16:37 - ERROR - goldcar.com - DNS Check - KO -> expected: ['52.212.105.167'] and get: [u'52.212.105.167', u'52.51.179.76']
    19/10/2017 16:37 - INFO - goldcar.com - Redirect Status Code for http://goldcar.com - OK -> result: 301
    19/10/2017 16:37 - INFO - goldcar.com - Redirect Location for http://goldcar.com - OK -> result: https://www.goldcar.es/en/
    19/10/2017 16:37 - INFO - goldcar.com - Redirect Status Code for https://goldcar.com - OK -> result: 301
    19/10/2017 16:37 - INFO - goldcar.com - Redirect Location for https://goldcar.com - OK -> result: https://www.goldcar.es/en/
    19/10/2017 16:37 - INFO - www.goldcar.com - DNS Check - OK -> result: ['goldcarcom.aws.goldcar.ws.']
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Status Code for http://www.goldcar.com - OK -> result: 301
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Location for http://www.goldcar.com - OK -> result: https://www.goldcar.es/en/
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Status Code for https://www.goldcar.com - OK -> result: 301
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Location for https://www.goldcar.com - OK -> result: https://www.goldcar.es/en/
    (rasengan) $ echo $?
    1
    (rasengan) $ rasengan --config=check.yml --domains=www.goldcar.com --loglevel=INFO
    19/10/2017 16:37 - INFO - www.goldcar.com - DNS Check - OK -> result: ['goldcarcom.aws.goldcar.ws.']
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Status Code for http://www.goldcar.com - OK -> result: 301
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Location for http://www.goldcar.com - OK -> result: https://www.goldcar.es/en/
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Status Code for https://www.goldcar.com - OK -> result: 301
    19/10/2017 16:37 - INFO - www.goldcar.com - Redirect Location for https://www.goldcar.com - OK -> result: https://www.goldcar.es/en/
    (rasengan) $ echo $?
    0


# Install & configure

To install `rasengan``:

    pip install -U git+https://github.com/APSL/rasengan.git


## check.yml

At this file you can specify the different for a domain:

| Field          | Description                                                        |
|----------------|--------------------------------------------------------------------|
| `dns`          | Check the DNS resolution, expect domain_type and result            |
| `http`         | Request the domain from http, expect status_code, redirect or text |
| `https`        | Request the domain from http, expect status_code, redirect or text |
| `http_path`    | Request the domain from http with a path                           |

### Basic Example

    www.goldcar.com:
      dns:
        domain_type: CNAME
        expected: ['goldcarcom.aws.goldcar.ws.']
      http:
        status_code: 301
        redirect: https://www.goldcar.es/en/
      https:
        status_code: 301
        redirect: https://www.goldcar.es/en/
      http_path:
        path: /any_path/
        status_code: 301
        redirect: https://www.goldcar.es/en/

    goldcar.com:
      dns:
        domain_type: A
        expected: ['52.212.105.167', '52.51.179.76']
      http:
        status_code: 301
        redirect: https://www.goldcar.es/en/
      https:
        status_code: 301
        redirect: https://www.goldcar.es/en/
      http_path:
        path: /any_path/
        status_code: 301
        redirect: https://www.goldcar.es/en/