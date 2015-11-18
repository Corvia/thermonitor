from rest_framework import mixins, viewsets
from rest_framework.response import Response
from notifications.models import SensorAlert
from notifications.serializers import SensorAlertSerializer


class SensorAlertViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """Endpoint for read-only `SensorAlert` data access."""
    queryset = SensorAlert.objects.all()
    serializer_class = SensorAlertSerializer

    def list(self, request):
        """Get a collection of `SensorAlert` objects.

        Arguments:
        request -- The API request, optionally containing filters.

        Returns:
        A collection of `SensorAlert` objects filtered according to the data in
        `request`.
        """
        queryset = SensorAlert.objects
        if 'alert_ids' in request.GET:
            ids = [int(id) for id in request.GET['alert_ids'].split(',')]
            queryset = queryset.filter(id__in=ids)

        if 'sensor_ids' in request.GET:
            ids = [int(id) for id in request.GET['sensor_ids'].split(',')]
            queryset = queryset.filter(sensor_id__in=ids)

        if 'zone_ids' in request.GET:
            ids = [int(id) for id in request.GET['zone_ids'].split(',')]
            queryset = queryset.filter(sensor__zone__id__in=ids)

        if 'order_by' in request.GET:
            queryset = queryset.order_by(request.GET['order_by'])
        else:
            queryset = queryset.order_by('-date')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SensorAlertSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SensorAlertSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
