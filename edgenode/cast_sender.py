#!/usr/bin/env python

MYPORT = 8123
MYGROUP_6 = 'ff02::1'
MYTTL = 1# Increase to reach other networks

import time
import struct
import socket
import sys
import threading
import time

class cast_sender(threading.Thread):

    def run(self):
        group = MYGROUP_6
        #threads = list()
#        t = threading.Thread(target = this_object.mcast_sender(group))# pass in the callable
	self.mcast_sender(group)# pass in the callable
#        threads.append(t)
        print('Starting Thread')
#        t.start()
        # wait for each to finish(join)
#        for i, t in enumerate(threads):
#            t.join()
#            print('Thread {} Stopped'.format(i))
       
    
    def mcast_sender(self,group):
        interface = "lowpan0"
        addrinfo = socket.getaddrinfo(group + "%" + interface, None)[0]
        print addrinfo
        s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    
        # Set Time - to - live(optional)
        ttl_bin = struct.pack('@i', MYTTL)
        if addrinfo[0] == socket.AF_INET: #IPv4
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
        else :
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, socket.inet_pton(socket.AF_INET6, "ff02::1") + '\0' * 4)
	i=0
        while True :
	    print "1"
            data = "edgenode multicast message"
            s.sendto(data + '\0', (addrinfo[4][0], MYPORT, 0, addrinfo[4][3]))
            time.sleep(2)
    
#    def __init__(self):
#        threads = list()
#        t = threading.Thread(target = mcast_control)# pass in the callable
#        threads.append(t)
#        print('Starting Thread')
#        t.start()
    
        # wait for each to finish(join)
#        for i, t in enumerate(threads):
#            t.join()
#            print('Thread {} Stopped'.format(i))
