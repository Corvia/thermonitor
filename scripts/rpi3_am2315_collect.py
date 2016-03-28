#!/usr/bin/python

"""
Thermonitor API client for AOSONG AM2315 Temp/Humidity Sensor on an RPI 3

Setup:

*Connect sensor clock/data lines to RPI 3 I2C clock data lines and add a 10K
pullup resistor to VCC on both SDA/SDC 

sudo-apt get install Python3
sudo-apt get install python3-setuptools
sudo apt-get install python-smbus

Install Quick2Wire:
git clone https://github.com/quick2wire/quick2wire-python-api.git 
cd quick2wire-python-api
sudo python3 setup.py install

Install AM2315 Python API:
git clone https://code.google.com/p/am2315-python-api/
cd am2315-python-api
sudo python3 setup.py

Enable I2C using 'rasps-config' tool

Sym link /dev/i2c-0 to /dev/i2c-1 
Edit /etc/rc.local and add the following line: 'ln /dev/i2c-1 /dev/i2c-0'

---

0. Copy this script to the device you will be running it on.
1. Change the API_ZONE_KEY and API_URL below. Zone key will be
   set in the django admin after you create the zone.
2. Setup cron to run the script as often as you'd like
   to report the temperatures. Something like:

*/15 * * * * /usr/bin/python3 /path/to/termonitor_collect.py >/dev/null 2>&1

"""

API_ZONE_KEY = "ZONEKEY" 
API_URL =  "http://localhost:9000/api/v1/"
API_HEADERS = {'Content-type': 'application/json'}
API_TIMEOUT = 4.0  # Time out API requests after this many seconds
API_TEMP_SERIAL = "AM2315TEMP1"
API_RH_SERIAL = "AM2315HUM1"

import json
import requests
from AM2315 import AM2315

def send_sensor_data_to_api(serial, value):
    data = {
        'guid': serial,
        'value': value,
        'key': API_ZONE_KEY,
    }

    try:
        response = requests.post(
            API_URL + "data/",
            data=json.dumps(data),
            headers=API_HEADERS,
            timeout=API_TIMEOUT,
        )
        print (response.json())
    except:
        # In the event of a timeout, just try the next set of data. Hopefully it will
        # eventually come back. If we want to get more complex with timeout handling, here's
        # the documentation for it. I don't think it's really necessary at this point.
        # http://docs.python-requests.org/en/latest/user/quickstart/#timeouts
        pass
    

sensor = AM2315()

temperature = round(sensor.temperature() * 9/5 + 23, 1) #Convert to F
humidity = round(sensor.humidity(), 1)

print ("OK:\tID: %s\tTemp: %s\tRH: %s" % (API_TEMP_SERIAL, temperature, humidity))

send_sensor_data_to_api(API_TEMP_SERIAL, temperature)
send_sensor_data_to_api(API_RH_SERIAL, humidity)


