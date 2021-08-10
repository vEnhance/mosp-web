"""
Django settings for mospweb project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / '.env'
if ENV_PATH.exists():
	load_dotenv(ENV_PATH)

PRODUCTION = bool(os.getenv('IS_PRODUCTION'))
if not PRODUCTION:
	INTERNAL_IPS = ('127.0.0.1',)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not PRODUCTION

if PRODUCTION:
	ALLOWED_HOSTS = ['mosp.evanchen.cc']
else:
	ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition

CRISPY_TEMPLATE_PACK = 'bootstrap4'
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.humanize',
	'django.contrib.messages',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.staticfiles',
	'allauth',
	'allauth.account',
	'allauth.socialaccount',
	'allauth.socialaccount.providers.discord',
	'markdownx',
	'tailwind',
	'crispy_forms',
	'crispy_tailwind',
	'theme',
	'core',
	'info',
	'typescripts',
	'data2021',
	'mospweb',
]
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACKE = "tailwind"
MARKDOWNX_MARKDOWN_EXTENSIONS = [
	'markdown.extensions.extra',
	'markdown.extensions.sane_lists',
	'markdown.extensions.smarty',
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

ROOT_URLCONF = 'mospweb.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'info.context_processors.pages',
			],
		},
	},
]

WSGI_APPLICATION = 'mospweb.wsgi.application'

#LOGGING = {
#	'version': 1,
#	'disable_existing_loggers': False,
#	'handlers': {
#		'file': {
#			'level': 'DEBUG',
#			'class': 'logging.FileHandler',
#			'filename': 'sql.log',
#		},
#	},
#	'loggers': {
#		'django.db.backends': {
#			'handlers': ['file'],
#			'level': 'DEBUG',
#			'propagate': True,
#		},
#	},
#}

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


if os.getenv("DATABASE_NAME"):
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'NAME': os.getenv("DATABASE_NAME"),
			'USER': os.getenv("DATABASE_USER"),
			'PASSWORD': os.getenv("DATABASE_PASSWORD"),
			'HOST': os.getenv("DATABASE_HOST"),
			'PORT': os.getenv("DATABASE_PORT", '3306'),
			'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", 'charset': 'utf8mb4'},
		},
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': BASE_DIR / 'db.sqlite3',
		}
	}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
AUTHENTICATION_BACKENDS = [
		'django.contrib.auth.backends.ModelBackend',
		'allauth.account.auth_backends.AuthenticationBackend',
		]
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_PRESERVE_USERNAME_CASING = False
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
if PRODUCTION:
	ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

TAILWIND_APP_NAME = 'theme'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'static'

if PRODUCTION:
	STATIC_URL = os.getenv("STATIC_URL")
	assert STATIC_URL is not None
	SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
	assert SECRET_KEY is not None
else:
	STATIC_URL = '/static/'
	MEDIA_URL = '/media/'
	SECRET_KEY = 'evan_chen_is_really_cool'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# fking windows
import platform
if platform.system() == 'Windows':
	NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd" # only for serena
	print("FUCK WINDOWS!!!")
