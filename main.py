# -*- coding: utf-8 -*-
import json, sys, os, time
from twisted.protocols import basic
import threading

#LOAD CONFIG
GENERAL_CONFIG_FILE = 'config.conf'
fp = open(GENERAL_CONFIG_FILE, 'r')
GENERAL_CONFIG = eval(fp.read())
fp.close()

#SET SERVER CONFIG
SERVER = GENERAL_CONFIG['server']['host']
PORT = GENERAL_CONFIG['server']['port']

#clients- class array by con
CLIENTS = []

#SET VK SETTINGS
API_ID = GENERAL_CONFIG['vk']['api_id']
SECRET = GENERAL_CONFIG['vk']['secret']

#DB Settings
DB_HOST = GENERAL_CONFIG['db']['host']
DB_USER = GENERAL_CONFIG['db']['login']
DB_PASS = GENERAL_CONFIG['db']['pass']
DB_NAME = GENERAL_CONFIG['db']['name']


#Other
PLUGIN_DIR = 'plugins'

TYPES = {}
LOST_FUNCTIONS = []
NEW_FUNCTIONS = []
#REGISTER TYPE
def regTypes(type, function):
	TYPES[type] = function

#FUNCTION CALLED WHEN USER CLOSE CONNECTION
def regLost(function):
	LOST_FUNCTIONS.append(function)
def regNew(function):
	NEW_FUNCTIONS.append(function)
#PLUGIN LOAD
def load_plugins():
	plugins = find_plugins()
	for plugin in plugins:
		try:
			fp = file(PLUGIN_DIR + '/' + plugin)
			exec fp in globals()
			fp.close()
		except:
			raise
	plugins.sort()
	print '\nloaded',len(plugins),'plug-ins:'
	loaded=', '.join(plugins)
	print loaded,'\n'
def find_plugins():
	print '\nLOADING PLUGINS'
	valid_plugins = []
	invalid_plugins = []
	possibilities = os.listdir('plugins')
	for possibility in possibilities:
		if possibility[-3:].lower() == '.py':
			try:
				fp = file(PLUGIN_DIR + '/' + possibility)
				data = fp.read(8)
				if data == '#plugin+':
					valid_plugins.append(possibility)
				else:
					invalid_plugins.append(possibility)
			except:
				pass
	if invalid_plugins:
		print '\nfailed to load',len(invalid_plugins),'plug-ins:'
		invalid_plugins.sort()
		invp=', '.join(invalid_plugins)
		print invp
		print 'plugins header is not corresponding\n'
	else:
		print '\nthere are not unloadable plug-ins'
	return valid_plugins


#MESSAGE
def messageHnd(connection, data=None):
	if data['type'] != "auth" and connection not in AUTHED_USERS:
		return
	if data['type'] in TYPES.keys():
		t = threading.Thread(target=TYPES[data['type']](connection, data,))
		t.start()


class server(basic.LineReceiver):
	load_plugins()
	def connectionMade(self):
		for i in NEW_FUNCTIONS:
			i(self)
		self.time = int(time.time())
		print "Got new client!"
		CLIENTS.append(self)
	def close(self):
		print "CLOSE!"
		self.transport.loseConnection()
	def connectionLost(self, reason):
		print "Lost a client!"
		CLIENTS.remove(self)
		for i in LOST_FUNCTIONS:
			i(self)
	def dataReceived(self, line):
		print "received", repr(line)
		if line.startswith('<policy-file-request/>'):
			print "POLICY REQUEST"
			msg = "<?xml version=\"1.0\"?><cross-domain-policy><allow-access-from domain=\"*\" to-ports=\"%s\" /></cross-domain-policy>\x00"%PORT
			self.transport.write(msg)
			return
		try:
			a = line.split("\r\n")
			del a[-1]
			for i in a:
				j = json.loads(i)
				messageHnd(self, j)
    		except Exception as what:
				self.message({"type":"error","message":"%s"%what.__str__()})
	def message(self, message):
		if type(message) != str():
			message = json.dumps(message)
			self.transport.write(message + '\n')
	def getInfo(self):
		return {"gid":self.gid, "name":self.name,"color":self.color,"rating":self.rating,"status":self.status,"money":self.money}


from twisted.internet import protocol
from twisted.application import service, internet
factory = protocol.ServerFactory()
factory.protocol = server
factory.clients = []
application = service.Application("App")
internet.TCPServer(PORT, factory, interface=SERVER).setServiceParent(application)