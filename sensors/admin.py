from django.contrib import admin
from sensors.models import Zone, Sensor, SensorData, SensorUnit

# Register your models here.

admin.site.register(Zone)
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(SensorUnit)
