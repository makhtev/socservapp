#plugin+
# -*- coding: utf-8 -*-
CHATROOMS_DIR = GENERAL_CONFIG['chat']['dir']
CHATROOMS_FILE = GENERAL_CONFIG['chat']['chatrooms']
fp = open(CHATROOMS_DIR+'/'+CHATROOMS_FILE, 'r')
CHATROOMS = eval(fp.read())
fp.close()

CHATS = []

class chat:
	def __init__(self, obj):
		self.name = obj['name']
		self.users = []
		self.last_messages = []
	def addUser(self, user):
		if user.chat == self:
			user.message({"type":"enterChat","state":"Already in chat"})
			return
		if user.chat:
			user.chat.removeUser(user)
			return
		user.chat = self
		self.users.append(user)
		self.sendAll({"type":"newUser","gid":user.gid,"name":user.name,"color":user.color})
		user.message({"type":"enterChat","state":"success","last_messages":self.last_messages, "users":self.getUsers()})
	def removeUser(self, user):
		user.chat = False
		self.users.remove(user)
		self.sendAll({"type":"removeUser", "gid":user.gid})
		user.message({"type":"leaveChat", "state":"success"})
	def message(self,user,message):
		self.sendAll({"type":"message","from_gid":user.gid,"message":message})
	def getUsers(self):
		array = []
		for i in self.users:
			array.append({"gid":i.gid,"name":i.name,"color":i.color})
		return array
	def sendAll(self, data):
		for i in self.users:
			i.message(data)

for i in CHATROOMS:
	#print i['name']
	tmp = chat(i)
	CHATS.append(tmp)
def enterChat(connection, data):
	for i in CHATS:
		if i.name == data['name']:
			i.addUser(connection)
			return
	connection.message({"type":"enterChat","state":"Not Found"})
def leaveChat(connection, data):
	for i in CHATS:
		if connection in i.users:
			i.removeUser(connection)
			return
		connection.message({"type":"leaveChat","state":"Not Found"})
def getRooms(connection, data):
	array = []
	for i in CHATS:
		array.append(i.name)
	connection.message({"state":"success","chats":array})
def chatMessage(connection, data):
	if connection.chat:
		connection.chat.message(connection,data['message'])
		return
	connection.message({"type":"message","state":"Not in chat"})
def lost_chat(user):
	for i in CHATS:
		if user in i.users:
			i.removeUser(user)
def set_user(user):
	user.chat = False
regTypes('getRooms', getRooms)
regTypes('enterChat', enterChat)
regTypes('leaveChat', leaveChat)
regTypes('message',chatMessage)
regLost(lost_chat)
regNew(set_user)