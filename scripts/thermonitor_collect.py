#!/usr/bin/python

"""
Thermonitor API client for digitemp DS9097 client.


Testing:

To test the digitemp_DS9097 command without any actual real hardware,
you can set CMD_EXECUTABLE below to "python ./digitemp_ds9097_fake_tester.py"
to emulate some fake data. There's an example line below. See that script in 
the "scripts" directory for more details.


Setup:

---

OpenWRT requires some packages to be installed:

opkg install distribute
opkg install python-openssl

(may have to get the file on another machine, OpenWRT doesn't allow for
    SSL URLs to be used)
wget https://github.com/kennethreitz/requests/tarball/master

tar zxvf requests.tar.gz
python setup.py install

You may also need to create a .digitemp.rc file in /root. The "digitemp -i" command sets
this up, see hh-controller-just.py for his implementation. I just copied the file
from his directory.

Then "crontab -e" and add:
*/15 * * * * cd /root; ./thermonitor_client.py  >/dev/null 2>&1

Here's a sample .digitemprc file:

root@HH-Controller-1:~# cat .digitemprc
TTY /dev/ttyUSB1
READ_TIME 5
LOG_TYPE 0
LOG_FORMAT "%R %F"
CNT_FORMAT "%b %d %H:%M:%S Sensor %s #%n %C"
HUM_FORMAT "%b %d %H:%M:%S Sensor %s C: %.2C F: %.2F H: %h%%"
SENSORS 11
ROM 0 0x28 0x6C 0xE0 0x83 0x05 0x00 0x00 0x1E
ROM 1 0x28 0xCA 0x76 0x82 0x05 0x00 0x00 0x54
ROM 2 0x28 0x7A 0x18 0x83 0x05 0x00 0x00 0x6F
ROM 3 0x28 0x86 0xD4 0x83 0x05 0x00 0x00 0x63
ROM 4 0x28 0x61 0x17 0x83 0x05 0x00 0x00 0xA3
ROM 5 0x28 0xF1 0x7D 0x82 0x05 0x00 0x00 0x31
ROM 6 0x28 0x13 0x8C 0x83 0x05 0x00 0x00 0x92
ROM 7 0x28 0xB3 0x8D 0x82 0x05 0x00 0x00 0x8C
ROM 8 0x28 0xCB 0x7E 0x82 0x05 0x00 0x00 0x5D
ROM 9 0x28 0xE7 0x6F 0x83 0x05 0x00 0x00 0xA8
ROM 10 0x28 0x6F 0xCB 0x82 0x05 0x00 0x00 0x40

----


0. Copy this script to the device you will be running it on.
1. Change the API_ZONE_KEY and API_URL below. Zone key will be set in the django admin
    after you create the zone.
2. Setup cron to run the script as often as you'd like to report the temperatures. Something like:

*/15 * * * * /usr/bin/python /path/to/termonitor_collect.py >/dev/null 2>&1

"""

API_ZONE_KEY = "FDEA9C52EBCA4F6D9B873FFF059F0392"
API_URL = "http://localhost:9000/api/v1/"
API_HEADERS = {'Content-type': 'application/json'}
API_TIMEOUT = 4.0 # Time out API requests after this many seconds

CMD_EXECUTABLE = "digitemp_DS9097"
CMD_ARGUMENTS = "-a"

# Uncomment this line for digitemp fake data generator.
#CMD_EXECUTABLE = "python digitemp_ds9097_fake_tester.py"

"""

Sample results of digitemp command. We're looking for the valid lines
with a hardware address and temperature readout.

    root@controller:# digitemp_DS9097  -a
    DigiTemp v3.5.0 Copyright 1996-2007 by Brian C. Lane
    GNU Public License v2.0 - http://www.digitemp.com
    286CE0830500001E 43.250000
    28CA768205000054 65.862503
    287A18830500006F 45.162498
    CRC Failed. CRC is 63 instead of 0x00
    CRC Failed. CRC is 63 instead of 0x00
    CRC Failed. CRC is 63 instead of 0x00
    28611783050000A3 41.450001
    28F17D8205000031 48.762501
    28138C8305000092 48.312500
    28B38D820500008C 42.012501
    28CB7E820500005D 41.337502
    28E76F83050000A8 65.074997
    286FCB8205000040 63.950001


Sample script run output:

    root@HH-Controller-1:/www# python thermonitor_collect.py
    CRC Failed. CRC is 63 instead of 0x00
    CRC Failed. CRC is 63 instead of 0x00
    CRC Failed. CRC is 63 instead of 0x00
    NOT DATA:  DigiTemp v3.5.0 Copyright 1996-2007 by Brian C. Lane
    NOT DATA:  GNU Public License v2.0 - http://www.digitemp.com
    OK:     ID: 286CE0830500001E    Temp: 45.275002
    OK:     ID: 28CA768205000054    Temp: 72.500000
    OK:     ID: 287A18830500006F    Temp: 49.662498
    OK:     ID: 28611783050000A3    Temp: 42.012501
    OK:     ID: 28F17D8205000031    Temp: 51.012501
    OK:     ID: 28138C8305000092    Temp: 52.474998
    OK:     ID: 28B38D820500008C    Temp: 42.799999
    OK:     ID: 28CB7E820500005D    Temp: 46.625000
    OK:     ID: 28E76F83050000A8    Temp: 69.349998
    OK:     ID: 286FCB8205000040    Temp: 66.087502

"""

import os
import re
import sys
import distutils.spawn
import json
import requests


# Check that the digitemp executable actually exists, quit if it is not installed.
# Also ignore the python test script emulator... it doesn't work with this check.
if not "python" in CMD_EXECUTABLE and not distutils.spawn.find_executable(CMD_EXECUTABLE):
    sys.exit("Unable to locate the '%s' executable. Is it installed or in the path?" % (CMD_EXECUTABLE))


""" 
Regular expression should be resilient enough to match lines with odd data.
ALl of these are... mostly valid:
    28F17D8205000031 -48.762501
    28138C8305000092 48.312500
    28B38D820500008C 42
    28B38D820500008C 0
    28B38D820500008C -0
"""
regex = re.compile("([A-F0-9]{16})\s([-]?\d+(\.\d+)?)")

for line in os.popen("%s %s" % (CMD_EXECUTABLE, CMD_ARGUMENTS)).readlines():
    try:
        (serial, temperature) = regex.match(line).group(1, 2)
    # Any errors here (regex bad matches, mostly), just continue to the next line.
    except:
        print "NOT DATA:\t%s" % (line.rstrip())
        continue

    print "OK:\tID: %s\tTemp: %s" % (serial, temperature)

    data = {
        'guid': serial,
        'value': temperature,
        'key': API_ZONE_KEY,
    }

    try:
        response = requests.post(
            API_URL + "data/", 
            data=json.dumps(data), 
            headers=API_HEADERS, 
            timeout=API_TIMEOUT,
        )
        print response.json()
    except:
        # In the event of a timeout, just try the next set of data. Hopefully it will
        # eventually come back. If we want to get more complex with timeout handling, here's
        # the documentation for it. I don't think it's really necessary at this point.
        # http://docs.python-requests.org/en/latest/user/quickstart/#timeouts
        pass





