from diyblog.settings.base import *
import os
import environ


# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.prod'))

SECRET_KEY = env("SECRET_KEY", default='(mrj9-6@iwob-cys($@@e#)%-_&f$$@0hu3bg3)vld%zxoe1e-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(env("DEBUG", default=0))
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(" ")

# AWS S3 SETTINGS
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_URL = env('AWS_URL')
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'


# MIDDLEWARE += [
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     ]


# Database

DATABASES = {
    'default': {
        'ENGINE': env("SQL_ENGINE", default='django.db.backends.postgresql'),
        # 'NAME': env("DBNAME", default='diy_blog_prod'),
        # "USER": env("DBUSER", default="user"),
        # "PASSWORD": env("DBPASS", default="password"),
        # "HOST": env("DBHOST", default="localhost"),
        # # "PORT": env("APP_PORT", default="5432"),
    }
}


import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
DATABASES = {'default': dj_database_url.config(default=env("DB_CONNECTION_STRING", default='postgres://...'))}

# # Simplified static file serving.
# # https://warehouse.python.org/project/whitenoise/
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_ROOT = '/home/c67855/mein-django-diy-blog.na4u.ru/www/static'
STATICFILES_DIRS = [
    BASE_DIR / "nltk_data",
]


MEDIA_URL = AWS_URL + '/media/'
DEFAULT_FILE_STORAGE = 'blog.storages.CustomS3Boto3Storage'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 600
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True

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
            'formatter': 'verbose'
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