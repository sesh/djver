Through the power of Django's contrib.admin you can use this tool to figure out
(with a low level of reliability) what version of Django a site is running.

This will only work if contrib.admin is enabled, you can figure out the site's
STATIC_URL, and access to the admin CSS isn't otherwise restricted.

It's probably not a great idea. Just a proof of concept.


### Installation

    pip install git+https://github.com/sesh/djver

_Note: right now this is only really tested with Python 3.5_


### Usage

    Usage:
        djver <url> [--static-path=<static-path>]

    Options:
        --static-path=<static-path>  URL path to the site's static files [default: /static/].


### Examples

    > ./djver.py commoncode.com.au
    1.9.10-1.9

    > ./djver.py djangoproject.com --static-path=/s/
    1.9.10-1.9
