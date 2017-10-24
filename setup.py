# -*- coding: utf-8 -*-

from sys import version_info
from setuptools import setup

INSTALL_REQUIRES = [
    'click==6.7',
    'PyYAML==3.12',
    'requests==2.18.4',
    'dnspython==1.15.0'
]

setup(
    name='rasengan',
    version='0.1.2',
    include_package_data=True,
    packages=[
        'rasengan',
    ],
    url=u"https://github.com/apsl/rasengan",
    license='GPLv3',
    install_requires=INSTALL_REQUIRES,
    entry_points="""
        [console_scripts]
        rasengan=rasengan.main:rasengan
    """,
    author=u"Edu Herraiz",
    author_email=u"eherraiz@apsl.net",
    description="""
    A tool to check if a list of domains configured in a yaml file
    have the redirections and DNS in a correct state.
    """
)
