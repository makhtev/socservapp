#plugin+
# -*- coding: utf-8 -*-
import MySQLdb
class mysql_db:
	
	def __init__(self):
		pass
	def getData(self, sql):
		self.connect()
		self.cursor.execute(sql)
		response = self.cursor.fetchall()
		self.disconnect()
		return response
	def exec_data(self, sql):
		self.connect()
		response = self.cursor.execute(sql)
		self.disconenct()
		return resposne
	def connect(self):
		self.db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME, charset='utf8')
		self.cursor = self.db.cursor()
	def disconnect(self):
		self.db.close()

database = mysql_db()