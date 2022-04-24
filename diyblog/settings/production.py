from diyblog.settings.base import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import os
import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.prod'))

SECRET_KEY = env("SECRET_KEY", default='(mrj9-6@iwob-cys($@@e#)%-_&f$$@0hu3bg3)vld%zxoe1e-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(env("DEBUG", default=0))
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS += [
    'imagekit',
    'crispy_forms',
    'crispy_bootstrap5',
    'anymail',
    # My Apps
    'blog.apps.BlogConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE += [
    'WhiteNoiseMiddleware',
    ]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': env("SQL_ENGINE", default='django.db.backends.postgresql'),
#         'NAME': env("SQL_DATABASE", default='diy_blog_prod'),
#         "USER": env("SQL_USER", default="user"),
#         "PASSWORD": env("SQL_PASSWORD", default="password"),
#         "HOST": env("SQL_HOST", default="localhost"),
#         "PORT": env("SQL_PORT", default="5432"),
#     }
# }

# Heroku: Update database configuration from $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

SESSION_COOKIE_SECURE = True
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
