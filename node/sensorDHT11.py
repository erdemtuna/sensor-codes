#!/usr/bin/env python
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import Adafruit_DHT #for sensor
import json
import ast
import datetime
import time
import netifaces
import sys
import decimal
import math

import struct #for mcast and threading
import socket #for mcast and threading
import sys #for mcast and threading
import threading #for mcast and threading
from cast_listener import cast_listener

MY_ID = None
UUID = "3dbe27d1"
can_send_message = True
Model = "DHT11"
char_per_packet=21
global deactivation
deactivation = False

# lowpan0 address of the edgenode
edgenode_6lowpan_address = None


#obtain the ip address
addrswlan0 = netifaces.ifaddresses('wlan0')
#obtain the 6lowpan address
addrslowpan0 = netifaces.ifaddresses('lowpan0')

# lowpan0 address of the deployed device
my_6lowpan_address = str(addrslowpan0[netifaces.AF_INET6][1]['addr'])

# global parameters
messageDirectory = "./json-messages/"

#sensor initialization over

#sensor initialization
sensor = Adafruit_DHT.DHT11
pin = "4"
#sensor initialization over


## Topic Abbrevations ##
#0 : Deactivation
#1 : KeepAlive
#2 : Output
#3 : Registration
#4 : Removal
#5 : Update
#6 : ID_REQ

#sensor function declarations
def read_hum():
	global sensor
	global pin
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	return humidity

#sensor functions over

#packet structure
# Payload = MY_ID (4) | message_type (1) | flag (1) | packet_number (2) | message (21)

#message header types
# o = one shot
# s = start of the message sequence
# c = continue on the same message sequence
# e = end of the message sequence

#string functions

#calculate json packet_length
def jsongString_packet_length(packet_itself):
    print json.dumps(packet_itself)
    print len(packet_itself)
    packet_length=decimal.Decimal(len(json.dumps(packet_itself))) / char_per_packet
    return int(math.ceil(packet_length))

