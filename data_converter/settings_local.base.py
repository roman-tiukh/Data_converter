import os
from celery.schedules import crontab

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
DEBUG_TOOLBAR = False

# SITE URLS
# For development mode
FRONTEND_SITE_URL = 'http://localhost:3000'
BACKEND_SITE_URL = 'http://localhost:8000'
# For production mode
# FRONTEND_SITE_URL = 'https://dp.dataocean.us'
# BACKEND_SITE_URL = 'https://ipa.dataocean.us'

# Custom user registration
CANDIDATE_EXPIRE_MINUTES = 5
# Send user_registration/reset_password email by POSTMAN or EMAIL_BACKEND
SEND_MAIL_BY_POSTMAN = False
# AUTHORIZATION TOKEN FOR POSTMAN
POSTMAN_TOKEN = 'e7937e4b5a309177b85fad8715bcbd451fdcb67f91696e1968f8dd188ada70a1'
# URL FOR POSTMAN
POSTMAN_URL = 'https://postman.org.ua/'

SENDGRID_API_KEY = 'change_me!'

EMAIL_BACKEND = 'data_converter.email_backends.sendgrid.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
POSTMAN_EMAIL_PORT = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SUPPORT_EMAIL = ''
REPORT_EMAILS = ['', ]
DEVELOPER_EMAILS = ['', ]

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

LOCAL_FOLDER = 'unzipped_xml/'


DATA_GOV_UA_DATASETS_URL = 'https://data.gov.ua/dataset/'
DATA_GOV_UA_SOURCE_PACKAGE = 'https://data.gov.ua/api/3/action/package_show?id='

LOCATION_KOATUU_SOURCE_REGISTER_ID = "dc081fb0-f504-4696-916c-a5b24312ab6e"
LOCATION_KOATUU_SOURCE_PACKAGE = DATA_GOV_UA_SOURCE_PACKAGE + LOCATION_KOATUU_SOURCE_REGISTER_ID
LOCATION_KOATUU_LOCAL_FILE_NAME = 'koatuu.json'
LOCAL_FILE_NAME_KOATUU = ''

LOCATION_RATU_SOURCE_REGISTER_ID = "a2d6c060-e7e6-4471-ac67-42cfa1742a19"
LOCATION_RATU_SOURCE_PACKAGE = DATA_GOV_UA_SOURCE_PACKAGE + LOCATION_RATU_SOURCE_REGISTER_ID
LOCAL_FILE_NAME_RATU = '28-ex_xml_atu.xml'
CHUNK_SIZE_RATU = 100

LOCATION_DRV_WSDL_URL = 'https://www.drv.gov.ua/ords/svc/personal/API/Opendata'
LOCATION_DRV_STRICT = False
LOCATION_DRV_XML_HUGE_TREE = True

BUSINESS_KVED_SOURCE_REGISTER_ID = "e1afb81c-70e4-4009-96a0-b240c36e4603"
BUSINESS_KVED_SOURCE_PACKAGE = DATA_GOV_UA_SOURCE_PACKAGE + BUSINESS_KVED_SOURCE_REGISTER_ID
LOCAL_FILE_NAME_KVED = ''
FILE_URL_KVED = ''

BUSINESS_FOP_SOURCE_REGISTER_ID = '1c7f3815-3259-45e0-bdf1-64dca07ddc10'
BUSINESS_FOP_SOURCE_PACKAGE = DATA_GOV_UA_SOURCE_PACKAGE + BUSINESS_FOP_SOURCE_REGISTER_ID
LOCAL_FILE_NAME_FOP = ''
CHUNK_SIZE_FOP = 100

BUSINESS_UKR_COMPANY_SOURCE_REGISTER_ID = '1c7f3815-3259-45e0-bdf1-64dca07ddc10'
BUSINESS_UKR_COMPANY_SOURCE_PACKAGE = DATA_GOV_UA_SOURCE_PACKAGE + BUSINESS_UKR_COMPANY_SOURCE_REGISTER_ID
LOCAL_FILE_NAME_UO = ''
CHUNK_SIZE_UO = 100
LOCAL_FILE_NAME_UO_FULL = ''
CHUNK_SIZE_UO_FULL = 100

