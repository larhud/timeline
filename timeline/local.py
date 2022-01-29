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
RECAPTCHA_PRIVATE_KEY = '6LdpQvwbAAAAAGjmJ5BfZcgzLmPiV4nOeJpw9DQ1'

SITE_NAME = 'Timeline LARHUD'

DATABASES = {
            'default': {
                        'ENGINE': 'django.db.backends.mysql',
                        'NAME': 'timeline',
                        'USER': 'timeline',
                        'PASSWORD': 'logica33',
                        'OPTIONS': { 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", },
                        }
            }

