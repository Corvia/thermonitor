"""
# Force sending out an notification.
#
# This is useful for testing, however it's also used in the check_for_down_sensors.py script.
#
# Accepts a sensor object and a notification message type (alert, down, recovered)
"""
def send_notification(sensor, notification_message_type):