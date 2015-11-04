from django.db import models
# Create your models here.

OPERATORS = (
	('>',  '>'),
	('<',  '<'),
	('>=', '>='),
	('<=', '<='),
)


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
	)


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
		choices = OPERATORS,
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
		choices = OPERATORS,
		help_text = "Comparison operator for the upper range check."
	)
	alert_groups = models.ManyToManyField(
		"Sensor Alert Groups",
		"notifications.SensorAlertGroup",
		help_text = "Groups to notify when this sensor is triggered."
	)
	state = models.BooleanField(default = False)
	state_last_change = models.DateTimeField(
		"Last State Change",
		blank = True,
		help_text = "Timestamp of the last state change of this sensor."
	)


class SensorData(models.Model):
	sensor = models.ForeignKey(Sensor)
	datetime = models.DateTimeField(auto_now_add = True)
	value = models.DecimalField(
		"Sensor Data Value",
		max_digits = 4,
		decimal_places = 1,
	)
	
	""" State of this sensor. True is status is within limits, False is the status is failing a check. """
	state = models.BooleanField()

	""" If this sensor state changed since the last time data was reported. Might be useful for reporting. """
	state_changed = models.BooleanField()
