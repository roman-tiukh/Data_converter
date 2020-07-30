import os
# sentry import configarution
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '89di$5_t-fo8f*z0!kvbli20gcz^6f)8&2!e1g3o4pbe7v(h^q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SITE URLS
# For development mode
FRONTEND_SITE_URL = 'http://localhost:3000'
BACKEND_SITE_URL = 'http://localhost:8000'
# For production mode
# FRONTEND_SITE_URL = 'https://dataocean.us'
# BACKEND_SITE_URL = 'https://ipa.dataocean.us'

# Custom user registration
CANDIDATE_EXPIRE_MINUTES = 5
# Send user_registration/reset_password email by POSTMAN or EMAIL_BACKEND
SEND_MAIL_BY_POSTMAN = False
# AUTHORIZATION TOKEN FOR POSTMAN
POSTMAN_TOKEN = 'e7937e4b5a309177b85fad8715bcbd451fdcb67f91696e1968f8dd188ada70a1'
# URL FOR POSTMAN
POSTMAN_URL = 'https://postman.org.ua/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


ALLOWED_HOSTS = [
    'ipa.dataocean.us',
    'localhost',
    '127.0.0.1',
]



DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "data_oceanv2",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.01",
        "PORT": "5432",
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

# CORS settings
# https://github.com/adamchainz/django-cors-headers

CORS_ORIGIN_WHITELIST = [
    'https://dataocean.us',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
]

CSRF_TRUSTED_ORIGINS = [
    'dataocean.us',
    'localhost',
    '127.0.0.1',
]


LOCAL_FILE_NAME_KOATUU = ''
LOCATION_KOATUU_LOCAL_FILE_NAME = ''
LOCAL_FOLDER = ''
FILE_URL_KVED = ''
LOCAL_FILE_NAME_KVED = ''
LOCAL_FILE_NAME_UO_ADDRESS = ''
LOCAL_FILE_NAME_UO_SIGNER = ''
LOCAL_FILE_NAME_UO_FOUNDER = ''
LOCAL_FILE_NAME_UO_NAME = ''
LOCAL_FILE_NAME_UO_SHORTNAME = ''
LOCAL_FILE_NAME_UO_CAPITAL = ''
LOCAL_FILE_NAME_UO_BRANCH = ''
LOCAL_FILE_NAME_UO_INFO = ''
LOCATION_KOATUU_SOURCE_REGISTER_ID = "dc081fb0-f504-4696-916c-a5b24312ab6e"
LOCATION_RATU_SOURCE_REGISTER_ID = "a2d6c060-e7e6-4471-ac67-42cfa1742a19"
LOCATION_KVED_SOURCE_REGISTER_ID = "e1afb81c-70e4-4009-96a0-b240c36e4603"


CACHES = {
    'default': {
        # REDIS cache configs
        # 'BACKEND': 'django_redis.cache.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
        # 'OPTIONS': {
        #     "IGNORE_EXCEPTIONS": True,
        #     # 'PASSWORD': 'XXXXXXXXX',
        #     'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        # },

        # Dummy Cache for developing
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # use this cashe for developing
    },
}

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# business_register/converter/company.py
UO_CHUNK_SIZE = 100
CHUNK_SIZE_UO = 100

# celery settings
# CELERY_BROKER_URL = 'redis://localhost:6379/2' # redis://:password@hostname:port/db_number
# CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# use CELERY_BEAT_SHEDULE to set periodic tasks in code, without admin aplication/ periodic tasks
# CELERY_BEAT_SCHEDULE = {
#     'fill_in_ratu_table':{
#         'task': 'location_register.tasks.fill_in_ratu_table',
#         'schedule': crontab(hour=14, minute=10, day_of_week=5),
#     },
#     'fill_in_koatuu_table':{
#         'task': 'location_register.tasks.fill_in_koatuu_table',
#         'schedule': crontab(hour=1, minute=10, day_of_week=6),
#     }
# }

# sentry configarution
# sentry_sdk.init(
#     # create your sentry account and add your own dsn <account_dsn>
#     # dsn.example="https://d47c87c1d55f4f30ba48ace8394efb0f@o411563.ingest.sentry.io/5286958"
#     dsn="<account_dsn>",
#     integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
#
#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=False
# )

# RAVEN_CONFIG = {
#     # format 'dsn':'https://<public_key>@sentry.io/<project_id>
#     "dsn":"<account_dsn>" # create your sentry account and add your own dsn
# }

#Settings to enable custome logging
DEBUG_PROPAGATE_EXCEPTIONS = True

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#         }
#     },
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'INFO',
#             'class': 'logging.StreamHandler',
#             'filters': ['require_debug_true'],
#             'formatter': 'verbose',
#         },
#         'production_logfile': {
#             'level': 'WARNING',
#             'filters': ['require_debug_false'],
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': 'django_production.log',
#             'maxBytes' : 1024*1024*100, # 100MB
#             'backupCount' : 5,
#             'formatter': 'verbose',
#         },
#         'sentry': {
#             'level': 'ERROR',
#             'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
#         }
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['production_logfile'],
#             'level': 'WARNING',
#             'propagate': False,
#         },
#         'location_register': {
#             'handlers': ['console', 'production_logfile', 'sentry'],
#             'level': 'INFO',
#         },
#         'business_register': {
#             'handlers': ['console', 'production_logfile', 'sentry'],
#             'level': 'INFO',
#         },
#     }
# }
