from rest_framework import serializers
from notifications.models import SensorAlert, SensorAlertGroup

class SensorAlertSerializer(serializers.HyperlinkedModelSerializer):
    """A DRF serializer for `SensorAlert` objects."""
    class Meta:
        """Contains metadata for the DRF `SensorAlert`."""
        model = SensorAlert
        fields = ('id', 'sensor', 'data_point', 'alert_type', 'alert_class',
            'recipients', 'message', 'date')
        read_only_fields = ('id', 'sensor', 'data_point', 'alert_type',
            'alert_class', 'recipients', 'message', 'date')