# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0004_auto_20151111_0604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='max_value',
            field=models.DecimalField(default=b'10.0', help_text=b'Upper range threshold value, in degrees Celsius.', verbose_name=b"Maximum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='min_value',
            field=models.DecimalField(default=b'2.0', help_text=b'Lower range threshold value, in degrees Celsius.', verbose_name=b"Minimum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='state',
            field=models.BooleanField(default=True, help_text=b'If True, sensor is within threshold checks.', verbose_name=b'Sensor OK'),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='state',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='state_changed',
            field=models.BooleanField(default=False),
        ),
    ]
