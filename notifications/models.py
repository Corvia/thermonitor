from django.db import models
from django.contrib.auth.models import User
from sensors.models import Sensor

# Create your models here.

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


class SensorAlert(models.Model):
	date = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	sensor = models.ForeignKey(Sensor)
	message = models.TextField()