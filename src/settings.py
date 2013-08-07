# Django settings for storyscape project.

import os

filepath = os.path.dirname(os.path.realpath(__file__))


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# TODO: we're pretty lax on security here. so here's the db password!
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'storyscape',
        'USER': 'storyscape',
        'PASSWORD': 'fs$WY@$UHwrg0h34t',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

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
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/var/www/storyscape/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/var/www/storyscape/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(filepath, "..", "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+wqm2_n%=mm8sj4=mt2o*etgea%#qx$-i@)+^n4(0wtk&vwvnn'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if (DEBUG):
    MIDDLEWARE_CLASSES = ('middleware.ProcessExceptionMiddleware',) + MIDDLEWARE_CLASSES

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(filepath, "..", "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.core.context_processors.request',
  "django.core.context_processors.media",
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.static',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'tagging',
    'medialibrary',
    'storyscape',
    'registration',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': "/var/log/storyscape/storyscape.log",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'ERROR',
        },
        'django.db.backends': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        '': {
            'handlers': ['logfile'],
            'level': 'WARN',
        },
    }
}

# CUSTOM STORYSCAPE VARIABLES

MEDIAOBJECT_UPLOAD_URL_ROOT_DIR_NAME = 'sodiioo-mo'
SODIIOO_SITE_URL = 'http://storyscape.media.mit.edu'
STORYSCAPE_STORIES_URL_ROOT = 'storyscape_media/stories/'
STORYSCAPE_IMAGE_URL_ROOT = '/var/www/storyscape/media/storyscape_media/stories/'
MEDIALIBRARY_URL_ROOT = '/var/www/storyscape/media/'


# REGISTRATION VARIABLES

ACCOUNT_ACTIVATION_DAYS = 3
PASSWORD_RESET_TIMEOUT_DAYS = ACCOUNT_ACTIVATION_DAYS
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'atabi.sodiioo@gmail.com'
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FORM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'Agpass4G'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
LOGIN_REDIRECT_URL = '/'

# DJANGO TAGGING

FORCE_LOWERCASE_TAGS = True
MAX_TAG_LENGTH = 20
