"""Contains values and functions for managing the Notification app's URLs."""

from notifications import views

def register_api_routes(router):
    """Register this application's API routes with the given `router`.

    Arguments:
    router -- The DRF router with which this applications API routes will be
        registered.
    """
    router.register(r'alerts', views.SensorAlertViewSet)
