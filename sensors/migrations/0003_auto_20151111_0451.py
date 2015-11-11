# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0002_auto_20151110_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='guid',
            field=models.CharField(help_text=b'Unique identifier of the sensor device. MAC address, serial number, etc.', max_length=120, verbose_name=b'Unique Identifier', db_index=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='max_value',
            field=models.DecimalField(default=b'45.0', help_text=b'Upper range threshold value, in degrees Fahrenheit.', verbose_name=b"Maximum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='max_value_operator',
            field=models.CharField(default=b'<', choices=[(b'>', b'>'), (b'<', b'<'), (b'>=', b'>='), (b'<=', b'<=')], max_length=3, blank=True, help_text=b'Comparison operator for the upper range check.', verbose_name=b'Minimum Value Check Operator'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='min_value',
            field=models.DecimalField(default=b'33.0', help_text=b'Lower range threshold value, in degrees Fahrenheit.', verbose_name=b"Minimum Check Value ('F)", max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='min_value_operator',
            field=models.CharField(default=b'>', choices=[(b'>', b'>'), (b'<', b'<'), (b'>=', b'>='), (b'<=', b'<=')], max_length=3, blank=True, help_text=b'Comparison operator for the lower range check.', verbose_name=b'Minimum Value Check Operator'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='state_last_change_date',
            field=models.DateTimeField(help_text=b'Date/Time of the last state change of this sensor.', verbose_name=b'Last State Change', auto_now_add=True),
        ),
        migrations.AlterUniqueTogether(
            name='sensor',
            unique_together=set([('zone', 'guid')]),
        ),
    ]
