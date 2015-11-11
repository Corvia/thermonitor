# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_auto_20151111_0638'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensoralert',
            name='recipients',
            field=models.TextField(help_text=b'List of email addresses, phone numbers, etc. that this alert was sent to.', verbose_name=b'Raw Recipients List', blank=True),
        ),
    ]
