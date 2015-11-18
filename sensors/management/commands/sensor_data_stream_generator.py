#!/usr/bin/python

from notifications.models import SensorAlertGroup
from sensors.models import Zone, Sensor
from django.contrib.auth.models import User
from decimal import Decimal
from uuid import uuid4
import requests
from random import randint
import json
from time import sleep


"""
Quick and dirty script for generating data and sending it to the
local API. 

Creates a Zone, test User, Alert Group, 4 Sensors.
Randomly generates SensorData every 60 seconds and sends it to the
API.

Run via:

$ ./manage.py sensor_data_stream_generator
"""


TEST_ZONE_NAME = "Streaming Test Data Zone"
TEST_ALERT_GROUP_NAME = "Streaming Test Alert Group"
TEST_USER_NAME = "test-data-user"
TEST_EMAIL_ADDR = "tester-streamer@example.net"
SLEEP_SECONDS = 60
API_URL = "http://localhost:9000/api/v1/"
API_HEADERS = {'Content-type': 'application/json'}

zone = None
user = None
alert_group = None
sensors = []

# Create zone
try:
    zone = Zone.objects.get(name=TEST_ZONE_NAME)
except Zone.DoesNotExist:
    zone = Zone.objects.create(name=TEST_ZONE_NAME)
# Create alert user
try:
    user = User.objects.get(username=TEST_USER_NAME)
except User.DoesNotExist:
    user = User.objects.create(
        username=TEST_USER_NAME,
        email=TEST_EMAIL_ADDR,
        password=str(uuid4())[:30]
    )
# Create alert group
try:
    alert_group = SensorAlertGroup.objects.get(name=TEST_ALERT_GROUP_NAME)
except SensorAlertGroup.DoesNotExist:
    alert_group = SensorAlertGroup.objects.create(
        name=TEST_ALERT_GROUP_NAME
    )
    alert_group.users.add(user)
# Create sensors
for sensor_count in range(1, 5):
    guid = "TESTSENSOR{0}".format(sensor_count)
    name = "Test Sensor #{0}".format(sensor_count)
    try:
        sensor = Sensor.objects.get(guid=guid)
    except Sensor.DoesNotExist:
        sensor = Sensor.objects.create(
            name=name,
            guid=guid,
            zone=zone
        )
        sensor.alert_groups.add(alert_group)
    sensors.append(sensor)

# Actually run the tests
while True:
    for sensor in sensors:
        data = {
            'guid': sensor.guid,
            'value': round(Decimal(randint(1, 1000)) / Decimal(10), 1),
            'key': zone.key,
        }
        print "SENDING: {0} -- {1}".format(data["guid"], data["value"])
        try:
            response = requests.post(
                API_URL + "data/",
                data=json.dumps(data),
                headers=API_HEADERS,
            )
            print "OK: " + str(response.json())
        except:
            print "FAIL: request failed for some reason or another"
        print "---"
    sleep(SLEEP_SECONDS)
