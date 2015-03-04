#!/usr/bin/env python

"""
djver.

Usage:
    djver.py <url> [--static-path=<static-path>]

Options:
    --static-path=<static-path>  URL path to the site's static files [default: /static/].

"""

import sys
import requests

from docopt import docopt
from urlparse import urljoin


def check_str(url, search_str):
    response = requests.get(url)

    if response.status_code == 200:
        return search_str in response.content
    print '[{}] {}'.format(response.status_code, url)


def check_14(base_url, static_path='/static/'):
    url = urljoin(base_url, '{}admin/css/base.css'.format(static_path))
    return check_str(url, 'background: white url(../img/nav-bg-reverse.gif) 0 -5px repeat-x;')


def check_15(base_url, static_path='/static/'):
    url = urljoin(base_url, '{}admin/css/widgets.css'.format(static_path))
    return check_str(url, '.inline-group .aligned .selector .selector-filter label {')


def check_16(base_url, static_path='/static/'):
    url = urljoin(base_url, '{}admin/css/base.css'.format(static_path))
    return check_str(url, 'input[type=text], input[type=password], input[type=email], input[type=url], input[type=number],')


def check_17(base_url, static_path='/static/'):
    url = urljoin(base_url, '{}admin/css/base.css'.format(static_path))
    return check_str(url, '#branding {')


def check_18(base_url, static_path='/static/'):
    url = urljoin(base_url, '{}admin/css/base.css'.format(static_path))
    return check_str(url, 'input, textarea, select, .form-row p, form .button {')


def check_version(base_url, static_path):
    if not base_url.startswith('http'):
        base_url = 'http://{}'.format(base_url)

    check_functions = [
        ('1.8.x', check_18),
        ('1.7.x', check_17),
        ('1.6.x', check_16),
        ('1.5.x', check_15),
        ('1.4.x', check_14),
    ]

    for ver, func in check_functions:
        if func(base_url, static_path):
            print ver
            sys.exit()

    print 'Unable to detect version of {}'.format(base_url)


def djver():
    arguments = docopt(__doc__, version='djver 1.0')
    check_version(arguments['<url>'], arguments['--static-path'])

if __name__ == '__main__':
    djver()
