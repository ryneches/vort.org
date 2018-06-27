#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Russell Neches'
SITENAME = u'Refracting the light of evolution'
SITEURL = 'https://vort.org'

PATH = 'content'
STATIC_PATHS = [ 'figures' ]
IGNORE_FILES = ['.ipynb_checkpoints']

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# markup
MARKUP = ('md', 'ipynb')

# plugins
PLUGIN_PATHS = [ '/home/russell/pkg/pelican-plugins',
                 './plugins' ]
PLUGINS = [ 'render_math', 'ipynb.markup', 'i18n_subsites' ]

# themes
THEME = '/home/russell/pkg/pelican-themes/pelican-bootstrap3'

# theme settings
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = True
SHOW_ARTICLE_AUTHOR = True
SHOW_DATE_MODIFIED = True
MENUITEMS = [ 'boop' ]

PYGMENTS_STYLE = 'default'

BOOTSTRAP_THEME = 'lumen'

STATIC_PATHS = [ 'assets' ]

#CUSTOM_CSS = 'static/css/custom.css'
CUSTOM_JS = 'static/js/custom.js'

FAVICON = 'assets/favicon.png'
AVATAR = 'assets/me.jpeg'

# Tell Pelican to change the path to 'static/custom.css' in the output dir
EXTRA_PATH_METADATA = {
    'assets/css/custom.css': {'path': 'static/css/custom.css'},
    'assets/js/custom.js': {'path': 'static/js/custom.js'}
}

DISQUS_SITENAME = 'vort.org'

DISPLAY_ARTICLE_INFO_ON_INDEX = True

# pagination
PAGINATION_PATTERNS = (
        (1, '{base_name}/', '{base_name}/index.html'),
        (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)

TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'
TAGS_URL = 'tags/'
TAGS_SAVE_AS = 'tags/index.html'

AUTHOR_URL = 'author/{slug}/'
AUTHOR_SAVE_AS = 'author/{slug}/index.html'
AUTHORS_URL = 'authors/'
AUTHORS_SAVE_AS = 'authors/index.html'

CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
CATEGORYS_URL = 'categories/'
CATEGORYS_SAVE_AS = 'categories/index.html'

ARCHIVES_URL       = 'archives'
ARCHIVES_SAVE_AS   = 'archives/index.html'

# use those if you want pelican standard pages to appear in your menu
MENU_INTERNAL_PAGES = (
        ('Tags', TAGS_URL, TAGS_SAVE_AS),
        ('Authors', AUTHORS_URL, AUTHORS_SAVE_AS),
#        ('Categories', CATEGORYS_URL, CATEGORYS_SAVE_AS),
        ('Archives', ARCHIVES_URL, ARCHIVES_SAVE_AS),
)

# additional menu items
MENUITEMS = (
        ('GitHub', 'https://github.com/ryneches'),
        ('Twitter', 'https://twitter.com/ryneches'),
)

# Social widget
SOCIAL = (('GitHub', 'https://github.com/ryneches'),
          ('Twitter', 'https://twitter.com/ryneches'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

# uikit theme stuff
# control the sidebar-tags/links with a simple setting.
# If the value
# is 0, all links will be displayed
# is negative, no links will be displayed
# is positive, that many links will be displayed

DISPLAY_TAGS_ON_SIDEBAR_LIMIT = 0
DISPLAY_LINKS_ON_SIDEBAR_LIMIT = 0

# available licenses (see LICENSE['cc_name']):
# licenses in version 4.0
# by-nc
# by-nc-nd
# by-nc-sa
# by-nd
# by-nd-nc
# by-sa
# all icons are included locally,
# however you can use the icon hosted by
# <https://licensebuttons.net/>.
# compact (80x15) or normal (88x31) icon
LICENSE = {
    'cc_name':"by-sa",
    'hosted':False,
    'compact':True,
    'brief':False
    }
