import threading
import json

lock = threading.Lock()

iplist = set()

def addtoiplist(ip):
	iplist.add(ip)

def getiplist():
	return iplist

tnxlist = {}

current_tnxid = 0

def performtnx(name, qty):

	if name in itemlist.keys():
		if qty <= itemlist[name]['qty']:
			itemlist[name]['qty'] = itemlist[name]['qty'] - qty

			if itemlist[name]['qty'] == 0:
				del itemlist[name]
		else:
			return False
	else:
		print("Parser Error: Invalid Transaction")
		return False

	return True

def createtnx(name, qty):
	global current_tnxid
	
	if performtnx(name, qty):
		print("Transaction Successful!")
	else:
		print("Parser Error: Transaction failed!")
		return False

	current_tnxid = current_tnxid + 1

	tnxlist[current_tnxid] = {'tnxid':current_tnxid,
					  'name': name,
					  'qty': qty}
	return createRequest('ADDTNX', tnxlist[current_tnxid])

def gettnxlist():
	return tnxlist

itemlist = {}

current_itemid = 0

def createitem(name, qty, price):
	global current_itemid
	current_itemid = current_itemid + 1

	if name in itemlist.keys():
		return False

	itemlist[name] = {'itemid':current_itemid,
					  'name': name,
					  'qty': qty,
					  'price': price}
	return createRequest('ADDITM', itemlist[name])

def getitemlist():
	return itemlist

""" Data is processed as JSON format. 
HEADERs for the data is created over here """
# Item List and Transactions. TNX should cange the amount of qtys in other nodes. TNX to be generated on a buy or a sell
# {HEAD: "SNDALL" | "SNDTNX", DATA: {"txid" : 123, "item" : "iphone", "qty" : 10,  "price" : 1000 }}

# Instructions:
# parseHeader return val: Parse Result -> True/False, Send To individual thread -> True/False, Data
# Anything created in the Parser will return as a request

def createDictonary(HEAD, DATA):
	dicti = {}
	dicti['HEAD'] = HEAD
	dicti['DATA'] = DATA
	return dicti

def createInitDictonary(HEAD, IPLIST, ITEMLIST):
	dicti = {}
	dicti['HEAD'] = HEAD
	dicti['IPLIST'] = IPLIST
	dicti['ITEMLIST'] = ITEMLIST
	return dicti

def createRequest(HEAD, DATA = {}):

	if(HEAD == 'INITCN' or HEAD == 'rINITCN'):
		return json.dumps(createInitDictonary(HEAD, repr(iplist), itemlist))

	elif((HEAD == 'ADDTNX' or HEAD == 'ADDITM') and DATA):
		return json.dumps(createDictonary(HEAD, DATA))


class parser:

	def __init__(self, jsonString):
		# self.jsonString = jsonString
		self.d = json.loads(jsonString)
		self.HEAD = self.d['HEAD']

		try:
			self.DATA = self.d['DATA']
		except:
			self.IPLIST = self.d['IPLIST']
			self.ITEMLIST = self.d['ITEMLIST']

	def parseHeader(self):

		global lock

		if(self.HEAD == 'ADDTNX'):
			global current_tnxid
			print("DEBUG: Received ADDTNX Packet")
			# ADDTNX - ADD a Transaction. Tnx is present in DATA field
			# Place to Modify the Transaction Protocol
			if self.DATA['tnxid'] not in tnxlist.keys():

				lock.acquire()

				if performtnx(self.DATA['name'], self.DATA['qty']):

					print("Transaction Successful!")

					current_tnxid = self.DATA['tnxid']
					tnxlist[self.DATA['tnxid']] = self.DATA

					lock.release()

					return True, False, createRequest('ADDTNX',self.DATA)

				else:
					print("Parser Error: Transaction failed!")

				lock.release()
			else:
				return True, False, None

		elif(self.HEAD == 'ADDITM'):
			global current_itemid
			# ADDITM - Add Item to ItemList. Item details is present in Data field
			# Rebroadcast ADDITM

			if self.DATA['name'] not in itemlist.keys():

				lock.acquire()

				current_itemid = self.DATA['itemid']
				itemlist[self.DATA['name']] = self.DATA

				lock.release()

				return True, False, createRequest('ADDITM', self.DATA)
			else:
				# Item Already received
				print("Ignore ADDITM")
				return True, False, None

		elif(self.HEAD == 'INITCN'):
			# INIT - New Initial connection. Send the Ip list

			lock.acquire()

			iplist.update(eval(self.IPLIST))
			itemlist.update(self.ITEMLIST)

			lock.release()

			return True, True, createRequest('rINITCN')

		elif(self.HEAD == 'rINITCN'):
			# rINITIP - reply Initial connection. Receive the IP list and update

			lock.acquire()

			iplist.update(eval(self.IPLIST))
			itemlist.update(self.ITEMLIST)

			lock.release()

			return True, False, None

		else:
			return False, False, None


