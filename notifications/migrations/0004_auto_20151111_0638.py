# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0003_auto_20151111_0634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensoralert',
            name='user',
        ),
        migrations.AddField(
            model_name='sensoralert',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
