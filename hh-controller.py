#!/usr/bin/python

# Script imports
import select   # select operation
import socket   # socket operations
import time     # sleep function
import serial   # to control relay UARTs

import glob     # imports for uart serial to device mappings
import os
import re

import string

# Hard coded serial IDs for each UART
OUTLET_UART_SERIAL = 'A7036NID'
PUMP_UART_SERIAL = 'A603VAPG'
TEMP_UART_SERIAL = 'A603V87S'

# Dallas DS18B20 Temp Sensor Hardware addresses
TEMP_EAST_1_ADDR = '286CE0830500001E' 
TEMP_EAST_2_ADDR = '287A18830500006F' 
TEMP_EAST_3_ADDR = '2886D48305000063' 
TEMP_MID_EAST_1_ADDR = '286FCB8205000040' 
TEMP_MID_EAST_2_ADDR = '28F17D8205000031'
TEMP_MID_EAST_3_ADDR = '28138C8305000092'
TEMP_MID_WEST_1_ADDR = '28CA768205000054'
TEMP_MID_WEST_2_ADDR = '28E76F83050000A8'
TEMP_MID_WEST_3_ADDR = '28ECDABC0500001F'
TEMP_WEST_1_ADDR = '28B38D820500008C'
TEMP_WEST_2_ADDR = '28611783050000A3'
TEMP_WEST_3_ADDR = '28CB7E820500005D'

# Temperature Probe Aliases
TEMP_TABLE_1_ADDR = TEMP_EAST_1_ADDR
TEMP_TABLE_2_ADDR = TEMP_MID_EAST_1_ADDR
TEMP_TABLE_3_ADDR = TEMP_MID_WEST_1_ADDR
TEMP_TABLE_4_ADDR = TEMP_WEST_1_ADDR
TEMP_TABLE_5_ADDR = TEMP_EAST_2_ADDR
TEMP_TABLE_6_ADDR = TEMP_MID_EAST_2_ADDR
TEMP_TABLE_7_ADDR = TEMP_MID_WEST_2_ADDR
TEMP_TABLE_8_ADDR = TEMP_WEST_2_ADDR
TEMP_TABLE_9_ADDR = TEMP_EAST_3_ADDR
TEMP_TABLE_10_ADDR = TEMP_MID_EAST_3_ADDR
TEMP_AMBIENT_ADDR = TEMP_MID_WEST_3_ADDR
TEMP_SOIL_ADDR = TEMP_WEST_3_ADDR

# Current State Vars
table_1_temp = 0
table_2_temp = 0
table_3_temp = 0
table_4_temp = 0
table_5_temp = 0
table_6_temp = 0
table_7_temp = 0
table_8_temp = 0
table_9_temp = 0
table_10_temp = 0
table_avg_temp = 0
ambient_temp = 0
soil_temp = 0
outlet_relay_state = True
pump_relay_state = False

# Configuration Vars
table_temp_target = 50      # desired table temperature
table_temp_delta = 1 	    # degrees +/- target temperature
update_time = 900             # 5 second delay between temperature readings

# We will populate these device names with the correct mappings to /dev/ttyUSB{0-2}
# during initialization by looking up their hardware serial ids
OUTLET_DEV = '' 
PUMP_DEV = ''
TEMP_DEV = ''

def process_request(data):
    print data

# Serial device, and On ( True) or Off ( False ) 
def toggle_relay(uart, state):
    global outlet_relay_state
    global pump_relay_state
    dtr = not state #Invert boolean value so DTR properly reflects the expected state 
    uart.setDTR(dtr)
    ts = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print (ts),
    if (uart == ser_outlet):
        outlet_relay_state = state
        print "Changing outlet relay state to: " + str(outlet_relay_state)
    if (uart == ser_pump):
        pump_relay_state = state
        print "Changing pump relay state to: " + str(pump_relay_state)

def init_temps(device_name):
    cmd = "digitemp_DS9097 -i -s " + device_name + " -r 5 -q -o\"%R %F\""
    for outline in os.popen(cmd).readlines():
        outline = outline[:-1];
        print outline

def update_temps():
    global table_1_temp
    global table_2_temp
    global table_3_temp
    global table_4_temp
    global table_5_temp
    global table_6_temp
    global table_7_temp
    global table_8_temp
    global table_9_temp
    global table_10_temp
    global table_avg_temp
    global ambient_temp
    global soil_temp
    cmd = "digitemp_DS9097 -a"
    for outline in os.popen(cmd).readlines():
        outline = outline[:-1]
        S = string.split(outline, " ")
        if S[0] == TEMP_TABLE_1_ADDR:
            table_1_temp = float(S[1])
        if S[0] == TEMP_TABLE_2_ADDR:
            table_2_temp = float(S[1])
        if S[0] == TEMP_TABLE_3_ADDR:
            table_3_temp = float(S[1])
        if S[0] == TEMP_TABLE_4_ADDR:
            table_4_temp = float(S[1])
        if S[0] == TEMP_TABLE_5_ADDR:
            table_5_temp = float(S[1])
        if S[0] == TEMP_TABLE_6_ADDR:
            table_6_temp = float(S[1])
        if S[0] == TEMP_TABLE_7_ADDR:
            table_7_temp = float(S[1])
        if S[0] == TEMP_TABLE_8_ADDR:
            table_8_temp = float(S[1])
        if S[0] == TEMP_TABLE_9_ADDR:
            table_9_temp = float(S[1])
        if S[0] == TEMP_TABLE_10_ADDR:
            table_10_temp = float(S[1])
        if S[0] == TEMP_AMBIENT_ADDR:
            ambient_temp = float(S[1])
        if S[0] == TEMP_SOIL_ADDR:
            soil_temp = float(S[1])
    table_avg_temp = (table_1_temp + table_2_temp + table_3_temp + table_4_temp + table_5_temp + table_6_temp + table_7_temp + table_8_temp + table_9_temp + table_10_temp)/10

