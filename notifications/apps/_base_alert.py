from django.conf import settings


"""
# BaseAlert class is overriden by notification method types.
# 
# Alert, Down, Recovered and Send are required.
# Setup is a helper method to set common variables before the other methods are called.
# 
"""
class BaseAlert:
    def __init__(self, sensor, sensor_data):
        self.name = self.__class__.__name__.lower()
        self.sensor = sensor
        self.sensor_data = sensor_data

        self.settings = {}
        if self.name in settings.NOTIFICATIONS:
            self.settings = settings.NOTIFICATIONS[self.name]

        self.setup()

    """
    # alert, recovered and down methods all configure this class for sending
    # out a notification based on the state of the sensor.
    """

    # Sensor exceeds threshold checks and is failing
    def alert(self):
        pass

    # Sensor has become unavailable or is late to report in
    def down(self):
        pass

    # Sensor has recovered (either temperature within thresholds or is back online)
    def recovered(self):
        pass
    

    """
    # Class configuration method loads any pertitent information relating to sending
    # the notification.
    #
    # Example: email class loads the email addresses we should deliver alerts to.
    """
    def setup(self):
        pass

    """
    # Send the alert. Notification is not sent until we actually call this method.
    """
    def send(self):
        pass