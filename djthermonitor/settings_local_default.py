"""

Example settings_local.py file. Imported at bottom of the settings.py.

Rename to settings_local.py for some sane default settings.

"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False


"""
Notification apps are located in notifications/apps/. Each app has some 
additional configuration options (for example, email From: address for 
the emails).
"""
NOTIFICATIONS = {
    'Email': {
        'FROM_ADDRESS': 'Thermonitor <thermonitor@rpnutrients.com>',
    },
    #'twilio-text' = {},
    #'square-pos' = {},
    #'slack' = {},
}


"""
The number of minutes we should wait until we send a notification that
the sensor hasn't checked in for awhile.
"""
SENSOR_DOWN_AFTER_MINUTES = 30


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #}
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djthermonitor',
        'USER': 'djthermonitor',
        'PASSWORD': '@@@@POSTGRESQL_PASSWORD@@@@',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


SECRET_KEY = '@@@@DJANGO_SECRET@@@@'