# First, link the UART device names to the known serial ID's since the system during boot can register them in any order

print "Beginning UART device mapping..."
vendor_id = None
product_id = None
for dn in glob.glob('/sys/bus/usb/devices/*') :
    try     :
        vid = int(open(os.path.join(dn, "idVendor" )).read().strip(), 16)
        pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
        sid = open(os.path.join(dn, "serial")).read().strip()
        if  ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)) :
            dns = glob.glob(os.path.join(dn, os.path.basename(dn) + "*"))
            for sdn in dns :
                for fn in glob.glob(os.path.join(sdn, "*")) :
                    if  re.search(r"\/ttyUSB[0-9]+$", fn) :
                        if (sid == OUTLET_UART_SERIAL):
                            OUTLET_DEV = os.path.join("/dev", os.path.basename(fn))
                            print "Mapping outlet device to: " + OUTLET_DEV
                        if (sid == PUMP_UART_SERIAL):
                            PUMP_DEV = os.path.join("/dev", os.path.basename(fn))
                            print "Mapping pump device to: " + PUMP_DEV
                        if (sid == TEMP_UART_SERIAL):
                            TEMP_DEV = os.path.join("/dev", os.path.basename(fn))
                            print "Mapping temp device to: " + TEMP_DEV
                    pass
                pass
            pass
        pass
    except ( ValueError, TypeError, AttributeError, OSError, IOError ) :
        pass
    pass
print "Finished UART device mapping"

# Second, open serial devices
print "Opening serial devices..."
ser_outlet = serial.Serial(OUTLET_DEV,9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,None,False,True,None,True,None)

print "Outlet UART Opened: " + str(ser_outlet.isOpen())

ser_pump = serial.Serial(PUMP_DEV,9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,None,False,True,None,True,None)

print "Pump UART Opened: " + str(ser_pump.isOpen())

ser_temp = serial.Serial(TEMP_DEV,9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,None,False,True,None,True,None)

print "Temp UART Opened: " + str(ser_temp.isOpen())

# Third, turn off the relays
toggle_relay(ser_pump, pump_relay_state) #pump default state 
toggle_relay(ser_outlet, outlet_relay_state) #outlet default state 

# Fourth initialize temp bus

print "Initializing temperature bus..."
init_temps(TEMP_DEV)
print "Temperature bus initialized..."

# BEGIN SERVER

print "Starting socket server..."

HOST = ''
PORT = 8888

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 8888))
server_socket.listen(5)
print "Listening on port 8888..."

read_list = [server_socket]
prev_time = time.time()

while True:
    time.sleep(.2) # sleep for 200ms each loop

    # Check sockets for incoming connections and requests
    readable, writable, errored = select.select(read_list, [], [], 0) # 0 timeout
    for s in readable:
        if s is server_socket:
	    # Accept new connection and create the socket for it
            client_socket, address = server_socket.accept()
            read_list.append(client_socket)
            print "Accepted connection from ", address
        else:
            data = s.recv(4096)
            if data:
                result = process_request(data)
                if result:
                    s.send(result)
            else:
                s.close()
                read_list.remove(s)

    cur_time = time.time()
    # Query temperature bus for updates every 5 seconds 
    if (cur_time > (prev_time+update_time)):
        prev_time = cur_time
        update_temps()
        # Make pump relay decisions based on temperature updates (
        if (pump_relay_state == True):
            if (table_avg_temp > (table_temp_target + table_temp_delta)):
                toggle_relay(ser_pump,False) 
        else:
            if (table_avg_temp < (table_temp_target - table_temp_delta)):
                toggle_relay(ser_pump,True)

        if (not os.path.isfile("/media/firestation/connected")):
            print "Attempting to connect to network drive for data logging"
            # try to remount drive (maybe something went down?)
            cmd = "mount -t cifs //192.168.220.10/hhcontroller /media/firestation -o username=hhcontroller,password=dagethot"
            for outline in os.popen(cmd).readlines():
                outline = outline[:-1];
                print outline
        #if we still weren't able to establish a connection to the fileshare we won't attempt to log data
        if (not os.path.isfile("/media/firestation/connected")):
            print "Unable to mount share...continuing"
            continue

        # Write data points to network share
        with open('/media/firestation/temperature.log', 'a') as f:
            ts = time.strftime("%a, %d %b %Y %H:%M:%S\n", time.localtime()) 
            f.write(ts)
            f.write("T1," + str(table_1_temp) + '\n')
            f.write("T2," + str(table_2_temp) + '\n')
            f.write("T3," + str(table_3_temp) + '\n')
            f.write("T4," + str(table_4_temp) + '\n')
            f.write("T5," + str(table_5_temp) + '\n')
            f.write("T6," + str(table_6_temp) + '\n')
            f.write("T7," + str(table_7_temp) + '\n')
            f.write("T8," + str(table_8_temp) + '\n')
            f.write("T9," + str(table_9_temp) + '\n')
            f.write("T10," + str(table_10_temp) + '\n')
            f.write("Avg," + str(table_avg_temp) + '\n')
            f.write("Soil," + str(soil_temp) + '\n')
            f.write("Ambient," + str(ambient_temp) + '\n')


# Cleanup

# FIXME build web front end 

print "Shutting down"

for s in read_list:
    s.close()

ser_pump.close()
ser_outlet.close()
ser_temp.close()
