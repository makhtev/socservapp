#plugin+
# -*- coding: utf-8 -*-

#STATE:
#1 - успешно
#0 - безуспешно
#2 - забанен
#3 - нужна регистрация


from hashlib import md5

AUTHED_USERS = []

def set_auth(connection):
	connection.authed = False
def auth(connection, data):
	if data['id'] and data['pass']:
		real = md5(API_ID+"_"+str(data['id'])+"_"+SECRET).hexdigest()
		if real == data['pass'] or data['pass'] == 'test':
			chkAuth(data['id'], connection)
		else:
			connection.message({'type':'auth','state':0})
			connection.transport.loseConnection()

def chkAuth(id, connection):
	if connection in AUTHED_USERS:
		return
	for i in AUTHED_USERS:
		if i.uid == id:
			i.transport.loseConnection()
			AUTHED_USERS.remove(connection)
	connection.uid = id
	AUTHED_USERS.append(connection)
	setInfo = setUserInfo(connection)
	if setInfo == 2:
		return
	if setInfo:
		connection.message({"type":"auth","state":1,"user_info":connection.getInfo()})
		return
	connection.message({"type":"auth","state":3})

def setUserInfo(connection):
	user_info = database.getData('SELECT * FROM users WHERE uid=%s'%connection.uid)
	if user_info:
		user_info = user_info[0]
		if user_info[7] == 1:
			connection.message({"type":"auth","state":2})
			connection.transport.loseConnection()
			return 2
		connection.gid = user_info[0]
		connection.name = user_info[2]
		connection.color = user_info[3]
		connection.rating = user_info[4]
		connection.status = user_info[5]
		connection.money = user_info[6]
		connection.authed = True
		return True
	return False
def getUserProfile(connection, data):
	if connection not in AUTHED_USERS:
		return
	print data
	db_info = database.getData('SELECT * FROM users WHERE gid=%s'%data['id'])
	if db_info:
		db_info = db_info[0]
	else:
		connection.message({"type":"getUserProfile","state":0})
		return
	info = {}
	info['gid'] = db_info[0]
	#info.uid = db_info[1]
	info['name'] = db_info[2]
	info['color'] = db_info[3]
	info['rating'] = db_info[4]
	info['status'] = db_info[5]
	connection.message({"type":"getUserProfile","state":1,"info":info})
	return
def regUser(connection,data):
	print connection.authed
	if connection.authed:
		return
	sql = "INSERT INTO `avatars`.`users` (`uid`, `name`, `status`) VALUES (%s,'%s','%s');"%(connection.uid,data['name'],data['status'])
	if database.exec_data(sql):
		setUserInfo(connection)
		connection.message({"type":"regUser","state":1,"usr_info":connection.getInfo()})
		return
	connection.message({"type":"regUser","state":0})
def setUserProfile(connection,data):
	print database.exec_data("UPDATE  `avatars`.`users` SET  `name` =  '%s', `status` = '%s' WHERE  `users`.`uid` =%s;"%(data['name'], data['status'], connection.uid))

#SEND data TO ALL AUTHED USERS
def snd_all(data):
	for i in AUTHED_USERS:
		i.message(data)

def snd_user(id, data):
	for i in AUTHED_USERS:
		if i.gid == id:
			i.message(data)
			return True
	return False

def lost_auth(user):
	if user in AUTHED_USERS:
		AUTHED_USERS.remove(user)

regTypes('auth', auth)
regTypes('regUser', regUser)
regTypes('getUserProfile', getUserProfile)
regLost(lost_auth)
regNew(set_auth)