Rasengan
=========

.. image:: https://img.shields.io/pypi/v/rasengan.svg
    :target: https://pypi.python.org/pypi/rasengan/

.. image:: https://travis-ci.org/APSL/rasengan.svg?branch=master
    :target: https://travis-ci.org/APSL/rasengan

Overview
--------

``rasengan``, is a command-line tool for automated testing of multiple
kind of integrations tests for domains, with a simple and flexible YAML
definition syntax. The yaml file can contain multiple domains and we
could check it in a diferent ways: 

  - Check the DNS resolution 
  - Checkredirects, status code and expected URL in the redirect 
  - Check http requests and the content text 
  - Check http using different user-agents 
  - Check SSL expiration date 
  - Check SSL Qualys grade

The exit of the execution is an error if any of the checks fails. You
can use a mrpe parameter to get MRPE simple and resume output.

Install & configure
-------------------

``rasengan`` is developed and tested with a python 3 version. We require
>3.4 to install it.

To install ``rasengan`` we can use the PyPI package:

::

    pip install rasengan

rasengan.yml
------------

At this file you can specify the different for a domain:

+------------+-----------------------------------------------------------------------+
| Field      | Description                                                           |
+============+=======================================================================+
| ``dns``    | Check the DNS resolution, expect domain\_type and result              |
+------------+-----------------------------------------------------------------------+
| ``ssl``    | Check the SSL status of the domain qualys test and expire date        |
+------------+-----------------------------------------------------------------------+
| ``http``   | Request the domain from http, expect status\_code, redirect or text   |
+------------+-----------------------------------------------------------------------+

Options in plugins
------------------

-  **dns**:

   -  *domain\_type*: CNAME, A or another type of expected resolution in
      the domain.
   -  *expected*: list of IPs or domains expected in the result.

-  **ssl**:

   -  *grade*: Qualys test expected grade.
   -  *days\_to\_expire*: expiration days limit warning in the https
      certificate for the domain.

-  **http**:

   -  *status\_code*: 200, 301, 302, 404, etc. Status code in the http
      request.
   -  *protocol*: http or https, do the request over different http
      protocol. Default https.
   -  *redirect*: expected redirect URL when you configure status code
      in 301 or 302.
   -  *path*: The url path to check in the domain. Default is '/'.
   -  *text*: check text in the result page when you expect 200 code.
   -  *user\_agent*: use a custom user\_agent for the request or stored
      one from keys: mobile, desktop, google\_desktop, google\_mobile.
   -  *auth\_user*: username in http auth.
   -  *auth\_password*: password in http auth .
Usage
-----

::

    $ rasengan --help
    Usage: rasengan [OPTIONS]

      Check all the domains in the file

    Options:
      -c, --config TEXT      Name of file to check. Default rasengan.yml
      -d, --domains TEXT     Check only this list of domain (comma separated)
      -l, --loglevel TEXT    Log level. Default INFO
      -w, --workers INTEGER  Number of threads to make the requests. Default 20.
      --mrpe / --no-mrpe     MRPE output (disable logging options). Default False, and if True disable loglevel.
      --help                 Show this message and exit.

Basic Example
-------------

::

    version: 0.2.5
    domains:
      www.apsl.net:
        ssl:
          grade: F
          days_to_expire: 10
        dns:
          domain_type: CNAME
          expected: 
            - apsl.net.
        http:
          main: 
            status_code: 301
            protocol: http
            redirect: https://www.apsl.net/
          main_https:
            status_code: 200
            text: Expertos en desarrollos web
          mobile:
            status_code: 200
            user_agent: mobile
            text: Expertos en desarrollos web           
      apsl.net:
        dns:
          domain_type: A
          expected: 
            - 148.251.84.231
        http:
          main_redirect:        
            protocol: http
            status_code: 301
            redirect: https://www.apsl.net/
          https_redirect:
            protocol: https
            status_code: 301
            redirect: https://www.apsl.net/

Usage example
-------------

::

    $ rasengan -c rasengan.yml 
    2017-12-26 03:38:01,250 INFO     www.apsl.net - DNS Check - OK -> result: ['apsl.net.']
    2017-12-26 03:38:01,309 INFO     apsl.net - DNS Check - OK -> result: ['148.251.84.231']
    2017-12-26 03:38:01,722 INFO     www.apsl.net - [desktop] - Status Code for http://www.apsl.net/ - OK -> result: 301
    2017-12-26 03:38:01,722 INFO     apsl.net - [desktop] - Status Code for http://apsl.net/ - OK -> result: 301
    2017-12-26 03:38:01,723 INFO     www.apsl.net - [desktop] - Redirect Location for http://www.apsl.net/ - OK -> result: https://www.apsl.net/                                
    2017-12-26 03:38:01,723 INFO     apsl.net - [desktop] - Redirect Location for http://apsl.net/ - OK -> result: https://www.apsl.net/
    2017-12-26 03:38:01,820 INFO     www.apsl.net - SSL Expires at 2018-01-17 23:59:59
    2017-12-26 03:38:01,936 INFO     www.apsl.net - [desktop] - Status Code for https://www.apsl.net/ - OK -> result: 200
    2017-12-26 03:38:01,938 INFO     www.apsl.net - [desktop] - Page content for https://www.apsl.net/ - OK -> Exists the phrase: Expertos en desarrollos web
    2017-12-26 03:38:01,958 INFO     apsl.net - [desktop] - Status Code for https://apsl.net/ - OK -> result: 301
    2017-12-26 03:38:01,960 INFO     www.apsl.net - [mobile] - Status Code for https://www.apsl.net/ - OK -> result: 200
    2017-12-26 03:38:01,960 INFO     apsl.net - [desktop] - Redirect Location for https://apsl.net/ - OK -> result: https://www.apsl.net/
    2017-12-26 03:38:01,962 INFO     www.apsl.net - [mobile] - Page content for https://www.apsl.net/ - OK -> Exists the phrase: Expertos en desarrollos web
    2017-12-26 03:38:03,353 INFO     www.apsl.net - SSL Qualys grade - OK -> result: F

    (rasengan) $ echo $?
    0

    (rasengan) $ rasengan -c rasengan.yml --mrpe
    Checks OK: 11 -- 

Future work
-----------

::

    - Integrate tavern to check APIs
    - Check http with authentication
    - Check http response time
    - Manage and show exceptions ocurred in Future threads

Acknowledgements
----------------

``rasengan`` makes use of several open-source projects:

-  `click <http://click.pocoo.org/5/>`__, for manage the command-line
   options.
-  `requests <http://docs.python-requests.org/en/master/>`__, for HTTP
   requests.
-  `pyyaml <https://github.com/yaml/pyyaml>`__, for the manage the data
   syntax.
-  `colorlog <https://github.com/borntyping/python-colorlog>`__, for
   formatting terminal outputs.
-  `dnspython <http://www.dnspython.org/>`__, for manage the DNS
   queries.
-  `pyOpenSSL <https://pypi.python.org/pypi/pyOpenSSL>`__, for manage
   the ssl expiration checks.
-  `SSL Qualys API <https://www.ssllabs.com/projects/ssllabs-apis/>`__,
   for check the grade of security in SSL.
