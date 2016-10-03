#!/usr/bin/env python

"""
djver.

Usage:
    djver.py [<url>] [--static-path=<static-path>] [--find-diffs] [--verbose]

Options:
    --static-path=<static-path>  URL path to the site's static files [default: /static/].
    --find-diffs                 Attempt to find differences between the known versions of Django
    --verbose                    Turn on verbose logging
"""

import os
import sys
import subprocess
import shutil

import difflib
import requests

from docopt import docopt

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin


RESPONSE_CACHE = {}

THIRD_PARTY_CSS = [
    # Third party apps, might disguise version numbers
    ('django-flat-theme, or Django 1.9', 'fonts.css', 'Roboto'),
    ('django-suit', 'forms.css', 'Django Suit'),
]

ADMIN_CHANGES = [
    ('1.10.2-1.10', 'base.css', 'color: #000;'),
    ('1.9.10-1.9', 'widgets.css', 'margin-left: 7px;'),
    ('1.8.15-1.8.2', 'forms.css', 'clear: left;'),
    ('1.8.1', 'widgets.css', '.related-widget-wrapper {'),
    ('1.8', 'widgets.css', 'opacity: 1;'),
    ('1.7.9-1.7', 'base.css', '#branding a:hover {'),
    ('1.6.11-1.6', 'widgets.css', 'width: 360px;'),
    ('1.5.12-1.5', 'widgets.css', '.url a {'),
    ('1.4.21-1.4.1', 'widgets.css', '.inline-group .aligned .selector .selector-filter label {'),
    ('1.4', 'widgets.css', 'background: #e1e1e1 url(../img/nav-bg.gif) top left repeat-x;'),
]


def check_str(url, search_str, verbose=False):
    if url in RESPONSE_CACHE.keys():
        content = RESPONSE_CACHE[url]
        status_code = 200
    else:
        response = requests.get(url)
        content = response.content.decode().replace(' ', '')
        status_code = response.status_code

    if verbose:
        print('[{}] {}'.format(status_code, url))

    if status_code == 200:
        RESPONSE_CACHE[url] = content
        return search_str.replace(' ', '') in content


def check_version(base_url, static_path, verbose=False):
    if not base_url.startswith('http'):
        base_url = 'http://{}'.format(base_url)

    for version, path, string in ADMIN_CHANGES:
        url = '{}{}admin/css/{}'.format(base_url, static_path, path)
        if check_str(url, string, verbose):
            return version


def find_diffs():
    versions = [
        '1.10.2', '1.10.1', '1.10',
        '1.9.10', '1.9.9', '1.9.8', '1.9.7', '1.9.6', '1.9.5', '1.9.4', '1.9.3', '1.9.2', '1.9.1', '1.9',
        '1.8.15', '1.8.14', '1.8.13', '1.8.12', '1.8.11', '1.8.10', '1.8.9', '1.8.8', '1.8.7', '1.8.6', '1.8.5', '1.8.4', '1.8.3', '1.8.2', '1.8.1', '1.8',
        '1.7.9', '1.7.8', '1.7.7', '1.7.6', '1.7.5', '1.7.4', '1.7.3', '1.7.2', '1.7.1', '1.7',
        '1.6.11', '1.6.10', '1.6.9', '1.6.8', '1.6.7', '1.6.6', '1.6.5', '1.6.4', '1.6.3', '1.6.2', '1.6.1', '1.6',
        '1.5.12', '1.5.11', '1.5.10', '1.5.9', '1.5.8', '1.5.7', '1.5.6', '1.5.5', '1.5.4', '1.5.3', '1.5.2', '1.5.1', '1.5',
        '1.4.21', '1.4.20', '1.4.19', '1.4.18', '1.4.17', '1.4.16', '1.4.15', '1.4.14', '1.4.13', '1.4.12', '1.4.11', '1.4.10',
        '1.4.9', '1.4.8', '1.4.7', '1.4.6', '1.4.5', '1.4.4', '1.4.3', '1.4.2', '1.4.1', '1.4',
        '1.3.7', '1.3.6', '1.3.5', '1.3.4', '1.3.3', '1.3.2', '1.3.1', '1.3',
        ]

    # favour files _not_ found in django-flat-theme
    files = [
        # admin js
        # "js/SelectBox.js",
        # "js/actions.js",
        # "js/actions.min.js",
        # "js/calendar.js",
        # "js/collapse.js",
        # "js/collapse.min.js",
        # "js/core.js",
        # "js/inlines.js",
        # "js/inlines.min.js",
        # "js/jquery.init.js",
        # "js/prepopulate.js",
        # "js/prepopulate.min.js",
        # "js/timeparse.js",
        # "js/urlify.js",

        # admin css
        'css/dashboard.css', 'css/widgets.css', 'css/base.css', 'css/forms.css', 'css/login.css', 'css/dashboard.css',
        # 'css/ie.css',  # removed in 1.9.x
    ]

    for v in versions:
        os.makedirs('files/{}/css/'.format(v), exist_ok=True)
        os.makedirs('files/{}/js/'.format(v), exist_ok=True)

        for fn in files:
            full_path = 'files/{}/{}'.format(v, fn)
            if not os.path.exists(full_path):
                url = 'https://raw.githubusercontent.com/django/django/{}/django/contrib/admin/static/admin/{}'.format(v, fn)
                if v.startswith('1.3'):
                    url = 'https://raw.githubusercontent.com/django/django/{}/django/contrib/admin/media/{}'.format(v, fn)
                response = requests.get(url)

                print('[{}] {}'.format(response.status_code, url))
                with open(full_path, 'wb') as f:
                    f.write(response.content)

    matched_versions = []
    for i, v1 in enumerate(versions[:-1]):
        matched_versions.append(v1)
        v2 = versions[i+1]
        new_line = None

        for f in files:
            f1 = open('files/{}/{}'.format(v1, f)).read()
            f2 = open('files/{}/{}'.format(v2, f)).read()

            # compare f2 to f1 so that we see _added_ lines
            diff = difflib.ndiff(f2.splitlines(), f1.splitlines())
            for line in diff:
                if line.startswith('+ ') and '/*' not in line:
                    line = line[2:]

                    # ensure this line is unique within the file
                    if f1.count(line) == 1:
                        # we also want to make sure that it doesn't appear in any _older_ versions
                        for v in versions[i+1:]:
                            f3 = open('files/{}/{}'.format(v, f)).read()
                            if line in f3:
                                break
                        new_line = line

            if new_line:
                if len(matched_versions) > 1:
                    print("('{}', '{}', '{}'),".format('-'.join([matched_versions[0], matched_versions[-1]]), f, new_line.strip()))
                else:
                    print("('{}', '{}', '{}'),".format(matched_versions[0], f, new_line.strip()))
                matched_versions = []
                break


def djver():
    arguments = docopt(__doc__, version='djver 2.0.0')

    if arguments['--find-diffs']:
        find_diffs()
    elif arguments['<url>']:
        version = check_version(arguments['<url>'], arguments['--static-path'], arguments['--verbose'])
        if version:
            print(version)
        else:
            print('Unable to detect version.')


if __name__ == '__main__':
    djver()
