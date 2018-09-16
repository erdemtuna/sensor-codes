#!/usr/bin/env python
from random import randint
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import ast
import datetime
import time
import netifaces
import sys
import decimal
import math
from nodes import nodes
from cast_sender import cast_sender
import threading #for mcast and threading

# global parameters
messageDirectory = "./json-messages/"
registered_nodes_list = []

# initialize id counter
#id_counter = 1

## Topic Abbrevations ##
#0 : Deactivation
#1 : KeepAlive
#2 : Output
#3 : Registration
#4 : Removal
#5 : Update
#6 : ID_REQ

# save NEW_ID's to .txt file and registered_nodes_list
def save_new_id(NEW_ID , index) :
	if NEW_ID == "0001" :
		f = open("id-list.txt","w")
		f.close()
	print "Saving the new node with ID" + " " + NEW_ID
	file = open("id-list.txt","a") 
	file.write(str(NEW_ID) + "\n") 
	file.close()
	
	print "Creating new object for the new node."
	#create a new object inside the list
	new_node = nodes(NEW_ID , client)
        registered_nodes_list.insert(index,new_node)
	print "The new node is now saved to database."

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	client.subscribe([("0/#", 0), ("1/#", 0), ("2/#", 0), ("3/#",0), ("4/#",0), ("5/#", 0), ("6/#", 0),("Output/#", 0), ("Registration/#", 0), ("Update/#", 0), ("Removal/#",0), ("KeepAlive/#",0), ("Deactivation/#", 0)])

# initialize id counter
id_counter = 1

def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload))

	global id_counter	
	#message analysis starts
	
	#if message is an ID_REQ message, assign a new ID to target node
	if msg.topic == '6/' :
		print "Message with topic " + msg.topic + " arrived"		
		NEW_ID = id_counter
		# format the NEW_ID to 4 digit, e.g., 1 -> 0001; 57-> 0057
		NEW_ID = format(NEW_ID, "04")
		# save the NEW_ID to .txt file and to registered_nodes_list
		save_new_id(NEW_ID, id_counter)
		# increment the id_counter
		id_counter = id_counter + 1
		#send the NEW_ID to written 6lowpan address in the msg.payload
		publish.single("6/","{}".format(NEW_ID), hostname="{}".format(msg.payload))
		print "NEW_ID is sent back to the device"

	#messages from nodes
	elif msg.topic == '0/' or msg.topic == '1/' or msg.topic == '2/' or msg.topic == '3/' or msg.topic == '3/' or msg.topic == '4/' or msg.topic == '5/' :
		print "Message with topic " + msg.topic + " arrived"
		# parse the content of the message
		MY_ID = msg.payload[0:4]
		flag = msg.payload[5:6]
		packet_number = msg.payload[6:8]
		print packet_number
		payload = msg.payload[8:]
		#check if sender ID is in the list of current_nodeClass_list
		for i in range(len(registered_nodes_list)):
	    		if registered_nodes_list[i].id == MY_ID :
				registered = True
				# if IDs match, save the index
				index = i 
				# break the for loop
				break
			else :
				registered = False
		if registered :
			print "Device " +registered_nodes_list[index].id + " registered in registered_nodes_list with index" + str(index)
			# passs msg.payload to related node object
			registered_nodes_list[index].receive_message(msg.payload)
			registered = False		
		else : 
			print('Register the device first with topic -6/- to send data')

	#messages from gateway
	elif msg.topic == 'Deactivation/' or msg.topic == 'KeepAlive/' or msg.topic == 'Output/' or msg.topic == 'Registration/' or msg.topic == 'Removal/' or msg.topic == 'Update/':
		print "Message with topic" + msg.topic + "arrived"
		# parse the content of the message
		rawInput = json.loads(str(msg.payload),'utf-8')
		# get the target node ID
		send_to_this_device_id = rawInput['Content']['ID']
		# get the target node lowpanIP
		send_to_this_device_lowpan= rawInput['Content']['lowpanIP']
		if msg.topic=="KeepAlive/" :
			print "New Request: Send a KeepAlive message to node with ID " + send_to_this_device_id
		        publish.single("1/", "{}".format(send_to_this_device_id), hostname="{}".format(send_to_this_device_lowpan))
			print "The KeepAlive request is sent to node with ID " + send_to_this_device_id

		if msg.topic=="Deactivation/" :
			print "New Request: Send a Deactivation message to node with ID " + send_to_this_device_id
		        publish.single("0/", "{}".format(send_to_this_device_id), hostname="{}".format(send_to_this_device_lowpan))
			print "The Deactivation request is sent to node with ID " + send_to_this_device_id

		if msg.topic=="Removal/" :
			print "New Request: Send a Removal message to node with ID " + send_to_this_device_id
		        publish.single("4/", "{}".format(send_to_this_device_id), hostname="{}".format(send_to_this_device_lowpan))
			print "The Removal request is sent to node with ID " + send_to_this_device_id

	# Invalid topic name
	else :
		print('Invalid message topic. Message topics can be as follows:')
		print('## 0/ : Deactivation ##')
		print('## 1/ : KeepAlive ##')
		print('## 2/ : Output ##')
		print('## 3/ : Registration ##')
		print('## 4/ : Removal ##')
		print('## 5/ : Update ##')
		print('## 6/ : ID_REQ ##')
	
## Topic Abbrevations ##
#0 : Deactivation
#1 : KeepAlive
#2 : Output
#3 : Registration
#4 : Removal
#5 : Update
#6 : ID_REQ

c = cast_sender()
c.start()
print "mcast started in a thread"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#listen the broker on edgenode
client.connect('fe80::e49c:9c4c:3a20:5547%lowpan0', 1883, 60)

client.loop_forever()
