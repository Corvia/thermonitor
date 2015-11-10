#!/usr/bin/python

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


CMD_EXECUTABLE = "digitemp_DS9097"
CMD_ARGUMENTS = "-a"


# Check that the digitemp executable actually exists, quit if it is not installed.
if not distutils.spawn.find_executable(CMD_EXECUTABLE):
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

	# TODO - Hooray! At this point we'll ship the data to the API.

