#!/usr/bin/env python3

'''
Basic IPv4 router (static routing) in Python.

Collaborators: Yuxin David Huang, Martin Liu' 16
Under supervision of Prof. Joel Sommers
COSC 465 (Spring 2015), Colgate University
'''

import sys
import os
import time
from switchyard.lib.packet import *
from switchyard.lib.address import *
from switchyard.lib.common import *

class Router(object):
	def __init__(self, net):
		'''
		(PyLLNet) -> ()

		Initializes the router object.
		'''
		self.net = net
		self._interfaces = self.net.interfaces()
		self._arptable = {}		# for later use, do nothing for now

	def _has_interface(self, arp):
		'''
		(Arp) -> (bool, IPv4Addr, Arp)

		Checks whether we need to respond to the ARP request.
		'''
		for interface in self._interfaces:
			if arp.targetprotoaddr == interface.ipaddr:
				return True, arp.targetprotoaddr, arp
		return False, None, None

	def _create_arp_reply(self, targetip, arp_req, dev):
		'''
		(IPv4Addr, Arp, Interface) -> (Packet)

		Creates an ARP reply.
		'''
		arp_reply = create_ip_arp_reply(dev.ethaddr,
										arp_req.senderhwaddr,
										dev.ipaddr,
										arp_req.senderprotoaddr)
		return arp_reply

	def router_main(self):    
		'''
		() -> ()

		Main method for router; we stay in a loop in this method, receiving
		packets until the end of time.
		'''
		while True:
			gotpkt = True
			try:
				dev, pkt = self.net.recv_packet(timeout=1.0)
			except NoPackets:
				log_debug("No packets available in recv_packet")
				gotpkt = False
			except Shutdown:
				log_debug("Got shutdown signal")
				break

			if gotpkt:
				log_debug("Got a packet: {}".format(str(pkt)))

				if pkt.has_header(Arp):
					arp = pkt.get_header(Arp)
					need_resp, targetip, arp_req = self._has_interface(arp)
					if need_resp:
						arp_reply = self._create_arp_reply(targetip, arp_req,
														   self.net.port_by_name(dev))
						self.net.send_packet(dev, arp_reply)			

def switchy_main(net):
	'''
	(PyLLNet) -> ()

	Main entry point for router.  Just create Router
	object and get it going.
	'''
	r = Router(net)
	r.router_main()
	net.shutdown()
