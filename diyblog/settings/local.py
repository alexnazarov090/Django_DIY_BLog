from diyblog.settings.base import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import os
import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))

SECRET_KEY = env("SECRET_KEY", default='(mrj9-6@iwob-cys($@@e#)%-_&f$$@0hu3bg3)vld%zxoe1e-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(env("DEBUG", default=1))
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(" ")

# AWS S3 SETTINGS
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_URL = env('AWS_URL')
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_SIGNATURE_VERSION = 's3v4'

# Application definition

INSTALLED_APPS += [
    'imagekit',
    'crispy_forms',
    'crispy_bootstrap5',
    'anymail',
    'storages',
    # My Apps
    'blog.apps.BlogConfig',
    'users.apps.UsersConfig',
]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        "USER": env("SQL_USER", default="user"),
        "PASSWORD": env("SQL_PASSWORD", default="password"),
        "HOST": env("SQL_HOST", default="localhost"),
        "PORT": env("SQL_PORT", default="5432"),
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.joinpath('media')

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = False
SECURE_SSL_REDIRECT = False

EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"
ANYMAIL = {
    "SENDINBLUE_API_KEY": env("SENDINBLUE_API_KEY", default="api_key"),
    "SENDINBLUE_API_URL": "https://api.sendinblue.com/v3/",
}

DEFAULT_FROM_EMAIL = "homecorp@gmail.com"
SERVER_EMAIL = env("SERVER_EMAIL", default="homecorp@gmail.com"),

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'general.log',
            'formatter': 'simple'
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'blog': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

if DEBUG:
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['file']