from django.core.management.base import BaseCommand
from sensors.models import Sensor, SensorData
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from notifications.apps.utils import send_notification


class Command(BaseCommand):
    """
    Cron script for checking for down sensors.

    Sends out notifications based on inactive hosts and the
    settings.SENSOR_DOWN_AFTER_MINUTES varirable.

    Here's the crontab config. Adjust the minutes as necessary, this checks every 15 minutes:

    */15 * * * *  cd /home/user/thermonitor; \
         /path/to/virtualenv/bin/python manage.py check_for_down_sensors >/dev/null 2>&1

    """
    help = 'Checks for Down or Inactive Sensors'

    def handle(self, *args, **options):
        sensors = Sensor.objects.all()
        for sensor in sensors:
            print sensor
            down = False

            # Get last sensor data entry
            data = SensorData.objects.filter(sensor=sensor).order_by("-datetime")[0:1]

            nowtz = timezone.make_aware(datetime.now())
            delta = timedelta(minutes=settings.SENSOR_DOWN_AFTER_MINUTES)

            old_before_datetime = nowtz - delta
            if data and data[0]:
                since = str(data[0].datetime)
            else:
                since = "???"

            # If the data is there, how old is it?
            if len(data) > 0 and data[0].datetime < old_before_datetime:
                # Data is old, device is down.
                down = True
            elif sensor.create_date < old_before_datetime:
                # Device is not a new one, device is down.
                down = True

            if down and not sensor.down:
                print "   - sending alert, down %s - %s" % (sensor, since)
                try:
                    send_notification(sensor, data[0], "down")
                except KeyError:
                    # If data[0] doesn't exist, the sensor doesn't have any
                    # active data anyway, and we probably don't care.
                    pass
                sensor.down = True
                sensor.save()

            elif sensor.down:
                print "   - sensor already down %s" % sensor
            else:
                print "   + still up %s - %s" % (sensor, since)
