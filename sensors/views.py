from datetime import datetime
from decimal import Decimal
from django.core.urlresolvers import resolve
from django.shortcuts import render
from django.utils.translation import ugettext
from rest_framework import exceptions, mixins, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from sensors.models import Sensor, SensorData, Zone
from sensors.serializers import (
    SensorSerializer, SensorDataSerializer, ZoneSerializer)

def _raise_zone_key_auth_failed():
    """Raise a `AuthenticationFailed` exception for a zone key auth failure."""
    msg = ugettext('Invalid zone key.')
    raise exceptions.AuthenticationFailed(msg)

def _get_zone(request):
    """Get the `Zone` for the key specified in `request`.

    If a `key` value is not specified or a `Zone` with the given `key` cannot be
    found, a DRF `AuthenticationFailed` exception is raised with an appropriate
    message.

    Arguments:
    request -- The request to get the `Zone.key` value from.

    Returns:
    The `Zone` for the key specified in `request`
    """
    zone = None
    if 'key' in request.data:
        key = request.data['key']
        try:
            zone = Zone.objects.get(key=key)
        except Zone.DoesNotExist:
            pass

    if zone is None:
        _raise_zone_key_auth_failed()

    return zone

class SensorViewSet(viewsets.ModelViewSet):
    """Endpoint for `Sensor` management."""
    queryset = Sensor.objects.all().order_by('name')
    serializer_class = SensorSerializer

    def list(self, request):
        """Get a collection of `Sensor` objects.

        Arguments:
        request -- The API request, optionally containing filters.

        Returns:
        A collection of `Sensor` objects filtered according to the data in
        `request`.
        """
        queryset = Sensor.objects
        if 'sensor_ids' in request.GET:
            ids = [int(id) for id in request.GET['sensor_ids'].split(',')]
            queryset = queryset.filter(id__in=ids)

        if 'zone_ids' in request.GET:
            ids = [int(id) for id in request.GET['zone_ids'].split(',')]
            queryset = queryset.filter(zone_id__in=ids)

        if 'order_by' in request.GET:
            queryset = queryset.order_by(request.GET['order_by'])
        else:
            queryset = queryset.order_by('id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SensorSerializer(page,
                many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SensorSerializer(queryset,
            many=True,
            context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """Create a new `Sensor` object for the data in `request`.

        The `state` and `state_last_change_date` values will be set
        automatically.

        The `request.data` collection must contain a `key` value that
        corresponds to the `Zone` to which the `Sensor` belongs. If the `key` is
        missing or invalid, DRF `AuthenticationFailed` exception is raised. The
        `Sensor.zone` value will be set automatically based on this key.

        Arguments:
        request -- The API request containing the data for the new object.

        Returns:
        A new `Sensor` object containing the data from `request`.
        """
        zone = _get_zone(request)
        request.data['zone'] = reverse('zone-detail',
            args=[zone.id],
            request=request)
        
        return super(SensorViewSet, self).create(request)

    def update(self, request, pk=None, partial=False):
        """Update a `Sensor` using the data in `request`.

        The `request.data` collection must contain a `key` value that
        corresponds to the `Zone` to which the `Sensor` belongs. If the `key` is
        missing or invalid, DRF `AuthenticationFailed` exception is raised.

        Note: this method cannot be used to change the `zone` value.

        Arguments:
        request -- The API request containing the data for the updated object.
        pk -- The ID of the object to update.

        Returns:
        The updated `Sensor` object containing the data from `request`.
        """
        zone = _get_zone(request)
        zone_url = reverse('zone-detail', args=[zone.id], request=request)
        if 'zone' in request.data and request.data['zone'] != zone_url:
            _raise_zone_key_auth_failed()
        return super(SensorViewSet, self).update(request, pk=pk, partial=partial)

    def partial_update(self, request, pk=None):
        """Update a `Sensor` using the data in `request`.

        The `request.data` collection must contain a `key` value that
        corresponds to the `Zone` to which the `Sensor` belongs. If the `key` is
        missing or invalid, DRF `AuthenticationFailed` exception is raised.

        Note: this method cannot be used to change the `zone` value.

        Arguments:
        request -- The API request containing the data for the updated object.
        pk -- The ID of the object to update.

        Returns:
        The updated `Sensor` object containing the data from `request`.
        """
        zone = _get_zone(request)
        zone_url = reverse('zone-detail', args=[zone.id], request=request)
        if 'zone' in request.data and request.data['zone'] != zone_url:
            _raise_zone_key_auth_failed()
        return super(SensorViewSet, self).partial_update(request, pk=pk)

    def destroy(self, request, pk=None):
        """Delete a `Sensor`.

        The `request.data` collection must contain a `key` value that
        corresponds to the `Zone` to which the `Sensor` belongs. If the `key` is
        missing or invalid, DRF `AuthenticationFailed` exception is raised.

        Arguments:
        request -- The API request containing the `Zone` `key`.
        pk -- The ID of the object to delete.

        Returns:
        A `Response` indicating whether the object was deleted.
        """
        zone = _get_zone(request)
        sensor = self.get_object()
        if sensor.zone.id != zone.id:
            _raise_zone_key_auth_failed()
        return super(SensorViewSet, self).destroy(request, pk=pk)

class SensorDataViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Endpoint for `SensorData` management"""
    queryset = SensorData.objects.all().order_by('-datetime')
    serializer_class = SensorDataSerializer

    def list(self, request):
        """Get a collection of `SensorData` objects.

        Arguments:
        request -- The API request, optionally containing filters.

        Returns:
        A collection of `SensorData` objects filtered according to the data in
        `request`.
        """
        queryset = SensorData.objects
        if 'sensor_ids' in request.GET:
            ids = [int(id) for id in request.GET['sensor_ids'].split(',')]
            queryset = queryset.filter(sensor_id__in=ids)

        if 'zone_ids' in request.GET:
            ids = [int(id) for id in request.GET['zone_ids'].split(',')]
            queryset = queryset.filter(sensor__zone_id__in=ids)

        if 'start_date' in request.GET:
            start_date = datetime.strptime(request.GET['start_date'],
                '%Y-%m-%dT%H:%M:%S.%fZ')
            queryset = queryset.filter(datetime__gte=start_date)

        if 'end_date' in request.GET:
            end_date = datetime.strptime(request.GET['end_date'],
                '%Y-%m-%dT%H:%M:%S.%fZ')
            queryset = queryset.filter(datetime__lte=end_date)

        if 'min_value' in request.GET:
            print('value gte {}'.format(Decimal(request.GET['min_value'])))
            min_value = Decimal(request.GET['min_value'])
            queryset = queryset.filter(value__gte=min_value)

        if 'max_value' in request.GET:
            print('value lte {}'.format(Decimal(request.GET['max_value'])))
            max_value = Decimal(request.GET['max_value'])
            queryset = queryset.filter(value__lte=max_value)

        if 'order_by' in request.GET:
            queryset = queryset.order_by(request.GET['order_by'])
        else:
            queryset = queryset.order_by('-datetime')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SensorDataSerializer(page,
                many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SensorDataSerializer(queryset,
            many=True,
            context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """Create a new `SensorData` object for the data in `request`.

        The `state` and `state_changed` values will be set automatically based
        on the associated `Sensor`'s values. If necessary, the `Sensor`'s
        `state` and `state_last_change_date` values will be updated accordingly
        too.

        Arguments:
        request -- The API request containing the data for the new object.

        Returns:
        A new `SensorData` object containing the data in `request`.
        """
        sensor_url = request.data['sensor']
        sensor_id = int([x for x in sensor_url.split('/') if x][-1])
        sensor = Sensor.objects.get(pk=sensor_id)
        zone = _get_zone(request)
        if sensor.zone.id != zone.id:
            _raise_zone_key_auth_failed()

        return super(SensorDataViewSet, self).create(request)

class ZoneViewSet(mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """Endpoint for `Zone` management"""
    queryset = Zone.objects.all().order_by('name')
    serializer_class = ZoneSerializer

    def list(self, request):
        """Get a collection of `Zone` objects.

        Arguments:
        request -- The API request, optionally containing filters.

        Returns:
        A collection of `Zone` objects filtered according to the data in
        `request`.
        """
        queryset = Zone.objects
        if 'zone_ids' in request.GET:
            ids = [int(id) for id in request.GET['zone_ids'].split(',')]
            queryset = queryset.filter(id__in=ids)

        if 'sensor_ids' in request.GET:
            # This is probably not the most efficient way to do this. -ajm
            sensor_ids = [int(id) for id in request.GET['sensor_ids'].split(',')]
            sensors = Sensor.objects.filter(id__in=sensor_ids)
            ids = list(set([s.zone.id for s in sensors]))
            queryset = queryset.filter(id__in=ids)

        if 'order_by' in request.GET:
            queryset = queryset.order_by(request.GET['order_by'])
        else:
            queryset = queryset.order_by('id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ZoneSerializer(page,
                many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ZoneSerializer(queryset,
            many=True,
            context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None, partial=False):
        """Update a `Zone` using the data in `request`.

        The `request.data` collection must contain a `key` value that
        corresponds to the `Zone` being updated. If the `key` is missing or
        invalid, DRF `AuthenticationFailed` exception is raised.

        Arguments:
        request -- The API request containing the data for the updated object.
        pk -- The ID of the object to update.

        Returns:
        The updated `Zone` object containing the data from `request`.
        """
        zone = _get_zone(request)
        if 'id' in request.data and request.data['id'] != zone.id:
            _raise_zone_key_auth_failed()
        return super(ZoneViewSet, self).update(request, pk=pk, partial=partial)

    def partial_update(self, request, pk=None):
        """Update a `Zone` using the data in `request`.

        The `request.data` collection must contain a `key` value that
        corresponds to the `Zone` being updated. If the `key` is missing or
        invalid, DRF `AuthenticationFailed` exception is raised.

        Note: this method cannot be used to change the `zone` value.

        Arguments:
        request -- The API request containing the data for the updated object.
        pk -- The ID of the object to update.

        Returns:
        The updated `Zone` object containing the data from `request`.
        """
        zone = _get_zone(request)
        if 'id' in request.data and request.data['id'] != zone.id:
            _raise_zone_key_auth_failed()
        return super(ZoneViewSet, self).partial_update(request, pk=pk)