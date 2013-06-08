#plugin+
from hashlib import md5

AUTHED_USERS = []

def auth(connection, data):
	if data['id'] and data['pass']:
		real = md5(API_ID+"_"+str(data['id'])+"_"+SECRET).hexdigest()
		if real == data['pass']:
			connection.authed = True
			chkAuth(data['id'], connection)
		else:
			connection.message({'type':'auth','data':'error'})
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
	if setUserInfo(connection):
		connection.message({"type":"auth","state":"success","user_info":connection.getInfo()})
		return
	connection.message({"type":"auth","state":"not_registered"})

def setUserInfo(connection):
	user_info = database.getData('SELECT * FROM users WHERE uid=%s'%connection.uid)
	if user_info:
		user_info = user_info[0]
		if user_info[7] == 1:
			connection.message({"type":"auth","state":"banned"})
			connection.transport.loseConnection()
			return
		connection.gid = user_info[0]
		connection.name = user_info[2]
		connection.color = user_info[3]
		connection.rating = user_info[4]
		connection.status = user_info[5]
		connection.money = user_info[6]
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
		connection.message({"type":"getUserProfile","status":"Not found"})
		return
	info = {}
	info['gid'] = db_info[0]
	info['name'] = db_info[2]
	info['color'] = db_info[3]
	info['rating'] = db_info[4]
	info['status'] = db_info[5]
	connection.message({"type":"getUserProfile","status":"success","info":info})
	return
def regUser(connection,data):
	if not connection.authed:
		return
	sql = "INSERT INTO `avatars`.`users` (`uid`, `name`, `status`) VALUES (%s,'%s','%s');"%(connection.uid,data['name'],data['status'])
	if database.exec_data(sql):
		setUserInfo(connection)
		connection.message({"type":"regUser","state":"success","usr_info":connection.getInfo()})
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