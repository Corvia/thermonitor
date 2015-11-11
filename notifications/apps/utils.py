"""
# Force sending out an notification.
#
# This is useful for testing, however it's also used in the check_for_down_sensors.py script.
#
# Accepts a sensor object and a notification message type (alert, down, recovered)
"""
from django.conf import settings

def send_notification(sensor, sensor_data, notification_message_type):
    # Load the modules dynamcally, create a class, call constructor, then alert type and message methods.
    for notification_module, config in settings.NOTIFICATIONS.iteritems():
        module = __import__("notifications.apps." + notification_module.lower(), fromlist=[notification_module])
        obj = getattr(module, notification_module)
        notification = obj(sensor, sensor_data)
        if notification_message_type in notification.message_types:
            getattr(notification, notification_message_type)()
            notification.alert_type = notification_message_type
            notification.send()
