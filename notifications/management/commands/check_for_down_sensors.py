from django.core.management.base import BaseCommand, CommandError
from sensors.models import Sensor, SensorData
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Checks for Down or Inactive Sensors'

    def handle(self, *args, **options):
        sensors = Sensor.objects.all()
        for sensor in sensors:
            print sensor
            down = False

            # Get last sensor data entry
            data = SensorData.objects.filter(sensor=sensor).order_by("-datetime")[0:1]

            old_before_datetime = timezone.make_aware(datetime.now()) - timedelta(minutes=settings.SENSOR_DOWN_AFTER_MINUTES)
            if data and data[0]:
                since =  str(data[0].datetime)
            else:
                since = "???"
            print "+         currently checking against %s" % (old_before_datetime)


            # If the data is there, how old is it?
            if data[0].datetime < old_before_datetime:
                # Data is old, device is down.
                down = True
            elif sensor.create_date < old_before_datetime:
                # Device is not a new one, device is down.
                down = True

            if down and not sensor.down:
                print "down %s - %s" % (sensor, since)
                #send_notification(sensor, data, "down")

                #sensor.down = True
                #sensor.save()
            elif sensor.down:
                print "sensor already down %s" % sensor
            else:
                print "+ still up %s - %s" % (sensor, since)