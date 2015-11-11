# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20151105_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensoralert',
            name='alert_class',
            field=models.CharField(help_text=b'The method the user was notified. Ex: Email, Twilio, POS, etc.', max_length=60, verbose_name=b'Alert Class', blank=True),
        ),
        migrations.AddField(
            model_name='sensoralert',
            name='alert_type',
            field=models.CharField(help_text=b'Type of Alert: alert, recovered, down', max_length=60, verbose_name=b'Alert Type', blank=True),
        ),
    ]
