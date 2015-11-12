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
	users = models.ManyToManyField(User, blank=True)

	def __unicode__(self):
		return self.name


"""
Alert

- Track when users are alerted a sensor has an issue.
- Basically, just a log of when things went haywire or were fixed.

"""

class SensorAlert(models.Model):
	
	users = models.ManyToManyField(User, blank=True)
	sensor = models.ForeignKey("sensors.Sensor")
	data_point = models.ForeignKey("sensors.SensorData")
	alert_type = models.CharField(
		"Alert Type",
		max_length = 60,
		help_text = "Type of Alert: alert, recovered, down",
		blank = True,
	)
	alert_class = models.CharField(
		"Alert Class",
		max_length = 60,
		help_text = "The method the user was notified. Ex: Email, Twilio, POS, etc.",
		blank = True,
	)
	recipients = models.TextField(
		"Raw Recipients List",
		help_text = "List of email addresses, phone numbers, etc. that this alert was sent to.",
		blank = True,
	)
	message = models.TextField()
	date = models.DateTimeField(auto_now=True)


	def __unicode__(self):
		return "%s - %s - %s" % (self.sensor.name, self.message, self.recipients)