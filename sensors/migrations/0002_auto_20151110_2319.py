# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 10, 23, 19, 13, 540403, tzinfo=utc), auto_now_add=True, help_text=b'Automatically set to the date the sensor is saved. Used for helping determine if the device is down.', verbose_name=b'Sensor Create Date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sensor',
            name='max_value',
            field=models.DecimalField(help_text=b'Upper range threshold value, in degrees Fahrenheit.', verbose_name=b"Maximum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='min_value',
            field=models.DecimalField(help_text=b'Lower range threshold value, in degrees Fahrenheit.', verbose_name=b"Minimum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='value',
            field=models.DecimalField(verbose_name=b'Sensor Data Value - Celsius', max_digits=4, decimal_places=1),
        ),
    ]
