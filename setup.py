#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for redsys client.
"""

import os
from setuptools import setup, find_packages

PACKAGES = ['redsys', ]
PACKAGES_DATA = {'redsys.tests': []}

setup(name='redsys',
    description='A client to submit payment orders to the Redsys service.',
    author='Zikzakmedia SL',
    author_email='zikzak@zikzakmedia.com',
    url='http://www.zikzakmedia.com',
    download_url="https://github.com/nanticzz/python-redsys",
    version='0.2.5',
    license='General Public Licence 2',
    provides=['redsys'],
    install_requires=[
        'pycrypto',
        ],
    packages=PACKAGES,
    package_data=PACKAGES_DATA,
    scripts=[],
    test_suite='redsys.tests',
)
