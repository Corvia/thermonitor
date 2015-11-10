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
    'email': {
        'FROM_ADDRESS': 'Thermonitor <thermonitor@rpnutrients.com>',
    },
    #'twilio-text' = {},
    #'square-pos' = {},
    #'slack' = {},
}