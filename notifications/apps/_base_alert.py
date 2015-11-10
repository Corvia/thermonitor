from django.conf import settings

class BaseAlert:
    def __init__(self, sensor, sensor_data):
        self.name = self.__class__.__name__.lower()
        self.sensor = sensor
        self.sensor_data = sensor_data

        self.settings = {}
        if self.name in settings.NOTIFICATIONS:
            self.settings = settings.NOTIFICATIONS[self.name]

        self.setup()
    
    def setup():
        pass

    def send():
        pass