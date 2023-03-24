from pathlib import Path
import os
import dj_database_url
import dotenv
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")

if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

SECRET_KEY = 'django-insecure-d2(k_+e4qei&y8u=uvoal-*95k!r+tc)0vn-o=ivp@imtfxd-8'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'study-buddy-ik.herokuapp.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'StudyBuddy',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'bootstrap5',
    'crispy_forms'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd90haccgh37lft',
        'USER': 'xlfziwxddggaqr',
        'PASSWORD': '9844b6024f0d089b08a184214bea2f1a901b167eaeae7ca68a58a6488838abde',
        'HOST': 'ec2-34-231-42-166.compute-1.amazonaws.com',
        'PORT':  ''
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase'
    }

# Password validation
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


# Social Account Signup
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_FORMS = {
    'signup': 'StudyBuddy.forms.CustomSignupForm',
}


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'EST'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

SITE_ID = 2

LOGIN_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


try:
    if 'HEROKU' in os.environ:
        import django_heroku
        django_heroku.settings(locals())
except ImportError:
    found = False


options = DATABASES['default'].get('OPTIONS', {})
options.pop('sslmode', None)
