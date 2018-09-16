#!/usr/bin/env python

import time
import struct
import socket
import sys
import threading
import time

MYPORT = 8123
MYGROUP_6 = 'ff02::1'
MYTTL = 1# Increase to reach other networks

class cast_listener:

    def mcast_control(self):
	group = MYGROUP_6
	print "mcast_control"
    	return self.mcast_receiver(group)

    def mcast_receiver(self, group): #Look up multicast group address in name server and find out IP version
	print "mcast_receiver"
        addrinfo = socket.getaddrinfo(group, None)[0]

        # Create a socket
        s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        
        # Allow multiple copies of this program on one machine#(not strictly needed)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind it to the port
        s.bind(('', MYPORT))
        
        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])# Join group
        if addrinfo[0] == socket.AF_INET: #IPv4
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else :
            mreq = group_bin + struct.pack('@I', 0)
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
        
        # Loop, printing any data we receive
	state = True
        while state:
            data, sender = s.recvfrom(1500)
            while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
            print str(sender[0])
            time.sleep(2)
#	    s.shutdown()
	    state = False
            return str(sender[0])

    #def __init__(self): #create and start our threads
	#print "cast_listener class"
	#mcast_control()
    	#threads = list()
	#t = threading.Thread(target = mcast_control)# pass in the callable
    	#threads.append(t)
    	#print('Starting Thread')
    	#t.start()
    
    	# wait
    	#for each to finish(join)
    	#for i, t in enumerate(threads):
    	#    t.join()
    	#    print('Thread {} Stopped'.format(i))
