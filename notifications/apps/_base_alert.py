from django.conf import settings


class BaseAlert:
    """BaseAlert class is overriden by notification method types.

    Alert, Down, Recovered and Send are required.
    Setup is a helper method to set common variables before the other methods are called.
    """
    def __init__(self, sensor, sensor_data):
        self.name = self.__class__.__name__
        self.sensor = sensor
        self.sensor_data = sensor_data
        self.alert_type = ""  # Set in utils.py / send_notification

        self.settings = {}
        if self.name in settings.NOTIFICATIONS:
            self.settings = settings.NOTIFICATIONS[self.name]

        self.setup()

    # alert, recovered and down methods all configure this class for sending
    # out a notification based on the state of the sensor.

    message_types = ["alert", "down", "recovered"]

    def alert(self):
        """Sensor exceeds threshold checks and is failing"""
        pass

    def down(self):
        """Sensor has become unavailable or is late to report in"""
        pass

    def recovered(self):
        """Sensor has recovered (either temperature within thresholds or is back online)"""
        pass

    def setup(self):
        """Class configuration method loads any pertitent information relating to sending
        the notification.

        Example: email class loads the email addresses we should deliver alerts to.
        """
        pass

    def send(self):
        """Send the alert. Notification is not sent until we actually call this method."""
        pass
