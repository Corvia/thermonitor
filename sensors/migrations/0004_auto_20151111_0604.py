# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0003_auto_20151111_0451'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='down',
            field=models.BooleanField(default=True, help_text=b'If True, Sensor is offline.', verbose_name=b'Sensor Offline'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='state',
            field=models.BooleanField(default=False, help_text=b'If True, sensor is within threshold checks.', verbose_name=b'Sensor OK'),
        ),
    ]
