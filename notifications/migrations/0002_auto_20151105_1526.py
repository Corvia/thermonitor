# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensoralert',
            name='data_point',
            field=models.ForeignKey(to='sensors.SensorData'),
        ),
        migrations.AddField(
            model_name='sensoralert',
            name='sensor',
            field=models.ForeignKey(to='sensors.Sensor'),
        ),
        migrations.AddField(
            model_name='sensoralert',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
