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

try:
    from packaging.version import parse
except:
    def parse(version):
        return None


RESPONSE_CACHE = {}

THIRD_PARTY_CSS = [
    # Third party apps, might disguise version numbers
    ('django-flat-theme, or Django 1.9', 'fonts.css', 'Roboto'),
    ('django-suit', 'forms.css', 'Django Suit'),
]

ADMIN_CHANGES = [
    ('2.1.2-2.1', 'css/base.css', 'background: url(../img/icon-viewlink.svg) 0 1px no-repeat;'),
    ('2.0.9-2.0', 'css/base.css', 'textarea:focus, select:focus, .vTextField:focus {'),
    ('1.11.16-1.11', 'css/base.css', 'background-position: right 7px center;'),
    ('1.10.8-1.10', 'css/base.css', 'color: #000;'),
    ('1.9.13-1.9', 'css/widgets.css', 'margin-left: 7px;'),
    ('1.8.19-1.8.2', 'css/forms.css', 'clear: left;'),
    ('1.8.1', 'css/widgets.css', '.related-widget-wrapper {'),
    ('1.8', 'css/widgets.css', 'opacity: 1;'),
    ('1.7.11-1.7', 'css/base.css', '#branding a:hover {'),
    ('1.6.11-1.6', 'css/widgets.css', 'width: 360px;'),
    ('1.5.12-1.5', 'css/widgets.css', '.url a {'),
    ('1.4.22-1.4.1', 'css/widgets.css', '.inline-group .aligned .selector .selector-filter label {'),
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
        url = '{}{}admin/{}'.format(base_url, static_path, path)
        if check_str(url, string, verbose):
            return version


def find_diffs():
    response = requests.get('https://pypi.org/pypi/Django/json')
    versions = [parse(v) for v in response.json()['releases'].keys()]
    versions = sorted(versions, reverse=True)

    print(versions)
    versions = [str(v) for v in versions if v.is_prerelease == False and v > parse("1.3.99")]

    # we only care about 1.4 and above

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
        'css/widgets.css', 'css/base.css', 'css/forms.css', 'css/login.css', 'css/dashboard.css',
        # 'css/ie.css',  # removed in 1.9.x
    ]

    for v in versions:
        os.makedirs('files/{}/css/'.format(v), exist_ok=True)
        os.makedirs('files/{}/js/'.format(v), exist_ok=True)

        for fn in files:
            full_path = 'files/{}/{}'.format(v, fn)
            if not os.path.exists(full_path):
                repo = 'https://raw.githubusercontent.com/django/django/'
                url = '{}{}/django/contrib/admin/static/admin/{}'.format(repo, v, fn)
                if v.startswith('1.3'):
                    url = '{}{}/django/contrib/admin/media/{}'.format(repo, v, fn)
                response = requests.get(url)

                print('[{}] {}'.format(response.status_code, url))
                with open(full_path, 'wb') as f:
                    f.write(response.content)

    matched_versions = []
    for i, v1 in enumerate(versions[:-1]):
        matched_versions.append(v1)
        v2 = versions[i + 1]
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
                        for v in versions[i + 1:]:
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
