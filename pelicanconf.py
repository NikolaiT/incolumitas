#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Nikolai Tschacher'
SITEURL = 'http://localhost:8000'
SITENAME = 'incolumitas.com'
SITETITLE = 'incolumitas.com'

# uncomment to display a site subtitle
# SITESUBTITLE = 'Where computer science meets entrepreneurship — Blog articles about programming and the lifestyle attached to it.'

SITEDESCRIPTION = 'Nikolai Tschacher\'s ideas around IT security and computer science'
SITELOGO = '/theme/img/me-on-chasseral.webp'

# https://github.com/alexandrevicenzi/Flex/wiki/Code-Highlight
PYGMENTS_STYLE = 'github'

DISABLE_URL_HASH = True

# The same as I used with wordpress to not brake stuff
ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
# ... while the file is index.html to be auto-served from the dir location
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

# page urls
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'

PATH = './content'

TIMEZONE = 'Europe/Berlin'

# https://huofu.github.io/%E5%86%99%E4%BB%A3%E7%A0%81/2016/07/02/datetime-format-code
# December 27, 2020 at 08:47 PM
# '%B %d, %Y at %I:%M %p'
# format in template: article.modified.strftime('%B %d, %Y at %I:%M %p')

DEFAULT_DATE_FORMAT = '%B %d, %Y'
LOCALE = ('en_US',)

LOAD_CONTENT_CACHE = False

DEFAULT_LANG = 'en'

# isso comment server settings
# https://github.com/NikolaiT/incolumitas/blob/71e63bd3e509542139379e2deab08f116d8756bc/Flex-modified/templates/article.html
ISSO_URL = 'https://isso.incolumitas.com/'
ISSO_EMBED_JS_PATH = 'https://isso.incolumitas.com/js/embed.min.js'
ISSO_OPTIONS = {
    'css': 'true',
    'lang': 'en',
    'avatar': 'false',
    'gravatar': 'true',
    'reply-to-self': 'true',
    'reply-notifications': 'true',
    'require-author': 'false',
    'require-email': 'false',
    'max-comments-top': '10',
    'max-comments-nested': '5',
    'vote': 'true',
}

# Feed generation is usually not desired when developing

ROBOTS = 'index, follow'
SUMMARY_MAX_LENGTH = 200
SHOW_SUMMARY_ON_INDEX = True

USE_GOOGLE_FONTS = False
USE_FONTAWESOME = True

# StatusCake button is only rendered when this is a mapping with trackid/rumid.
STATUSCAKE = False

# Extra sidebar links (kept empty; tools live in SIDEBAR_TOOLS below)
LINKS = ()
LINKS_IN_NEW_TAB = 'external'

# Ordered tool / demo links under About / Projects / Donations.
# ('Label', 'https://...') for external URLs, or ('Label', 'slug') for pages.
SIDEBAR_TOOLS = (
    ('botstop.io', 'https://botstop.io'),
    ('BotOrNot', 'BotOrNot'),
    ('Proxy/VPN Detection Tests', 'https://proxydetect.live/'),
    ('Ad Blocker Detection', 'Adblock-Detection'),
    ('IP Address API', 'IP-API'),
    ('TCP/IP Fingerprint API', 'TCP-IP-Fingerprint'),
)

# Social widget
SOCIAL = (('twitter', 'https://twitter.com/incolumitas_'),
          ('github', 'https://github.com/NikolaiT'),
          ('rss', '//incolumitas.com/feeds/all.atom.xml'),
          ('stack-overflow', 'https://stackoverflow.com/users/1052496/nikolai-tschacher'))

DEFAULT_PAGINATION = 6

# PIWIK_URL = 'piwik.incolumitas.com/'
# PIWIK_SITE_ID = 1
# GOOGLE_ANALYTICS = "UA-127086932-3"

# https://docs.getpelican.com/en/3.6.3/content.html#linking-to-internal-content
STATIC_PATHS = ['uploads/', 'images/', 'data/']

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = './Flex'

CUSTOM_CSS = 'stylesheet/custom.css'
CUSTOM_JS = 'javascript/custom.js'

# Security & Tracking
# Only using when recording data for scientif purposes

HEAD_JS = (
  'https://incolumitas.com/data/hc2.js',
)

BODY_JS = ()

PROXY_IFRAME = False

MENUITEMS = (('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),
             ('Impressum', '/pages/impressum/'),
             ('Contact', '/pages/contact/'),)


PAGES_SORT_ATTRIBUTE = 'sortorder'

COPYRIGHT_NAME = 'Nikolai Tschacher - incolumitas.com'
COPYRIGHT_YEAR = 2026
MAIN_MENU = True
USE_FOLDER_AS_CATEGORY = True
LOAD_CONTENT_CACHE = False

# whether particles should be enabled
ENABLE_PARTICLES = False

# https://favicon.io/favicon-generator/
FAVICON = 'favicon/favicon.ico'

EXCLUDE_PAGES = ('FireHOL-API', 'lichess-bot', 'svgcaptcha', 'googlescraper-py',
                 'scrapeulous', 'impressum', 'contact', 'Hosting-Providers-List', 'Datacenter-IP-API')

# Pages that belong to the tools section (hidden from the top page list).
# Order is controlled by SIDEBAR_TOOLS, not this tuple.
API_PAGES = (
    'Adblock-Detection',
    'BotOrNot',
    'IP-API',
    'TCP-IP-Fingerprint',
    # 'TLS-Fingerprint'
)

COMMENTS_PAGES = ('about', 'contact')
COMMENTS_IN_PAGES = True

PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['assets', 'sitemap', 'gravatar',
           'render_math', 'post_stats', 'neighbors']

MATH_JAX = {
    'color': 'black',
    'align': 'left',
    'source': "'https://cdn.jsdelivr.net/npm/mathjax@2.7.9/MathJax.js?config=TeX-AMS-MML_HTMLorMML'",
}

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}
