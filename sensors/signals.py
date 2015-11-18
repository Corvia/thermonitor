from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from sensors.models import SensorData, Zone
from datetime import datetime
import uuid
from notifications.apps.utils import send_notification


@receiver(pre_save, sender=Zone)
def zone_set_api_key(sender, instance, *args, **kwargs):
    """Automatically set API key for new zones before they are saved to the database.
    Set API key to something like '0172ZD9A1ASF4414B88D6b9A6FEB91EB'
    """
    if instance.pk is None:
        instance.key = str(uuid.uuid4()).replace("-", "").upper()


@receiver(pre_save, sender=SensorData)
def sensor_data_process(sender, instance, *args, **kwargs):
    """
    Process Sensor Data
    - If a sensor is marked as down, it should be up now.
    - Update state
    - Update last_state_change if the state has changed.
    - If the threshold checks fail, send out notifications.
    """
    sensor = instance.sensor

    if sensor.down:
        sensor.down = False
        sensor.save()

    state = sensor.check_value(instance.value)
    instance.state = state

    if sensor.state != state:
        sensor.state = state
        sensor.state_last_change_date = datetime.utcnow()
        sensor.save()
        instance.state_changed = True


@receiver(post_save, sender=SensorData)
def sensor_data_state_change(sender, instance, *args, **kwargs):
    """
    Send Sensor Data notifications
    - If the state of a sensor changed with this save, send out a notification.
    """
    if instance.state_changed:
        if instance.sensor.state:
            # Recovered
            send_notification(instance.sensor, instance, "recovered")
        else:
            # Failed
            send_notification(instance.sensor, instance, "alert")
