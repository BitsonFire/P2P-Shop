import socket
import threading
from threading import Thread
import time
import select
import parser
import json

broadcastdata = ""
broadcastmode = False

# Barrier used for Broadcasting
barrier = None

event = threading.Event()

class IThread(Thread):

	# threadtype -> inbound thread == 0 or outbound thread == 1
	def __init__(self, threadtype, clientsocket, clientaddress):
		Thread.__init__(self)
		self.clientsocket = clientsocket
		self.clientaddress = clientaddress
		self.threadtype = threadtype

	def run(self):

		global broadcastmode
		global broadcastdata
		global barrier
		individualsend = False
		mdata = None

		if(self.threadtype == 0):
			print(f"Connection from {self.clientaddress} has been established!")

		elif(self.threadtype == 1):
			# Exchange Iplist and Itemlist and update
			self.clientsocket.send(bytes(parser.createRequest('INITCN'),"utf-8"))

		
		while True:
			try:
				readable, _, _ = select.select([self.clientsocket], [], [], 0)
			except:
				print("readable error occured")

			if readable:

				data = self.clientsocket.recv(1024)
				print(data)

				if(data == b''):
					print("Error: {} Client might have closed the socket".format(self.clientaddress))
					break

				p = parser.parser(data.decode("utf-8"))
				result, individualsend, mdata = p.parseHeader()

				# Enables Rebroadcasting
				if individualsend == False and mdata != None and result == True:
					print("Enabling Rebroadcasting")
					broadcastData(mdata)

				# Update GUI
				connectionManager.setevent()

			if individualsend == True:

				print("Sending Individually to this thread")
				self.clientsocket.send(bytes(mdata, "utf-8"))
				individualsend = False
				mdata = None

				# Update GUI
				connectionManager.setevent()

			if broadcastmode == True:

				i = barrier.wait()
				broadcastmode = False

				self.clientsocket.send(bytes(broadcastdata,"utf-8"))

				# Update GUI
				connectionManager.setevent()

		self.clientsocket.close()

class connectionManager:

	def __init__(self):
		self.bindip = socket.gethostname()

	def setbindip(self, bindip):
		self.bindip = bindip

	def inbound(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		s.bind((self.bindip, 1234))
		s.listen(5)

		while(True):
			print(f"Listening for incoming connections on " + self.bindip)
			clientsocket, address = s.accept()
			crt = IThread(0, clientsocket, address)
			crt.setName("connectionthread")
			parser.addtoiplist(address[0])
			crt.start()

	def outbound(self, ip, port_number):
		try:
			z = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print(f"Trying to establish connection")
			z.connect((ip, port_number))
			cst = IThread(1, z, ip)
			cst.setName("connectionthread")
			cst.start()
		except:
			print("Error: Cannot Establish connection with requested ip address")

	@staticmethod
	def getcountofconnectionthreads():
		count = 0
		allthreads = threading.enumerate()
		for t in allthreads:
			if t.getName() == "connectionthread":
				count = count + 1
		return count

	@staticmethod
	def setevent():
		global event
		event.set()

	@staticmethod
	def waitevent():
		global event
		event.wait()
		event.clear()

def broadcastData(data):
	global barrier
	global broadcastdata
	global broadcastmode
	broadcastdata = data
	broadcastmode = True
	barrier = threading.Barrier(connectionManager.getcountofconnectionthreads(), timeout = None)