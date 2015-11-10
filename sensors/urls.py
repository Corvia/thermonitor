"""Contains values and functions for managing the Sensors app's URLs."""

from sensors import views

def register_api_routes(router):
    """Register this application's API routes with the given `router`.

    Arguments:
    router -- The DRF router with which this applications API routes will be
        registered.
    """
    router.register(r'data', views.SensorDataViewSet)
    router.register(r'sensors', views.SensorViewSet)
    router.register(r'zones', views.ZoneViewSet)
