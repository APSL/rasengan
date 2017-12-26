# -*- coding: utf-8 -*-

import os
import re
import codecs

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = codecs.open(os.path.join(package, '__init__.py'), encoding='utf-8').read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_author(package):
    """
    Return package author as listed in `__author__` in `init.py`.
    """
    init_py = codecs.open(os.path.join(package, '__init__.py'), encoding='utf-8').read()
    return re.search("^__author__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_email(package):
    """
    Return package email as listed in `__email__` in `init.py`.
    """
    init_py = codecs.open(os.path.join(package, '__init__.py'), encoding='utf-8').read()
    return re.search("^__email__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)

INSTALL_REQUIRES = [
    'click==6.7',
    'PyYAML==3.12',
    'requests==2.18.4',
    'dnspython==1.15.0',
    'pyOpenSSL==17.5.0',
    'colorlog==3.1.0'
]

setup(
    name='rasengan',
    version=get_version('rasengan'),
    include_package_data=True,
    packages=[
        'rasengan',
    ],
    url=u"https://github.com/apsl/rasengan",
    license='GPLv3',
    python_requires='>=3.4',
    install_requires=INSTALL_REQUIRES,
    entry_points="""
        [console_scripts]
        rasengan=rasengan.main:rasengan
    """,
    author=get_author('rasengan'),
    author_email=get_email('rasengan'),
    long_description=codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8').read(),
    description="""
    A tool to check if a list of domains configured in a yaml file
    have the redirections and DNS in a correct state.
    """
)
