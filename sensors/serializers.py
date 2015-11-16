from datetime import datetime
from rest_framework import serializers
from sensors.models import Sensor, SensorData, Zone

class SensorSerializer(serializers.HyperlinkedModelSerializer):
    """A DRF serializer for `Sensor` objects."""
    def create(self, validated_data):
        """Createa `Sensor` instance using `validated_data`.

        The `state` and `state_last_change_date` are read-only because they
        can't be changed by users (they're effectively computed values).
        However, they're required for new instances. As such, default values
        must be set here.
        """
        validated_data['state'] = True
        validated_data['state_last_change_date'] = datetime.utcnow()
        return super(SensorSerializer, self).create(validated_data)

    class Meta:
        """Contains metadata for the DRF `Sensor` serializer class."""
        model = Sensor
        fields = ('id', 'guid', 'name', 'notes', 'state',
            'state_last_change_date', 'zone', 'min_value', 'max_value',
            'min_value_operator', 'max_value_operator')
        read_only_fields = ('state', 'state_last_change_date')

class SensorDataSerializer(serializers.HyperlinkedModelSerializer):
    """A DRF serializer for `SensorData` objects."""
    def create(self, validated_data):
        """Create a `SensorData` instance using `validated_data`.

        The `state` and `state_changed` values are automatically set based on
        the associated `Sensor`'s properties.
        """
        sensor = validated_data['sensor']
        validated_data['state'] = sensor.check_value(validated_data['value'])
        validated_data['state_changed'] = validated_data['state'] != sensor.state

        if validated_data['state_changed']:
            sensor.state = validated_data['state']
            sensor.state_last_change_date = datetime.utcnow()
            sensor.save()

        return super(SensorDataSerializer, self).create(validated_data)

    sensor_name = serializers.CharField(source="sensor.name", read_only=True)

    class Meta:
        """Contains metadata for the DRF `SensorData` serializer class."""
        model = SensorData
        fields = ('id', 'datetime', 'sensor_name', 'value', 'sensor', 'state', 'state_changed')
        read_only_fields = ('state', 'state_changed')


class ZoneSerializer(serializers.HyperlinkedModelSerializer):
    """A DRF serializer for `Zone` objects."""
    class Meta:
        """Contains metadata for the DRF `Zone` serializer class."""
        model = Zone
        fields = ('id', 'name', 'notes')