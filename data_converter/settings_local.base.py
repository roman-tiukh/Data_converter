
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATABASE_CONFIG = {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
# }

DATABASE_CONFIG = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "data_oceanv2",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.01",
        "PORT": "5432",
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
            }

LOCAL_FILE_NAME_KOATUU = ''
LOCAL_FOLDER = ''
FILE_URL_KVED = ''
LOCAL_FILE_NAME_KVED = ''