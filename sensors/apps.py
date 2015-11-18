"""
Very useful django 1.8 signals layout was stolen from here:
http://stackoverflow.com/questions/31973707/django-signals-how-to-initialize-bindings
"""

from django.apps import AppConfig


class SensorAppConfig(AppConfig):
    name = "sensors"

    def ready(self):
        from . import signals  # noqa
