"""Contains functions for testing the functionality of the Notifications API."""

import json
import pytest
import re
import requests
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import Group, User
from notifications.models import SensorAlert, SensorAlertGroup
from sensors.models import Sensor, SensorData, Zone
from django.core import mail
from uuid import uuid4

class TestSensorsApi(object):
    user = None
    alert_group = None
    zone = None
    sensor = None
    data = None
    alerts = None

    @pytest.fixture(autouse=True)
    def api_root(self, request, live_server):
        api_root = '{}{}api/v1/'.format(
            live_server.url,
            '/' if not live_server.url.endswith('/') else '')
        return api_root

    @pytest.fixture(autouse=True)
    def create_data(self, request):
        def finalizer():
            if self.alerts is not None:
                for alert in self.alerts:
                    alert.delete()
                self.alerts = None

            if self.data is not None:
                for data in self.data:
                    data.delete()
                self.data = None

            if self.sensor is not None:
                self.sensor.delete()
                self.sensor = None

            if self.zone is not None:
                self.zone.delete()
                self.zone = None

            if self.alert_group is not None:
                self.alert_group.delete()
                self.alert_group = None

            if self.user is not None:
                self.user.delete()

        username = str(uuid4())[:30]
        self.user = User(username=username,
            email='{}@example.net'.format(username))
        self.user.save()

        self.alert_group = SensorAlertGroup(name='Test Group')
        self.alert_group.save()
        self.alert_group.users.add(self.user)

        self.zone = Zone(name='Test Zone',
            notes='Zone notes.',
            key=uuid4())
        self.zone.save()

        self.sensor = Sensor(guid=uuid4(),
            name='Test Sensor',
            notes='Sensor notes.',
            zone = self.zone,
            min_value=60,
            max_value=85,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        self.sensor.save()
        self.sensor.alert_groups.add(self.alert_group)

        self.data = []

        # Inbox is empty
        assert 0 == len(mail.outbox)

        # Create in-range data point; no notification.
        datum = SensorData(sensor=self.sensor,
            datetime=datetime.utcnow(),
            value=self.sensor.min_value + 1,
            state=True,
            state_changed=False)
        datum.save()
        self.data.append(datum)

        # Inbox still empty
        assert 0 == len(mail.outbox)

        # Create out-of-range notification; sends "alert."
        datum = SensorData(sensor=self.sensor,
            datetime=datetime.utcnow(),
            value=self.sensor.min_value - 1,
            state=True,
            state_changed=False)
        datum.save()
        self.data.append(datum)

        # Inbox received alert
        assert 1 == len(mail.outbox)

        # Create another in-range data point; sends "recovered."
        datum = SensorData(sensor=self.sensor,
            datetime=datetime.utcnow(),
            value=self.sensor.min_value + 1,
            state=True,
            state_changed=False)
        datum.save()
        self.data.append(datum)

        # Inbox received recovery email
        assert 2 == len(mail.outbox)

        self.alerts = SensorAlert.objects.all().order_by('id')

        request.addfinalizer(finalizer)

    def _compare_sensor_alert_json(self, alert, alert_json):
        assert alert.id == alert_json['id']
        assert alert.alert_type == alert_json['alert_type']
        assert alert.alert_class == alert_json['alert_class']
        assert alert.recipients == alert_json['recipients']
        assert alert.message == alert_json['message']
        assert alert.date.strftime('%Y-%m-%dT%H:%M:%S.%f') == alert_json['date'][:26]

        m = re.match(r'.*sensors/([0-9]+)/?', alert_json['sensor'])
        assert m is not None
        assert alert.sensor.id == int(m.group(1))

        m = re.match(r'.*data/([0-9]+)/?', alert_json['data_point'])
        assert m is not None
        assert alert.data_point.id == int(m.group(1))

    def test_alerts_list_no_filters(self, api_root):
        response = requests.get(api_root + 'alerts/?format=json')
        data = response.json()
        assert len(data) > 1

        for alert in self.alerts:
            alert_json = [x for x in data if int(x['id']) == alert.id][0]
            self._compare_sensor_alert_json(alert, alert_json)

    def test_alerts_list_get_with_limit_and_offset(self, api_root):
        response = requests.get(api_root + 'alerts/?limit=10&offset=0&format=json')
        data = response.json()
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data

    def test_alerts_list_get_with_alert_filter(self, api_root):
        included_alert = self.alerts[0]
        excluded_alert = self.alerts[1]

        suffix = 'alerts/?alert_ids={}&format=json'.format(included_alert.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_alert_json = [x for x in data if int(x['id']) == excluded_alert.id]
        assert len(excluded_alert_json) == 0

        included_alert_json = [x for x in data if int(x['id']) == included_alert.id][0]
        self._compare_sensor_alert_json(included_alert, included_alert_json)

    def test_alerts_list_get_with_zone_filters(self, api_root):
        alert = self.alerts[0]
        # Ensure this alert is *not* included if its zone isn't specified.
        suffix = 'alerts/?zone_ids={}&format=json'.format(alert.sensor.zone.id + 1)
        response = requests.get(api_root + suffix)
        data = response.json()

        alerts_json = [x for x in data if int(x['id']) == alert.id]
        assert len(alerts_json) == 0

        # Ensure this alert *is* included if its zone is specified.
        suffix = 'alerts/?zone_ids={}&format=json'.format(alert.sensor.zone.id)
        response = requests.get(api_root + suffix)
        data = response.json()

        alert_json = [x for x in data if int(x['id']) == alert.id][0]
        self._compare_sensor_alert_json(alert, alert_json)

    def test_alerts_list_get_with_sensor_filters(self, api_root):
        alert = self.alerts[0]
        # Ensure this alert is *not* included if its zone isn't specified.
        suffix = 'alerts/?sensor_ids={}&format=json'.format(alert.sensor.id + 1)
        response = requests.get(api_root + suffix)
        data = response.json()

        alerts_json = [x for x in data if int(x['id']) == alert.id]
        assert len(alerts_json) == 0

        # Ensure this alert *is* included if its zone is specified.
        suffix = 'alerts/?sensor_ids={}&format=json'.format(alert.sensor.id)
        response = requests.get(api_root + suffix)
        data = response.json()

        alert_json = [x for x in data if int(x['id']) == alert.id][0]
        self._compare_sensor_alert_json(alert, alert_json)

    def test_alerts_list_get_with_order_by(self, api_root):
        response = requests.get(api_root + 'alerts/?order_by=-id&format=json')
        data = response.json()
        assert len(data) > 1
        assert int(data[0]['id']) == self.alerts[1].id
        assert int(data[1]['id']) == self.alerts[0].id

    def test_alerts_list_post(self, api_root):
        response = requests.post(api_root + 'alerts/?format=json')
        assert response.status_code == 405

    def test_alerts_list_patch(self, api_root):
        response = requests.patch(api_root + 'alerts/?format=json')
        assert response.status_code == 405

    def test_alerts_list_delete(self, api_root):
        response = requests.delete(api_root + 'alerts/?format=json')
        assert response.status_code == 405

    def test_alerts_detail_get(self, api_root):
        alert = self.alerts[0]
        suffix = 'alerts/{}/?format=json'.format(alert.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        self._compare_sensor_alert_json(alert, data)

    def test_alerts_detail_post(self, api_root):
        alert = self.alerts[0]
        suffix = 'alerts/{0}/?format=json'.format(alert.id)
        response = requests.post(api_root + suffix)
        assert response.status_code == 405

    def test_alerts_detail_patch(self, api_root):
        alert = self.alerts[0]
        suffix = 'alerts/{0}/?format=json'.format(alert.id)
        response = requests.patch(api_root +suffix)
        assert response.status_code == 405

    def test_alerts_detail_delete(self, api_root):
        alert = self.alerts[0]
        suffix = 'alerts/{0}/?format=json'.format(alert.id)
        response = requests.delete(api_root + suffix)
        assert response.status_code == 405