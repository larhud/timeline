from .settings import *

DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = '%^e0+lt5@3^o2nmiz^s-bkwqhp*^35yfk8%qsi8@s5)(i7r&g6'

LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = False

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error', ]
NOCAPTCHA = True
RECAPTCHA_USE_SSL = True

RECAPTCHA_DOMAIN = 'www.recaptcha.net'
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

SITE_NAME = 'Timeline LARHUD'