#send 0 : Deactivation
def send_JSONdeactivation(MY_ID):
    with open(messageDirectory+'JSONdeactivation-6lowpan.json', 'r+') as f:
        json_data = json.load(f)
        f.close()
    #determine packet length
    #packet_length = jsongString_packet_length(json_data)
    #print packet_length
    json_data["DeactDate"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    json_data['ID'] = str(MY_ID)
    packet_length = jsongString_packet_length(json_data)
    #initialize payload with ID and message type 0
    payload = str(MY_ID) + "0"
    #construct the rest of the payload
    if packet_length == 1 :
        payload =str( payload + "o" + str(format(0, "02")) + str(json.dumps(json_data)))
        print payload
        publish.single("0/","{}".format(str(payload)), hostname="{}".format(edgenode_6lowpan_address))
    else :
        for x in range(packet_length):
            if (x) == 0 :
                index = char_per_packet
                payload = payload + "s" + format(x, "02") + json.dumps(json_data)[0:index]
                publish.single("0/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            elif (x == packet_length-1) :
                index = char_per_packet*packet_length
                payload = payload + "e" + format(x, "02") + json.dumps(json_data)[index:]
                publish.single("0/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            else :
                index1 = char_per_packet * x
                index2 = char_per_packet * (x+1)
                payload = payload + "c" + format(x, "02") + json.dumps(json_data)[index1:index2]
                publish.single("0/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]


#send 1 : KeepAlive
def send_JSONkeepAlive(cf, MY_ID):
    with open(messageDirectory+'JSONkeepAlive-6lowpan.json', 'r+') as f:
        json_data = json.load(f)
        f.close()
    #determine packet length
    #packet_length = jsongString_packet_length(json_data)
    #print packet_length
    json_data['AliveDate'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    json_data['Output'] = str(cf)
    json_data['ID'] = str(MY_ID)
    json_data['UUID'] = str(UUID)
    packet_length = jsongString_packet_length(json_data)
    #initialize payload with ID and message type 1
    payload = str(MY_ID) + "1"
    print payload + str(packet_length)
    #construct the rest of the payload
    if packet_length == 1 :
        payload =str( payload + "o" + str(format(0, "02")) + str(json.dumps(json_data)))
        print payload
        publish.single("1/","{}".format(str(payload)), hostname="{}".format(edgenode_6lowpan_address))
    else :
        for x in range(packet_length):
            if (x) == 0 :
                print "head"
                index = char_per_packet
                payload = payload + "s" + format(x, "02") + json.dumps(json_data)[0:index]
                publish.single("1/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            elif (x == packet_length-1) :
                print "middle"
                index = char_per_packet*(packet_length-1)
                payload = payload + "e" + format(x, "02") + json.dumps(json_data)[index:]
                publish.single("1/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            else :
                print "problem"
                index1 = char_per_packet * x
                index2 = char_per_packet * (x+1)
		print "index"
                payload = payload + "c" + format(x, "02") + json.dumps(json_data)[index1:index2]
		print "mqtt"
                publish.single("1/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]


#send 2 : Output
def send_JSONoutput(cf, MY_ID):
    with open(messageDirectory+'JSONoutput-6lowpan.json', 'r+') as f:
        json_data = json.load(f)
        f.close()
    #determine packet length
    #packet_length = jsongString_packet_length(json_data)
    #print packet_length
    json_data['Output'] = str(cf)
    json_data['ID'] = str(MY_ID)
    json_data['UUID'] = str(UUID)
    packet_length = jsongString_packet_length(json_data)
    #initialize payload with ID and message type 2
    payload = str(MY_ID) + "2"
    #construct the rest of the payload
    if packet_length == 1 :
        payload =str( payload + "o" + str(format(0, "02")) + str(json.dumps(json_data)))
        print payload
        publish.single("2/","{}".format(str(payload)), hostname="{}".format(edgenode_6lowpan_address))
    else :
        for x in range(packet_length):
            if (x) == 0 :
                index = char_per_packet
                payload = payload + "s" + format(x, "02") + json.dumps(json_data)[0:index]
                publish.single("2/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            elif (x == packet_length-1) :
                index = char_per_packet*(packet_length-1)
                payload = payload + "e" + format(x, "02") + json.dumps(json_data)[index:]
                publish.single("2/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            else :
                index1 = char_per_packet * x
                index2 = char_per_packet * (x+1)
                payload = payload + "c" + format(x, "02") + json.dumps(json_data)[index1:index2]
                publish.single("2/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]

#send 3 : Registration
def send_JSONregistration(MY_ID):
    with open(messageDirectory+'JSONregistration-6lowpan.json', 'r+') as f:
        json_data = json.load(f)
        f.close()
    #determine packet length
    #packet_length = jsongString_packet_length(json_data)
    #print packet_length
    json_data['Connectivity']['DeviceIP'] = addrswlan0[netifaces.AF_INET][0]['addr']
    json_data['ID'] = str(MY_ID)
    json_data['UUID'] = str(UUID)
    json_data['Connectivity']['lowpanIP'] = addrslowpan0[netifaces.AF_INET6][1]['addr']
    json_data['Connectivity']['ConnectedDevice'] = addrswlan0[netifaces.AF_INET6][0]['addr']
    json_data['GeneralDescription']['DeploymentDate'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    json_data['GeneralDescription']['CanMeasure']=str("Humidity")
    json_data['GeneralDescription']['Model']=Model
    json_data['GeneralDescription']['Unit'] = str("Percent")
    packet_length = jsongString_packet_length(json_data)
    #initialize payload with ID and message type 3
    payload = str(MY_ID) + "3"
    #construct the rest of the payload
    if packet_length == 1 :
        payload =str( payload + "o" + str(format(0, "02")) + str(json.dumps(json_data)))
        print payload
        publish.single("3/","{}".format(str(payload)), hostname="{}".format(edgenode_6lowpan_address))
    else :
        for x in range(packet_length):
            if (x) == 0 :
                index = char_per_packet
                payload = payload + "s" + format(x, "02") + json.dumps(json_data)[0:index]
                publish.single("3/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            elif (x == packet_length-1) :
                index = char_per_packet*(packet_length-1)
                payload = payload + "e" + format(x, "02") + json.dumps(json_data)[index:]
                publish.single("3/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            else :
                index1 = char_per_packet * x
                index2 = char_per_packet * (x+1)
                payload = payload + "c" + format(x, "02") + json.dumps(json_data)[index1:index2]
                publish.single("3/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]

#send 4 : Removal
def send_JSONremoval(MY_ID):
    with open(messageDirectory+'JSONremoval-6lowpan.json', 'r+') as f:
        json_data = json.load(f)
        f.close()
    #determine packet length
    #packet_length = jsongString_packet_length(json_data)
    #print packet_length
    json_data['Output'] = str(cf)
    json_data['ID'] = str(MY_ID)
    json_data['UUID'] = str(UUID)
    packet_length = jsongString_packet_length(json_data)
    #initialize payload with ID and message type 4
    payload = str(MY_ID) + "4"
    #construct the rest of the payload
    if packet_length == 1 :
        payload =str( payload + "o" + str(format(0, "02")) + str(json.dumps(json_data)))
        print payload
        publish.single("4/","{}".format(str(payload)), hostname="{}".format(edgenode_6lowpan_address))
    else :
        for x in range(packet_length):
            if (x) == 0 :
                index = char_per_packet
                payload = payload + "s" + format(x, "02") + json.dumps(json_data)[0:index]
                publish.single("4/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            elif (x == packet_length-1) :
                index = char_per_packet*(packet_length-1)
                payload = payload + "e" + format(x, "02") + json.dumps(json_data)[index:]
                publish.single("4/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            else :
                index1 = char_per_packet * x
                index2 = char_per_packet * (x+1)
                payload = payload + "c" + format(x, "02") + json.dumps(json_data)[index1:index2]
                publish.single("4/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]

#send 5 : Update
def send_JSONupdate(cf, MY_ID):
    with open(messageDirectory+'JSONupdate-6lowpan.json', 'r+') as f:
        json_data = json.load(f)
        f.close()
    #determine packet length
    #packet_length = jsongString_packet_length(json_data)
    #print packet_length
    json_data['ID'] = str(MY_ID)
    json_data['UUID'] = str(UUID)
    packet_length = jsongString_packet_length(json_data)
    #initialize payload with ID and message type 5
    payload = str(MY_ID) + "5"
    #construct the rest of the payload
    if packet_length == 1 :
        payload =str( payload + "o" + str(format(0, "02")) + str(json.dumps(json_data)))
        print payload
        publish.single("5/","{}".format(str(payload)), hostname="{}".format(edgenode_6lowpan_address))
    else :
        for x in range(packet_length):
            if (x) == 0 :
                index = char_per_packet
                payload = payload + "s" + format(x, "02") + json.dumps(json_data)[0:index]
                publish.single("5/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            elif (x == packet_length-1) :
                index = char_per_packet*(packet_length-1)
                payload = payload + "e" + format(x, "02") + json.dumps(json_data)[index:]
                publish.single("5/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
            else :
                index1 = char_per_packet * x
                index2 = char_per_packet * (x+1)
                payload = payload + "c" + format(x, "02") + json.dumps(json_data)[index1:index2]
                publish.single("5/","{}".format(payload), hostname="{}".format(edgenode_6lowpan_address))
                payload = payload[0:5]
#string functions over


## Topic Abbrevations ##
#0 : Deactivation
#1 : KeepAlive
#2 : Output
#3 : Registration
#4 : Removal
#5 : Update
#6 : ID_REQ

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	client.subscribe([("0/#", 0), ("1/#", 0), ("2/#", 0), ("3/#",0), ("4/#",0), ("5/#", 0),("6/#",0)])
def on_message(client, userdata, msg):
	global MY_ID, can_send_message
	print(msg.topic + " " + str(msg.payload))
	
	#arrived 6 : ID_REQ
	if msg.topic=="6/" :
		print "6 : ID_REQ message is detected"
		if MY_ID == None:
			MY_ID = msg.payload
			print "Passed to send_JSONregistration(MY_ID)"
			can_send_message = False
			send_JSONregistration(MY_ID)
		else:
			print "Got an 6 : ID_REQ message but dismissed, since ID is assigned already!"

	#arrived 0 : Deactivation
	elif msg.topic=="0/" :
		print "0 : Deactivation message is detected"
		print "Passed to send_JSONdeactivation(MY_ID)"
		can_send_message = False
		send_JSONdeactivation(MY_ID)

	#arrived 1 : KeepAlive
	elif msg.topic=="1/" :
		print "1 : KeepAlive message is detected"
		print "Passed to send_JSONkeepAlive(MY_ID)"
		can_send_message = False
		send_JSONkeepAlive(cf, MY_ID)
		

	#arrived 4 : Removal
	elif msg.topic=="4/" :
		print "4 : Removal message is detected"
		print "Passed to send_JSONremoval(MY_ID)"
		can_send_message = False
        loopWorking = False
		send_JSONremoval(MY_ID)

	# allow a new message to be published
	can_send_message = True
		

## Topic Abbrevations ##
#0 : Deactivation
#1 : KeepAlive
#2 : Output
#3 : Registration
#4 : Removal
#5 : Update
#6 : ID_REQ

loopWorking = True
while edgenode_6lowpan_address == None:
	print "Looking for edgenodes"
        #edgenode_6lowpan_address
	c=cast_listener()
        edgenode_6lowpan_address = c.mcast_control()
        time.sleep(2)

if True :

    #publish a ID_REQ (6) message to broker to obtain sensor ID.
    publish.single("6/", "{}".format(my_6lowpan_address), hostname="{}".format(edgenode_6lowpan_address))
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(my_6lowpan_address, 1883, 60)
    
    client.loop_start()
    former=-45
    #measurements
    while loopWorking :
    	if deactivation == False and MY_ID != None and can_send_message:  
    		cf=read_hum()
    		#test if humidity has changed by 1.5% since last data transfer	
    		if abs(cf-former)>=(cf/75):
    		    send_JSONoutput(cf, MY_ID)
    		    print "Temperature measurement..."
    		    former=cf
    	time.sleep(10)
