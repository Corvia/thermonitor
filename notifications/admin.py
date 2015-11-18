from django.contrib import admin
from notifications.models import SensorAlertGroup, SensorAlert

# Register your models here.

admin.site.register(SensorAlertGroup)
admin.site.register(SensorAlert)
