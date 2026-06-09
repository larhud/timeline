# -*- coding: utf-8 -*-
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.insert(0, PROJECT_DIR)

VERSION = 'v1.5'

LOCAL = True
DEBUG = True

SITE_NAME = 'Default'
SITE_HOST = 'http://127.0.0.1:8000'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
ADMIN_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'admin')

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'utils.ThreadLocal.ThreadLocalMiddleware',
    # 'cms.middleware.URLMigrateFallbackMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
]

LOGIN_URL = '/admin/'

ROOT_URLCONF = 'powercms.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'powercms.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Estrutura de arquivos obrigatórios para um tema
TEMA_STRUCTURE = (
    # 'templatetags',  # os.path.join('templatetags', '__init__.py'),
    '__init__.py', 'static', 'urls.py', 'readme.md',
    'templates',
    os.path.join('templates', 'home.html'),
    os.path.join('templates', 'article.html'),
    os.path.join('templates', 'section.html'),
    os.path.join('templates', 'search.html')
)
#
OPTIONAL = ['views.py', os.path.join('templates', '__init__.py')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(PROJECT_DIR, os.path.join('theme', 'templates')),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'admin_tools.template_loaders.Loader',
            ]
        },
    },
]

INSTALLED_APPS = [
    'powercms.dj_tppc',
    'powercms.filebrowser',
    'poweradmin',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_mptt_admin',
    'django.contrib.admin',
    # CMS
    'powercms.cms',
    'powercms.crm',
    'powercms.utils',
    'captcha',
    'ckeditor',
    'ckeditor_uploader',
    'mptt',
    'easy_thumbnails',
    'smart_selects',
    'compressor',
    'django.contrib.sitemaps',
    'powercms.imagestore',
    'sorl.thumbnail',
    'tagging',
    'crispy_forms',
]

if os.path.isdir(os.path.join(PROJECT_DIR, 'theme')):
    INSTALLED_APPS += [
        'theme',
    ]

# A list of directories where Django looks for translation files
LOCALE_PATHS = [
    os.path.join(PROJECT_DIR, 'dj_tppc', 'translation', 'imagestore', 'locale'),
]

IMAGESTORE_SHOW_USER = False
IMAGESTORE_UPLOAD_TO = 'uploads/gallery/'

COMPRESS_CSS_FILTERS = [
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_OUTPUT_DIR = 'site'
COMPRESS_ENABLED = True

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            {
                'name': 'document',
                'items': [
                    'Source', '-', 'Preview'
                ]
            },
            {
                'name': 'basicstyles',
                'groups': [
                    'basicstyles', 'cleanup'
                ],
                'items': [
                    'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'
                ]
            },
            {
                'name': 'paragraph', 'groups': ['list', 'indent', 'blocks', 'align'],
                'items': [
                    'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
                    'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter',
                    'JustifyRight', 'JustifyBlock'
                ]
            },
            '/',
            {
                'name': 'styles',
                'items': [
                    'Styles', 'Format'
                ]
            },
            {
                'name': 'colors',
                'items': [
                    'TextColor', 'BGColor'
                ]
            },
            {
                'name': 'tools',
                'items': [
                    'Maximize', 'ShowBlocks', 'FontSize'
                ]
            },
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Iframe']},
        ],
        'contentsCss': [
            os.path.join(STATIC_URL, 'ckeditor_config/content.css'),
            os.path.join(STATIC_URL, 'public/css/ckeditor_configs.css') if os.path.exists(os.path.join(STATIC_ROOT,  'public/css/ckeditor_configs.css')) else '',
        ],
        'stylesSet': 'my_styles:%s' % os.path.join(STATIC_URL, 'ckeditor_config/styles.js'),
        'stylesSet': 'my_styles2:%s' % os.path.join(STATIC_URL, 'public/js/ckeditor_configs.js') if os.path.exists(os.path.join(STATIC_ROOT, 'public/js/ckeditor_configs.js')) else '',
    },
}

LOGIN_REDIRECT_URL = '/admin/'

DEFAULT_FILE_STORAGE = 'utils.storage.SpecialCharFileSystemStorage'

# Configurations of the tools
ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'

EMAIL_BACKEND = 'utils.email.CustomEmailBackend'
