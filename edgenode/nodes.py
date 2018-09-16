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

class nodes:

	def __init__(self, id, client):
		# declare the variable for completed flag
		self.completed = False
		# set the input device id
		self.id = id
		# declare one_shot message flag
		self.one_shot_message = []
		
		self.build = ""
		# declare s-tart, c-ontinue, e-nd message flags
		self.sce_message = []
		# set the input mqtt_client
		self.mqtt_client = client
			
		self.last_packet_number = 0
	## Topic Abbrevations ##
	#0 : Deactivation
	#1 : KeepAlive
	#2 : Output
	#3 : Registration
	#4 : Removal
	#5 : Update
	#6 : ID_REQ

	def receive_message(self, packet):
		messageDirectory = "./json-messages/"
		MY_ID = packet[0:4]
		message_type = packet[4:5]
		flag = packet[5:6]
		packet_number = packet[6:8]
		payload = packet[8:]
		
		# merge the incoming messages according to flags
		if (flag=='o') :
			self.one_shot_message = payload
		elif (flag == 's' and packet_number == "00") :
			self.sce_message.insert(0, payload)
			print "hi"
		#packet_number = int(packet_number.lstrip("0"))
		elif (flag == 'c') :
			packet_number = int(packet_number.lstrip("0"))
			self.sce_message.insert(packet_number,payload)
			#self.sce_message = self.sce_message + payload
		elif (flag == 'e') :
			packet_number = int(packet_number.lstrip("0"))
			self.last_packet_number = packet_number+1
			self.sce_message.insert(packet_number,payload)
			#self.sce_message = self.sce_message + payload

		if (len(self.sce_message) == self.last_packet_number):
			for lines in self.sce_message:
    				self.build = self.build + lines
			self.build = json.loads(self.build)
			print "JSON packets are merged" + " " + json.dumps(self.build)
			# construct the JSONs to send send it to gateway

			# construct the deactivation JSON to send send it to gateway
			if (message_type == '0') :
				with open(messageDirectory+'JSONdeactivation.json', 'r+') as f:
					json_data = json.load(f)
					f.close()
				# generate the topic
				topic_name = 'Deactivation/'
				# dump the JSON objects
				json_data["Content"]["DeactDate"] = self.build["DeactDate"]
				json_data['Content']['ID'] = self.build["ID"]
				json_data['Content']['UUID'] = self.build["UUID"]
		                #if keepAlive message comes send an answer

			# construct the keepAlive JSON to send send it to gateway
			elif (message_type == '1') :
				with open(messageDirectory+'JSONkeepAlive.json', 'r+') as f:
					json_data = json.load(f)
					f.close()
				# generate the topic
				topic_name = 'KeepAlive/'
				# dump the JSON objects
				json_data['Content']['AliveDate'] = self.build['AliveDate']
				json_data['Content']['Output'] = self.build['Output']
				json_data['Content']['ID'] = self.build['ID']
				json_data['Content']['UUID'] = self.build['UUID']

			# construct the output JSON to send send it to gateway
			elif (message_type == '2') :
				with open(messageDirectory+'JSONoutput.json', 'r+') as f:
					json_data = json.load(f)
					f.close()
				# generate the topic
				topic_name = 'Output/'
				# dump the JSON objects
				json_data['Content']['Output'] = self.build['Output']
				json_data['Content']['ID'] = self.build['ID']
				json_data['Content']['UUID'] = self.build['UUID']

			# construct the registration JSON to send send it to gateway
			elif (message_type == '3') :
				with open(messageDirectory+'JSONregistration.json', 'r+') as f:
					json_data = json.load(f)
					f.close()
				# generate the topic
				topic_name = 'Registration/'
				# dump the JSON objects
				json_data['Content']['Connectivity']['DeviceIP'] = self.build['Connectivity']['DeviceIP']
				json_data['Content']['ID'] = self.build['ID']
				json_data['Content']['UUID'] = self.build['UUID']
				json_data['Content']['Connectivity']['lowpanIP'] = self.build['Connectivity']['lowpanIP']
				json_data['Content']['Connectivity']['ConnectedDevice'] = self.build['Connectivity']['ConnectedDevice']
				json_data['Content']['GeneralDescription']['DeploymentDate'] = self.build['GeneralDescription']['DeploymentDate']
				json_data['Content']['GeneralDescription']['Model'] = self.build['GeneralDescription']['Model']
				json_data['Content']['GeneralDescription']['CanMeasure'] = self.build['GeneralDescription']['CanMeasure']
				json_data['Content']['GeneralDescription']['Unit'] = self.build['GeneralDescription']['Unit']

			# construct the removal JSON to send send it to gateway
			elif (message_type == '4') :
				with open(messageDirectory+'JSONremoval.json', 'r+') as f:
					json_data = json.load(f)
					f.close()
				# generate the topic
				topic_name = 'Removal/'
				# dump the JSON objects
				json_data['Content']['ID'] = str(MY_ID)
				json_data['Content']['UUID'] = str(UUID)

			# construct the update JSON to send send it to gateway
			elif (message_type == '5') :
				with open(messageDirectory+'JSONupdate.json', 'r+') as f:
					json_data = json.load(f)
					f.close()
				# generate the topic
				topic_name = 'Update/'

			# send the message to the gateway via wlan0
			publish.single(topic_name, "{}".format(json.dumps(json_data)), hostname="172.24.1.1")
			# declare one_shot message flag
		        self.one_shot_message = ""
			# declare s-tart, c-ontinue, e-nd message flags
		        self.sce_message = []
			self.build = ""
			self.last_packet_number = 0

