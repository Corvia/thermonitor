# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Sensor Name and Location. Displayed under the temperature guage in the website.', max_length=120, verbose_name=b'Sensor Name')),
                ('guid', models.CharField(help_text=b'Unique identifier of the sensor device. MAC address, serial number, etc. Automatically set by the API.', max_length=120, verbose_name=b'Unique Identifier')),
                ('notes', models.TextField(help_text=b'Notes specific to this sensor, location, contact information.', verbose_name=b'Sensor Notes', blank=True)),
                ('min_value', models.DecimalField(help_text=b'Lower range threshold value.', verbose_name=b'Minimum Check Value', max_digits=4, decimal_places=1)),
                ('min_value_operator', models.CharField(blank=True, help_text=b'Comparison operator for the lower range check.', max_length=3, verbose_name=b'Minimum Value Check Operator', choices=[(b'>', b'>'), (b'<', b'<'), (b'>=', b'>='), (b'<=', b'<=')])),
                ('max_value', models.DecimalField(help_text=b'Upper range threshold value.', verbose_name=b'Maximum Check Value', max_digits=4, decimal_places=1)),
                ('max_value_operator', models.CharField(blank=True, help_text=b'Comparison operator for the upper range check.', max_length=3, verbose_name=b'Minimum Value Check Operator', choices=[(b'>', b'>'), (b'<', b'<'), (b'>=', b'>='), (b'<=', b'<=')])),
                ('state', models.BooleanField(default=False)),
                ('state_last_change_date', models.DateTimeField(help_text=b'Date/Time of the last state change of this sensor.', verbose_name=b'Last State Change', blank=True)),
                ('alert_groups', models.ManyToManyField(help_text=b'Groups to notify when this sensor is triggered.', to='notifications.SensorAlertGroup')),
            ],
            options={
                'ordering': ['zone__name', 'name'],
            },
        ),
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('value', models.DecimalField(verbose_name=b'Sensor Data Value', max_digits=4, decimal_places=1)),
                ('state', models.BooleanField()),
                ('state_changed', models.BooleanField()),
                ('sensor', models.ForeignKey(to='sensors.Sensor')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Zone Name. Displayed in the frontend, and sensors are grouped in buildings.', max_length=120, verbose_name=b'Building Name')),
                ('notes', models.TextField(help_text=b'Notes specific to this building, structure, location or wherever the sensors are.', verbose_name=b'Building Notes', blank=True)),
                ('key', models.CharField(max_length=32, verbose_name=b'Unique API Key', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='sensor',
            name='zone',
            field=models.ForeignKey(to='sensors.Zone'),
        ),
    ]