LOCAL_FILE_NAME_UO_ADDRESS = ''
LOCAL_FILE_NAME_UO_SIGNER = ''
LOCAL_FILE_NAME_UO_FOUNDER = ''
LOCAL_FILE_NAME_UO_NAME = ''
LOCAL_FILE_NAME_UO_SHORTNAME = ''
LOCAL_FILE_NAME_UO_CAPITAL = ''
LOCAL_FILE_NAME_UO_BRANCH = ''
LOCAL_FILE_NAME_UO_INFO = ''

BUSINESS_UK_COMPANY_SOURCE = 'https://download.companieshouse.gov.uk/'
BUSINESS_UK_COMPANY_SOURCE_PAGE = BUSINESS_UK_COMPANY_SOURCE + 'en_output.html'
BUSINESS_UK_COMPANY_SOURCE_XPATH = '//*[@id="mainContent"]/div[2]/ul[1]/li/a/@href'

BUSINESS_PEP_AUTH_USER = ''
BUSINESS_PEP_AUTH_PASSWORD = ''
BUSINESS_PEP_SOURCE_URL = 'https://pep.org.ua/opendata/persons/json'

# AWS S3 configuration and credentials
AWS_S3_ACCESS_KEY_ID = ''
AWS_S3_SECRET_ACCESS_KEY = ''
AWS_S3_REGION_NAME = 'eu-central-1'
AWS_S3_BUCKET_NAME = 'do-export'


# PEP use SSH for connection
PEP_SOURCE_USE_SSH = False
# ssh params
PEP_TUNNEL_TIMEOUT = 5.0
PEP_SSH_TIMEOUT = 5.0
PEP_SSH_SERVER_IP = ''
PEP_SSH_SERVER_PORT = 22
PEP_SSH_USERNAME = ''
PEP_SSH_PKEY = ''
# postgres params
PEP_SOURCE_HOST = ''
PEP_SOURCE_PORT = 5432
PEP_SOURCE_DATABASE = ''
PEP_SOURCE_USER = ''
PEP_SOURCE_PASSWORD = ''
# PEP_LOCAL_SOURCE_HOST = '0.0.0.0'
# PEP_LOCAL_SOURCE_PORT = 8080


REDIS_PASSWORD = 'You_Redis_Password'


CACHES = {
    'default': {
        # REDIS cache configs
        # 'BACKEND': 'django_redis.cache.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
        # 'OPTIONS': {
        #     "IGNORE_EXCEPTIONS": True,
        #     # 'PASSWORD': f'{REDIS_PASSWORD}',
        #     'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        # },

        # Dummy Cache for developing
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # use this cashe for developing
    },
}

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'


# celery settings
# CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@localhost:6379/2'
# CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600 * 24 * 5, 'max_retries': 0, }
# CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERYD_MAX_TASKS_PER_CHILD = 1
# FLOWER_BROKER = CELERY_RESULT_BACKEND
# FLOWER_PORT = 5555


# use CELERY_BEAT_SHEDULE to set periodic tasks in code, without admin aplication/ periodic tasks
# CELERY_BEAT_SCHEDULE = {
#     'test_task': {
#         'task': 'data_ocean.tasks.test_task',
#         'schedule': crontab(minute='*/1'),
#     },
#     'update_pep': {
#         'task': 'business_register.tasks.update_pep',
#         'schedule': crontab(hour=10, minute=30),
#     },
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
# DEBUG_PROPAGATE_EXCEPTIONS = True

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

# PEP_SCHEMA_TOKENS - dictionary of `<hostname>`: `<token>`. hostname without port
# for generate token use
# date +%s | sha256sum | base64 | head -c 50 ; echo
# or
# < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-50};echo;
PEP_SCHEMA_TOKENS = {
    'google.com': 'mThmM2Q1MTU1MoVlNGRkNjdkOTcyYTk2YmE5Njc2YjdmYWQzMj',
}
