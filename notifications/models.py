from django.db import models
from django.contrib.auth.models import User

"""
Alert Group

- Group of Django user contacts that will be notified when an associated sensor fails.
- We can have multiple groups of contacts associated with each sensor.

"""

class SensorAlertGroup(models.Model):
	name = models.CharField(
		"Alert Group Name",
		max_length = 120,
	)
	desc = models.TextField(
		"Alert Group Description",
		blank = True,
	)
	users = models.ManyToManyField(User)

	def __unicode__(self):
		return self.name


"""
Alert

- Track when users are alerted a sensor has an issue.
- Basically, just a log of when things went haywire or were fixed.

"""

class SensorAlert(models.Model):
	
	user = models.ForeignKey(User)
	sensor = models.ForeignKey("sensors.Sensor")
	data_point = models.ForeignKey("sensors.SensorData")
	message = models.TextField()
	date = models.DateTimeField(auto_now=True)


	def __unicode__(self):
		return "%s - %s - %s" % (self.sensor.user.name, self.sensor.name, self.message)