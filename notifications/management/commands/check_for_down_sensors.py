from django.core.management.base import BaseCommand, CommandError
from sensors.models import Sensor, SensorData
from django.conf import settings
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Checks for Down or Inactive Sensors'

    def handle(self, *args, **options):
        sensors = Sensor.objects.all()
        for sensor in sensors:
            down = False

            # Get last sensor data entry
            data = SensorData.objects.filter(sensor=sensor).order_by("-datetime")[0:1]

            old_before_datetime = datetime.now() - timedelta(minutes=settings.SENSOR_DOWN_AFTER_MINUTES)

            # If the data is there, how old is it?
            if data and data.datetime < old_before_datetime:
                # Data is old, device is down.
                down = True
            elif data is None and sensor.create_date < old_before_datetime:
                # Device is not a new one, device is down.
                down = True

            if down:
                



            # if it exists, check the date
            # if it has no data, check the created date

            # is last check-in date (or create date) < current date - settings.SENSOR_DOWN_TIME?
            # is the state of the sensor good?
                 # send out an alert