"""Contains functions for testing the functionality of the Sensors API."""

# Initialize Django
# http://stackoverflow.com/a/11158224
import inspect, os, sys
cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(cwd)
sys.path.insert(0, parentdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djthermonitor.settings")
from django.core.management import execute_from_command_line
execute_from_command_line([''])
# End Django initialization

import json
import pytest
import re
import requests
from datetime import datetime
from decimal import Decimal
from sensors.models import Sensor, SensorData, Zone
from uuid import uuid4

class TestSensorsApi(object):
    zone = None
    sensor = None
    data = None

    @pytest.fixture(autouse=True)
    def api_root(self, request):
        server = pytest.config.getoption('--server')
        api_root = '{}{}api/v1/'.format(
            server,
            '/' if not server.endswith('/') else '')
        return api_root

    @pytest.fixture(autouse=True)
    def create_data(self, request):
        def finalizer():
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

        self.zone = Zone(name='Test Zone',
            notes='Zone notes.',
            key=uuid4())
        self.zone.save()

        self.sensor = Sensor(guid=uuid4(),
            name='Test Sensor',
            notes='Sensor notes.',
            zone = self.zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        self.sensor.save()

        self.data = []
        for i in range(3):
            datum = SensorData(sensor=self.sensor,
                datetime=datetime.utcnow(),
                value=self.sensor.min_value + i,
                state=True,
                state_changed=False)
            datum.save()
            self.data.append(datum)

        request.addfinalizer(finalizer)

    def _compare_zone_json(self, zone, zone_json):
        assert zone.id == zone_json['id']
        assert zone.name == zone_json['name']
        assert zone.notes == zone_json['notes']

    def _compare_sensor_json(self, sensor, sensor_json):
        assert sensor.id == sensor_json['id']
        assert str(sensor.guid) == sensor_json['guid']
        assert sensor.name == sensor_json['name']
        assert sensor.notes == sensor_json['notes']
        assert sensor.min_value == Decimal(sensor_json['min_value'])
        assert sensor.max_value == Decimal(sensor_json['max_value'])
        assert sensor.min_value_operator == sensor_json['min_value_operator']
        assert sensor.max_value_operator == sensor_json['max_value_operator']
        assert sensor.state == sensor_json['state']
        assert sensor.state_last_change_date.strftime('%Y-%m-%dT%H:%M:%S.%f') == \
            sensor_json['state_last_change_date'][:26]

        m = re.match(r'.*zones/([0-9]+)/?', sensor_json['zone'])
        assert m is not None
        assert sensor.zone.id == int(m.group(1))

    def _compare_sensor_data_json(self, sensor_data, sensor_data_json):
        assert sensor_data.datetime.strftime('%Y-%m-%dT%H:%M:%S.%f') == \
            sensor_data_json['datetime'][:26]
        assert sensor_data.value == Decimal(sensor_data_json['value'])
        assert sensor_data.state == sensor_data_json['state']
        assert sensor_data.state_changed == sensor_data_json['state_changed']

        m = re.match(r'.*sensors/([0-9]+)/?', sensor_data_json['sensor'])
        assert m is not None
        assert sensor_data.sensor.id == int(m.group(1))

    def test_api_root_get(self, api_root):
        response = requests.get(api_root)
        data = response.json()
        assert 'data' in data
        assert 'sensors' in data
        assert 'zones' in data

    def test_api_root_post(self, api_root):
        response = requests.post(api_root)
        assert response.status_code == 405

    def test_api_root_put(self, api_root):
        response = requests.put(api_root)
        assert response.status_code == 405

    def test_api_root_patch(self, api_root):
        response = requests.patch(api_root)
        assert response.status_code == 405

    def test_api_root_delete(self, api_root):
        response = requests.delete(api_root)
        assert response.status_code == 405

    def test_sensors_list_get_no_filters(self, api_root):
        response = requests.get(api_root + 'sensors/?format=json')
        data = response.json()
        assert len(data) > 0
        sensor_json = [x for x in data if x['guid'] == str(self.sensor.guid)][0]
        self._compare_sensor_json(self.sensor, sensor_json)

    def test_sensors_list_get_with_limit_and_offset(self, api_root):
        response = requests.get(api_root + 'sensors/?limit=10&offset=0&format=json')
        data = response.json()
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data
        # It's more work than it's worth to check that we can find self.sensor
        # in this test--there's no telling how many pages would have to be
        # checked, and the json is already being checked elsewhere anyway. -ajm

    def test_sensors_list_get_with_sensor_filter(self, api_root):
        excluded_sensor = Sensor(guid=uuid4(),
            name='Test Sensor Excluded',
            notes='Sensor notes.',
            zone = self.zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        excluded_sensor.save()

        suffix = 'sensors/?sensor_ids={}&format=json'.format(self.sensor.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_sensor_json = [x for x in data if x['guid'] == str(excluded_sensor.guid)]
        assert len(excluded_sensor_json) == 0

        excluded_sensor.delete()

        sensor_json = [x for x in data if x['guid'] == str(self.sensor.guid)][0]
        self._compare_sensor_json(self.sensor, sensor_json)

    def test_sensors_list_get_with_zone_filter(self, api_root):
        excluded_zone = Zone(name='Test Zone Excluded',
            notes='Zone notes.',
            key=uuid4())
        excluded_zone.save()

        excluded_sensor = Sensor(guid=uuid4(),
            name='Test Sensor Excluded',
            notes='Sensor notes.',
            zone = excluded_zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        excluded_sensor.save()

        suffix = 'sensors/?zone_ids={}&format=json'.format(self.sensor.zone.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_sensor_json = [x for x in data if x['guid'] == str(excluded_sensor.guid)]
        assert len(excluded_sensor_json) == 0

        excluded_sensor.delete()
        excluded_zone.delete()

        sensor_json = [x for x in data if x['guid'] == str(self.sensor.guid)][0]
        self._compare_sensor_json(self.sensor, sensor_json)

    def test_sensors_list_get_with_order_by(self, api_root):
        second_sensor = Sensor(guid=uuid4(),
            name=self.sensor.name + '_', # Just something to make it sort lower
            notes='Sensor notes.',
            zone = self.zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        second_sensor.save()

        # Sort by name, ascending
        response = requests.get(api_root + 'sensors/?order_by=name&format=json')
        data = response.json()
        assert len(data) > 1

        first_guid = str(self.sensor.guid)
        second_guid = str(second_sensor.guid)
        matches = [x for x in data if (
            x['guid'] == first_guid or x['guid'] == second_guid)]
        assert matches[0]['name'] == self.sensor.name
        assert matches[1]['name'] == second_sensor.name

        # Sort by name, descending
        response = requests.get(api_root + 'sensors/?order_by=-name&format=json')
        data = response.json()
        assert len(data) > 1

        matches = [x for x in data if (
            x['guid'] == first_guid or x['guid'] == second_guid)]
        assert matches[0]['name'] == second_sensor.name
        assert matches[1]['name'] == self.sensor.name

        # Default sorting (id)
        response = requests.get(api_root + 'sensors/?format=json')
        data = response.json()
        assert len(data) > 1

        matches = [x for x in data if (
            x['guid'] == first_guid or x['guid'] == second_guid)]
        assert matches[0]['name'] == self.sensor.name
        assert matches[1]['name'] == second_sensor.name

    def test_sensors_list_post(self, api_root):
        sensor_dict = {
            'guid': str(uuid4()),
            'name': 'POST Sensor',
            'notes': 'POST notes.',
            'min_value': 20,
            'max_value': 25,
            'min_value_operator': '>=',
            'max_value_operator': '<=',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'sensors/',
            data=json.dumps(sensor_dict),
            headers=headers)

        data = response.json()

        assert 'id' in data
        id = int(data['id'])
        assert id > 0

        sensor = Sensor.objects.get(id=id)
        self._compare_sensor_json(sensor, data)

        sensor.delete()

    def test_sensors_list_post_with_invalid_data(self, api_root):
        sensor_dict = {
            'guid': None,
            'name': None,
            'notes': 'POST notes.',
            'min_value': 20,
            'max_value': 25,
            'min_value_operator': '>=',
            'max_value_operator': '<=',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'sensors/',
            data=json.dumps(sensor_dict),
            headers=headers)

        # Attempt to remove the object if it's erroneously created.
        try:
            data = response.json()
            if 'id' in data:
                Sensor.objects.get(id=int(data['id'])).delete()
        except:
            pass

        assert response.status_code == 400

    def test_sensors_list_post_without_zone_key(self, api_root):
        sensor_dict = {
            'guid': str(uuid4()),
            'name': 'POST Sensor',
            'notes': 'POST notes.',
            'min_value': 20,
            'max_value': 25,
            'min_value_operator': '>=',
            'max_value_operator': '<='
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'sensors/',
            data=json.dumps(sensor_dict),
            headers=headers)

        # Attempt to remove the object if it's erroneously created.
        try:
            data = response.json()
            if 'id' in data:
                Sensor.objects.get(id=int(data['id'])).delete()
        except:
            pass

        assert response.status_code == 403

    def test_sensors_list_put(self, api_root):
        response = requests.put(api_root + 'sensors/')
        assert response.status_code == 405

    def test_sensors_list_patch(self, api_root):
        response = requests.patch(api_root + 'sensors/')
        assert response.status_code == 405

    def test_sensors_list_delete(self, api_root):
        response = requests.delete(api_root + 'sensors/')
        assert response.status_code == 405

    def test_sensors_detail_get(self, api_root):
        suffix = 'sensors/{}/?format=json'.format(self.sensor.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        self._compare_sensor_json(self.sensor, data)

    def test_sensors_detail_post(self, api_root):
        suffix = 'sensors/{}/?format=json'.format(self.sensor.id)
        response = requests.post(api_root + suffix)
        assert response.status_code == 405

    def test_sensors_detail_put(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        sensor_dict = {
            'guid': str(uuid4()),
            'name': 'PUT Sensor',
            'notes': 'PUT notes.',
            'zone': api_root + 'zones/{}/'.format(self.zone.id),
            'min_value': 200,
            'max_value': 250,
            'min_value_operator': '<=',
            'max_value_operator': '>=',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.put(api_root + suffix,
            data=json.dumps(sensor_dict),
            headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data['guid'] == sensor_dict['guid']
        assert data['name'] == sensor_dict['name']
        assert data['notes'] == sensor_dict['notes']
        assert data['zone'] == sensor_dict['zone']
        assert Decimal(data['min_value']) == Decimal(sensor_dict['min_value'])
        assert Decimal(data['max_value']) == Decimal(sensor_dict['max_value'])
        assert data['min_value_operator'] == sensor_dict['min_value_operator']
        assert data['max_value_operator'] == sensor_dict['max_value_operator']

    def test_sensors_detail_put_without_zone_key(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        sensor_dict = {
            'guid': str(uuid4()),
            'name': 'PUT Sensor',
            'notes': 'PUT notes.',
            'zone': api_root + 'zones/{}/'.format(self.zone.id),
            'min_value': 200,
            'max_value': 250,
            'min_value_operator': '<=',
            'max_value_operator': '>='
        }
        headers = {'Content-type': 'application/json'}
        response = requests.put(api_root + suffix,
            data=json.dumps(sensor_dict),
            headers=headers)

        assert response.status_code == 403

    def test_sensors_detail_put_with_invalid_data(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        sensor_dict = {
            'guid': None,
            'name': None,
            'notes': 'PUT notes.',
            'zone': api_root + 'zones/{}/'.format(self.zone.id),
            'min_value': 200,
            'max_value': 250,
            'min_value_operator': '<=',
            'max_value_operator': '>=',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.put(api_root + suffix,
            data=json.dumps(sensor_dict),
            headers=headers)

        assert response.status_code == 400

    def test_sensors_detail_patch(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        sensor_dict = {
            'guid': str(self.sensor.guid),
            'name': 'PATCH Sensor',
            'notes': 'PATCH notes.',
            'min_value': self.sensor.min_value,
            'max_value': self.sensor.max_value,
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.patch(api_root + suffix,
            data=json.dumps(sensor_dict),
            headers=headers)

        print(response.text)
        assert response.status_code == 200
        data = response.json()

        assert data['guid'] == sensor_dict['guid']
        assert data['name'] == sensor_dict['name']
        assert data['notes'] == sensor_dict['notes']
        assert Decimal(data['min_value']) == Decimal(sensor_dict['min_value'])
        assert Decimal(data['max_value']) == Decimal(sensor_dict['max_value'])

    def test_sensors_detail_patch_without_zone_key(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        sensor_dict = {
            'guid': str(self.sensor.guid),
            'name': 'PATCH Sensor',
            'notes': 'PATCH notes.',
            'min_value': self.sensor.min_value,
            'max_value': self.sensor.max_value
        }
        headers = {'Content-type': 'application/json'}
        response = requests.patch(api_root + suffix,
            data=json.dumps(sensor_dict),
            headers=headers)

        assert response.status_code == 403

    def test_sensors_detail_patch_with_invalid_data(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        sensor_dict = {
            'guid': None,
            'name': None,
            'notes': 'PATCH notes.',
            'min_value': None,
            'max_value': None,
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.patch(api_root + suffix,
            data=json.dumps(sensor_dict),
            headers=headers)

        print(response.text)
        assert response.status_code == 400

    def test_sensors_detail_delete(self, api_root):
        data = {'key': str(self.zone.key)}
        headers = {'Content-type': 'application/json'}
        suffix = 'sensors/{}/'.format(self.sensor.id)
        response = requests.delete(api_root + suffix,
            data=json.dumps(data),
            headers=headers)
        assert response.status_code == 204

    def test_sensors_detail_delete_without_zone_key(self, api_root):
        suffix = 'sensors/{}/'.format(self.sensor.id)
        response = requests.delete(api_root + suffix)
        assert response.status_code == 403

    def test_sensor_data_list_get_no_filters(self, api_root):
        response = requests.get(api_root + 'data/?format=json')
        data = response.json()
        assert len(data) > 2

        for i in range(3):
            data_json = [x for x in data if int(x['id']) == self.data[i].id][0]
            self._compare_sensor_data_json(self.data[i], data_json)

    def test_sensor_data_list_get_with_limit_and_offset(self, api_root):
        response = requests.get(api_root + 'data/?limit=10&offset=0&format=json')
        data = response.json()
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data

    def test_sensor_data_list_get_with_sensor_filter(self, api_root):
        excluded_sensor = Sensor(guid=uuid4(),
            name='Test Sensor Excluded',
            notes='Sensor notes.',
            zone = self.zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        excluded_sensor.save()

        excluded_data = SensorData(sensor=excluded_sensor,
            datetime=datetime.utcnow(),
            value=22,
            state=True,
            state_changed=False)
        excluded_data.save()

        suffix = 'data/?sensor_ids={}&format=json'.format(self.sensor.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_data_json = [x for x in data if x['id'] == str(excluded_data.id)]
        assert len(excluded_data_json) == 0

        excluded_data.delete()
        excluded_sensor.delete()

        for i in range(3):
            data_json = [x for x in data if int(x['id']) == self.data[i].id][0]
            self._compare_sensor_data_json(self.data[i], data_json)

    def test_sensor_data_list_get_with_zone_filter(self, api_root):
        excluded_zone = Zone(name='Test Zone Excluded',
            notes='Zone notes.',
            key=uuid4())
        excluded_zone.save()

        excluded_sensor = Sensor(guid=uuid4(),
            name='Test Sensor Excluded',
            notes='Sensor notes.',
            zone = excluded_zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        excluded_sensor.save()

        excluded_data = SensorData(sensor=excluded_sensor,
            datetime=datetime.utcnow(),
            value=22,
            state=True,
            state_changed=False)
        excluded_data.save()

        suffix = 'data/?zone_ids={}&format=json'.format(self.zone.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_data_json = [x for x in data if x['id'] == str(excluded_data.id)]
        assert len(excluded_data_json) == 0

        excluded_data.delete()
        excluded_sensor.delete()
        excluded_zone.delete()

        for i in range(3):
            data_json = [x for x in data if int(x['id']) == self.data[i].id][0]
            self._compare_sensor_data_json(self.data[i], data_json)

    def test_sensor_data_list_get_with_date_filters(self, api_root):
        suffix = 'data/?start_date={}&end_date={}&format=json'.format(
            self.data[0].datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            self.data[0].datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_data_json = [x for x in data if x['id'] == str(self.data[1].id)]
        assert len(excluded_data_json) == 0

        data_json = [x for x in data if int(x['id']) == self.data[0].id][0]
        self._compare_sensor_data_json(self.data[0], data_json)

    def test_sensor_data_list_get_with_value_filters(self, api_root):
        suffix = 'data/?min_value={}&max_value={}&format=json'.format(
            self.data[0].value,
            self.data[0].value)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_data_json = [x for x in data if x['id'] == str(self.data[1].id)]
        assert len(excluded_data_json) == 0

        data_json = [x for x in data if int(x['id']) == self.data[0].id][0]
        self._compare_sensor_data_json(self.data[0], data_json)

    def test_sensor_data_list_post(self, api_root):
        data_dict = {
            'sensor': api_root + 'sensors/{}/'.format(self.sensor.id),
            'datetime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'value': 22.5,
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'data/',
            data=json.dumps(data_dict),
            headers=headers)

        data = response.json()

        assert 'id' in data
        id = int(data['id'])
        assert id > 0

        sensor_data = SensorData.objects.get(id=id)
        self._compare_sensor_data_json(sensor_data, data)

        sensor_data.delete()

    def test_sensor_data_list_post_without_zone_key(self, api_root):
        data_dict = {
            'sensor': api_root + 'sensors/{}/'.format(self.sensor.id),
            'datetime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'value': 22.5
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'data/',
            data=json.dumps(data_dict),
            headers=headers)

        assert response.status_code == 403

    def test_sensor_data_list_post_in_range_maintains_state(self, api_root):
        prev_state_last_change_date = self.sensor.state_last_change_date

        data_dict = {
            'sensor': api_root + 'sensors/{}/'.format(self.sensor.id),
            'datetime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'value': 22.5,
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'data/',
            data=json.dumps(data_dict),
            headers=headers)

        data = response.json()

        assert 'id' in data
        id = int(data['id'])
        assert id > 0

        sensor_data = SensorData.objects.get(id=id)
        self._compare_sensor_data_json(sensor_data, data)

        sensor = Sensor.objects.get(pk=self.sensor.id)
        assert sensor.state == True
        assert sensor.state_last_change_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') == \
            prev_state_last_change_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        sensor_data.delete()

    def test_sensor_data_list_post_outside_range_updates_state(self, api_root):
        prev_state = self.sensor.state
        prev_state_last_change_date = self.sensor.state_last_change_date

        data_dict = {
            'sensor': api_root + 'sensors/{}/'.format(self.sensor.id),
            'datetime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'value': self.sensor.max_value + 1,
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(api_root + 'data/',
            data=json.dumps(data_dict),
            headers=headers)

        data = response.json()

        assert 'id' in data
        id = int(data['id'])
        assert id > 0

        sensor_data = SensorData.objects.get(id=id)
        self._compare_sensor_data_json(sensor_data, data)

        sensor = Sensor.objects.get(pk=self.sensor.id)
        assert not sensor.state
        assert sensor.state_last_change_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') != \
            prev_state_last_change_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        sensor_data.delete()

    def test_sensor_data_list_put(self, api_root):
        response = requests.put(api_root + 'data/')
        assert response.status_code == 405

    def test_sensor_data_list_patch(self, api_root):
        response = requests.patch(api_root + 'data/')
        assert response.status_code == 405

    def test_sensor_data_list_delete(self, api_root):
        response = requests.delete(api_root + 'data/')
        assert response.status_code == 405

    def test_sensor_data_detail_get(self, api_root):
        suffix = 'data/{}/?format=json'.format(self.data[0].id)
        response = requests.get(api_root + suffix)
        data = response.json()
        self._compare_sensor_data_json(self.data[0], data)

    def test_sensor_data_detail_post(self, api_root):
        response = requests.post(api_root + 'data/{}/'.format(self.data[0].id))
        assert response.status_code == 405

    def test_sensor_data_detail_put(self, api_root):
        response = requests.put(api_root + 'data/{}/'.format(self.data[0].id))
        assert response.status_code == 405

    def test_sensor_data_detail_patch(self, api_root):
        response = requests.patch(api_root + 'data/{}/'.format(self.data[0].id))
        assert response.status_code == 405

    def test_sensor_data_detail_delete(self, api_root):
        response = requests.delete(api_root + 'data/{}/'.format(self.data[0].id))
        assert response.status_code == 405

    def test_zone_list_get_no_filters(self, api_root):
        response = requests.get(api_root + 'zones/?format=json')
        data = response.json()
        assert len(data) > 0
        zone_json = [x for x in data if int(x['id']) == self.zone.id][0]
        self._compare_zone_json(self.zone, zone_json)

    def test_zone_list_get_with_limit_and_offset(self, api_root):
        response = requests.get(api_root + 'zones/?limit=10&offset=0&format=json')
        data = response.json()
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data

    def test_zone_list_get_with_sensor_filter(self, api_root):
        excluded_zone = Zone(name='Test Zone Excluded',
            notes='Zone notes.',
            key=uuid4())
        excluded_zone.save()

        excluded_sensor = Sensor(guid=uuid4(),
            name='Test Sensor Excluded',
            notes='Sensor notes.',
            zone = excluded_zone,
            min_value=20,
            max_value=25,
            min_value_operator='>=',
            max_value_operator='<=',
            state=True,
            state_last_change_date=datetime.utcnow())
        excluded_sensor.save()

        suffix = 'zones/?sensor_ids={}&format=json'.format(self.sensor.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_zone_json = [x for x in data if x['id'] == str(excluded_zone.id)]
        assert len(excluded_zone_json) == 0

        excluded_sensor.delete()
        excluded_zone.delete()

        zone_json = [x for x in data if int(x['id']) == self.zone.id][0]
        self._compare_zone_json(self.zone, zone_json)

    def test_zone_list_get_with_zone_filter(self, api_root):
        excluded_zone = Zone(name='Test Zone Excluded',
            notes='Zone notes.',
            key=uuid4())
        excluded_zone.save()

        suffix = 'zones/?zone_ids={}&format=json'.format(self.zone.id)
        response = requests.get(api_root + suffix)
        data = response.json()
        assert len(data) > 0

        excluded_zone_json = [x for x in data if x['id'] == str(excluded_zone.id)]
        assert len(excluded_zone_json) == 0

        excluded_zone.delete()

        zone_json = [x for x in data if int(x['id']) == self.zone.id][0]
        self._compare_zone_json(self.zone, zone_json)

    def test_zone_list_post(self, api_root):
        response = requests.put(api_root + 'zones/')
        assert response.status_code == 405

    def test_zone_list_put(self, api_root):
        response = requests.put(api_root + 'zones/')
        assert response.status_code == 405

    def test_zone_list_patch(self, api_root):
        response = requests.patch(api_root + 'zones/')
        assert response.status_code == 405

    def test_zone_list_delete(self, api_root):
        response = requests.delete(api_root + 'zones/')
        assert response.status_code == 405

    def test_zone_detail_get(self, api_root):
        response = requests.get(api_root + 'zones/{}/'.format(self.zone.id))
        data = response.json()
        self._compare_zone_json(self.zone, data)

    def test_zone_detail_post(self, api_root):
        response = requests.post(api_root + 'zones/{}/'.format(self.zone.id))
        assert response.status_code == 405

    def test_zone_detail_put(self, api_root):
        zone_dict = {
            'name': 'PUT Zone',
            'notes': 'PUT notes.',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.put(api_root + 'zones/{}/'.format(self.zone.id),
            data=json.dumps(zone_dict),
            headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data['name'] == zone_dict['name']
        assert data['notes'] == zone_dict['notes']

    def test_zone_detail_put_without_zone_key(self, api_root):
        zone_dict = {
            'name': 'PUT Zone',
            'notes': 'PUT notes.'
        }
        headers = {'Content-type': 'application/json'}
        response = requests.put(api_root + 'zones/{}/'.format(self.zone.id),
            data=json.dumps(zone_dict),
            headers=headers)

        assert response.status_code == 403

    def test_zone_detail_put_with_invalid_data(self, api_root):
        zone_dict = {
            'name': None,
            'notes': 'PUT notes.',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.put(api_root + 'zones/{}/'.format(self.zone.id),
            data=json.dumps(zone_dict),
            headers=headers)

        assert response.status_code == 400

    def test_zone_detail_patch(self, api_root):
        zone_dict = {
            'name': 'PATCH Zone',
            'notes': 'PATCH notes.',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.patch(api_root + 'zones/{}/'.format(self.zone.id),
            data=json.dumps(zone_dict),
            headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data['name'] == zone_dict['name']
        assert data['notes'] == zone_dict['notes']

    def test_zone_detail_patch_without_zone_key(self, api_root):
        zone_dict = {
            'name': 'PATCH Zone',
            'notes': 'PATCH notes.'
        }
        headers = {'Content-type': 'application/json'}
        response = requests.patch(api_root + 'zones/{}/'.format(self.zone.id),
            data=json.dumps(zone_dict),
            headers=headers)

        assert response.status_code == 403

    def test_zone_detail_patch_with_invalid_data(self, api_root):
        zone_dict = {
            'name': None,
            'notes': 'PATCH notes.',
            'key': str(self.zone.key)
        }
        headers = {'Content-type': 'application/json'}
        response = requests.patch(api_root + 'zones/{}/'.format(self.zone.id),
            data=json.dumps(zone_dict),
            headers=headers)

        assert response.status_code == 400

    def test_zone_detail_delete(self, api_root):
        response = requests.delete(api_root + 'zones/{}/'.format(self.zone.id))
        assert response.status_code == 405