from django.db import models
import operator
from decimal import Decimal
# Create your models here.

OPERATOR_CHOICES = (
    ('>',  '>'),
    ('<',  '<'),
    ('>=', '>='),
    ('<=', '<='),
)

OPERATOR_LOOKUP = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
}



"""
Zone

A container of multiple sensors. Sensors are grouped by Zone in the UI and API.

- By default, sort these by name.
- API Key is automatically generated when we create new Zones. This is set in pre_save
  listener in zone_set_api_key in sensors.signals.

"""
class Zone(models.Model):
    name = models.CharField(
        "Building Name",
        max_length = 120,
        help_text = "Zone Name. Displayed in the frontend, and sensors are grouped in buildings.",
    )
    notes = models.TextField(
        "Building Notes",
        blank = True,
        help_text = "Notes specific to this building, structure, location or wherever the sensors are.",
    )
    key = models.CharField(
        "Unique API Key",
        max_length = 32,
        blank = True, # Initially needs to allow blank fields for the signal to work.
    )

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


"""
Sensor Device

- Each sensor has a GUID. This is a unique identifer pulled from the device itself,
  it could be a MAC address, serial number, etc. It doesn't matter, it just needs to be
  unique.
- Minimum and maximum value checks are optional, they won't be checked if they are left
  blank. This means each sensor can have 0, 1 or 2 checks.
- If the sensor fails the check, everyone in the associated alert groups will receive a notification.
- state_last_change_date will help us track how long a device has been failed or working fine.

"""

class Sensor(models.Model):
    name = models.CharField(
        "Sensor Name",
        max_length = 120,
        help_text = "Sensor Name and Location. Displayed under the temperature guage in the website.",
    )
    zone = models.ForeignKey(Zone)
    guid = models.CharField(
        "Unique Identifier",
        max_length = 120,
        help_text = "Unique identifier of the sensor device. MAC address, serial number, etc. Automatically set by the API.",
    )
    notes = models.TextField(
        "Sensor Notes",
        blank = True,
        help_text = "Notes specific to this sensor, location, contact information.",
    )
    min_value = models.DecimalField(
        "Minimum Check Value",
        max_digits = 4,
        decimal_places = 1,
        help_text = "Lower range threshold value."
    )
    min_value_operator = models.CharField(
        "Minimum Value Check Operator",
        max_length = 3,
        blank = True,
        choices = OPERATOR_CHOICES,
        help_text = "Comparison operator for the lower range check."
    )
    max_value = models.DecimalField(
        "Maximum Check Value",
        max_digits = 4,
        decimal_places = 1,
        help_text = "Upper range threshold value."
    )
    max_value_operator = models.CharField(
        "Minimum Value Check Operator",
        max_length = 3,
        blank = True,
        choices = OPERATOR_CHOICES,
        help_text = "Comparison operator for the upper range check."
    )
    alert_groups = models.ManyToManyField(
        "notifications.SensorAlertGroup",
        help_text = "Groups to notify when this sensor is triggered."
    )
    state = models.BooleanField(default = False)
    state_last_change_date = models.DateTimeField(
        "Last State Change",
        blank = True,
        help_text = "Date/Time of the last state change of this sensor."
    )

    def __unicode__(self):
        return "%s - %s" % (self.zone.name, self.name)

    class Meta:
        ordering = ["zone__name", "name"]

    """ 
    Compare a sensor data value to the thresholds specified in this Sensor object.
    - If set, use the minimum and maximum thresholds to pull the specified operator
      from the OPERATOR_LOOKUP mapping above.
    - Returns True if value is OK
    - Returns False if value is not meeting the thresholds

    TODO:
    - Some idiot could add an operator to only OPERATOR_CHOICES, resulting in a key error below. Validate for this.
    - Data model assumes we could have 0, 1, or 2 checks. Fine for this project. Not OK for other projects.
    """
    def check_value(self, value):
        if self.min_value_operator and not OPERATOR_LOOKUP[self.min_value_operator](value, self.min_value):
            return False
        if self.max_value_operator and not OPERATOR_LOOKUP[self.max_value_operator](value, self.max_value):
            return False
        # Nothing out of the ordinary, assume we are fine...
        return True



    """
    Get all users assigned to receive alerts from a sensor.

    Return a list of user objects.
    """
    def get_alert_users(self):
        users = []

        for group in self.alert_groups.all():
           for user in group.users.all():
                users.append(user)
    
        return users



"""
Sensor Data

- We expect all of our sensors in this app to store values in a Decimal format (XXX.X).
- Record if this value is outside of the range checks for the sensor and if the state
  changed compared to the last check (OK -> failed, failed -> OK). This will allow us
  graph/query data points where the checks failed and how many times relatively easily.

"""

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor)
    datetime = models.DateTimeField(auto_now_add = True)
    value = models.DecimalField(
        "Sensor Data Value - Celcius",
        max_digits = 4,
        decimal_places = 1,
    )
    
    """ State of this sensor. True is status is within limits, False is the status is failing a check. """
    state = models.BooleanField()

    """ If this sensor state changed since the last time data was reported. Might be useful for reporting. """
    state_changed = models.BooleanField()

    def __unicode__(self):
        return "%s - %s" % (self.sensor.name, self.value)

    class Meta:
        ordering = ["-datetime"]

    """
    Return the temperature value in degrees Fahrenheit
    """
    def value_f(self):
        return int(Decimal(9.0 / 5.0) * self.value + Decimal(32.0))
