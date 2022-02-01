"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import environ
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Initialise environment variables
root = environ.Path(__file__) - 3  # get root of the project
env = environ.Env()
environ.Env.read_env()
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# PROD
DEBUG = True
ALLOWED_HOSTS = ["laec-prod-test.ey.r.appspot.com",'127.0.0.1','*',env('PROD_HOST')]
ELASTICSEARCH_HOST = env('ELASTICSEARCH_HOST')
ELASTICSEARCH_PORT = env('ELASTICSEARCH_PORT')
PROD_HOST = env('PROD_HOST')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'haystack',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,  '/core/templates/')],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD':  env('DATABASE_PASS'),
        'HOST': env('DATABASE_HOST'),   # Or an IP Address that your DB is hosted on
        'PORT': env('DATABASE_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

#HAYSTACK
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'core.search_backends.CustomElasticSearchEngine',
        'URL': 'http://'+ELASTICSEARCH_HOST+':'+ELASTICSEARCH_PORT+'/',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'INDEX_NAME': 'haystack',
    },
}

#ELASTICSEARCH
ELASTICSEARCH_DSL={
    'default': {
        'hosts': ELASTICSEARCH_HOST+':'+ELASTICSEARCH_PORT
    },
}
ELASTICSEARCH_INDEX_SETTINGS   = {
    'mappings' : {
      "modelresult" : {
        "properties" : {
          "content" : {
            "type" : "text",
            "analyzer" : "snowball"
          },
          "content_auto" : {
            "type" : "text",
            "analyzer" : "edgengram_analyzer"
          },

          "title" : {
            "type" : "text",
            "analyzer" : "snowball"
          },
          "title_auto" : {
            "type" : "text",
            "analyzer" : "edgengram_analyzer"
          }
        }
      }
    },
  'settings': {
                "analysis": {
                    "analyzer": {
                        "ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "lowercase",
                            "filter": ["haystack_ngram"]
                        },
                        "edgengram_analyzer": {
                            "type": "custom",
                            "tokenizer": "lowercase",
                            "filter": ["haystack_edgengram"]
                        }
                    },
                    "tokenizer": {
                        "haystack_ngram_tokenizer": {
                            "type": "nGram",
                            "min_gram": 3,
                            "max_gram": 15,
                        },
                        "haystack_edgengram_tokenizer": {
                            "type": "edgeNGram",
                            "min_gram": 3,
                            "max_gram": 15,
                            "side": "front"
                        }
                    },
                    "filter": {
                        "haystack_ngram": {
                            "type": "nGram",
                            "min_gram": 3,
                            "max_gram": 15,
                        },
                        "haystack_edgengram": {
                            "type": "edgeNGram",
                            "min_gram": 3,
                            "max_gram": 15,
                        }
                    }
                }
            }

 }
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'

ELASTICSEARCH_DEFAULT_ANALYZER = "snowball"
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = "static"
STATIC_URL = "/static/"
STATICFILES_DIRS = []
SECURE_SSL_REDIRECT = False

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[DJANGO] %(levelname)s %(asctime)s %(module)s '
                          '%(name)s.%(funcName)s:%(lineno)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            }
        },
        'loggers': {
            '*': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            }
        },
    }
