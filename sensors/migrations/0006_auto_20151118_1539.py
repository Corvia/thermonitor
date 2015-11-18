# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0005_auto_20151111_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='alert_groups',
            field=models.ManyToManyField(help_text=b'Groups to notify when this sensor is triggered.', to='notifications.SensorAlertGroup', blank=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='create_date',
            field=models.DateTimeField(help_text=(b'Automatically set to the date the sensor is saved. ', b'Used for helping determine if the device is down.'), verbose_name=b'Sensor Create Date', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='max_value',
            field=models.DecimalField(default=b'75.0', help_text=b'Upper range threshold value, in degrees Fahrenheit.', verbose_name=b"Maximum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='min_value',
            field=models.DecimalField(default=b'35.0', help_text=b'Lower range threshold value, in degrees Fahrenheit.', verbose_name=b"Minimum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='value',
            field=models.DecimalField(verbose_name=b'Sensor Data Value - Fahrenheit', max_digits=4, decimal_places=1),
        ),
    ]
