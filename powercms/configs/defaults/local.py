import os

from django.conf import settings
from google.oauth2 import service_account

ADMINS = (
    ('Bonfim', 'bonfim1999@gmail.com'),
)
DEBUG = True
LOCAL = True
ALLOWED_HOSTS = ['']
SITE_HOST = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'jubarte_educativa',
#         'USER': 'root',
#         'PASSWORD':'123',
#         'HOST': '',
#         'PORT': '',
#     }
# }

TIME_ZONE = 'America/Sao_Paulo'

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error', ]
NOCAPTCHA = True
RECAPTCHA_USE_SSL = True

# PROJETO
CRISPY_TEMPLATE_PACK = 'bootstrap4'
SITE_NAME = 'Jubarte Educativa'
LOGOUT_REDIRECT_URL = '/login'

# django-admin-tools
ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_UPLOAD_PREFIX = settings.MEDIA_URL + 'uploads/'
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
                    'Maximize', 'ShowBlocks'
                ]
            },
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Iframe']},
        ],
        'contentsCss': [
            os.path.join(settings.STATIC_URL, 'ckeditor_config/content.css'),
        ],
        'stylesSet': 'my_styles:%s' % os.path.join(settings.STATIC_URL, 'ckeditor_config/styles.js'),
    },
}

# google-storage
DEFAULT_FILE_STORAGE = 'lms._google.CustomGoogleCloudStorage'

# pasta no bucket onde vão ficar os videos
BUCKET_VIDEOS = 'videos_google'
# pasta no bucket onde vão ficar os demais arquivos upados
BUCKET_OUTROS = 'recurso_google'
DIR_MEDIA = 'media'
DIR_STATIC = 'static'

# colocar o path do arquivo ".json" arquivo baixado no item 2.1 do topico Google Storage da documentação da infraestrutura
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    ""
)

# Youtube API para gerar a o arquivo oauth2

CLIENT_SECRETS_FILE = ''  # colocar path do arquivo .json baixado na sessão YOUTUBE da documentação da infra estrutura
CLIENT_SECRETS_FILE_UPDATE = CLIENT_SECRETS_FILE

REDIRECT_URI_OAUTH2 = 'http://localhost:8000/youtube'
REDIRECT_URI_OAUTH2_UPDATE = 'http://localhost:8000/youtube/update'
URL_FUNCTION_MANUAL = 'https://us-central1-educajubarte.cloudfunctions.net/teste'
VERSION = '1.0'
