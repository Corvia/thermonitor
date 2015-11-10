"""

Example settings_local.py file. Imported at bottom of the settings.py.

Rename to settings_local.py for some sane default settings.

"""




"""
Notification apps are located in notifications/apps/. Each app has some 
additional configuration options (for example, email From: address for 
the emails).
"""
NOTIFICATIONS = {
<<<<<<< HEAD
    'Email': {
=======
    'email': {
>>>>>>> 009ee7916e5d96e6da9406594a794ad7c01fba46
        'FROM_ADDRESS': 'Thermonitor <thermonitor@rpnutrients.com>',
    },
    #'twilio-text' = {},
    #'square-pos' = {},
    #'slack' = {},
<<<<<<< HEAD
}


"""
The number of minutes we should wait until we send a notification that
the sensor hasn't checked in for awhile.
"""
SENSOR_DOWN_AFTER_MINUTES = 30
=======
}
>>>>>>> 009ee7916e5d96e6da9406594a794ad7c01fba46
