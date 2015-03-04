Through the power of Django's contrib.admin you can use this tool to figure out
(sometimes) what version of Django a site is running.

This will only work if contrib.admin is enabled, you can figure out the site's
STATIC_URL, and access to the admin CSS isn't otherwise restricted.

It's probably not a great idea.


### Usage

    Usage:
        djver.py <url> [--static-path=<static-path>]

    Options:
        --static-path=<static-path>  URL path to the site's static files [default: /static/].


### Examples

    > ./djver.py commoncode.com.au
    1.6.x

    > ./djver.py djangoproject.com --static-path=/s/
    1.7.x