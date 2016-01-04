import sys
import json
import math
import urllib
import urllib2
import sqlite3
import os


baseUrl = "http://****"
#create a dictionary
defaultUrlParam = {
	"token": "****",
	"commonName": "N/A",
	"pageNo": 0,
	"pageSize": 20
}

def compose_request(cityCode, pageNo):
	param = defaultUrlParam.copy()
	param["pageNo"] = pageNo
	param["cityCode"] = cityCode
	urlParam = urllib.urlencode(param)
	url = baseUrl + "?" + urlParam
	req = urllib2.Request(url)
	return req

code = []
for line in open('cityCode.txt'):
	code.append(line)


###--- define functions related to database ---###
def db_init():
	global DB_FILE_PATH
	global TABLE_NAME
	DB_FILE_PATH = '/homeDatabase/guo_yao.db'
	TABLE_NAME = 'catalog'
	
def create_table(conn, sql):
	if sql is not None and sql != '':
		cu = conn.cursor()
		cu.execute(sql)
		conn.commit()
		cu.close()
	else:
		print('The [{}] is empty or None.'.format(sql))

def save(conn, sql, data):
	if sql is not None and sql != '':
		if data is not None:
			cu = conn.cursor()
			search_sql = "SELECT * FROM catalog WHERE goodsCode = ?"
			d = (data[0],)
			cu.execute(search_sql,d)
			r = cu.fetchall()
			if len(r)==0:
				cu.execute(sql, data)
				conn.commit()
			cu.close()
	else:
		print('The [{}] is empty or None.'.format(sql))

def fetchall(conn,sql):
	if sql is not None and sql != '':
		cu = conn.cursor()
		cu.execute(sql)
		r = cu.fetchall()
		if len(r)>0:
			for e in range(len(r)):
				for item in r[e]:
					print item.encode('utf-8')
		cu.close()
	else:
		print('The [{}] is empty or None.'.format(sql))

###--- create database file and table ---###
db_init()

table_list = ''' (goodsCode varchar(10) PRIMARY KEY, goodsName varchar(20), 
				commonName varchar(20), specifications varchar(10), manufactorName varchar(30), 
				approvalNumber varchar(30), dosageForm varchar(20), terminalName varchar(30), 
				provinceCode varchar(20), provinceName varchar(15), cityCode varchar(5), cityName varchar(15)
				)'''
creat_table_sql = "CREATE TABLE " + TABLE_NAME + table_list
save_sql = "INSERT INTO catalog values (?,?,?,?,?,?,?,?,?,?,?,?)"
fetchall_sql = "SELECT * FROM catalog"

key_list = ['goodsCode','goodsName','commonName','specifications','manufactorName','approvalNumber','dosageForm','terminalName','provinceCode','provinceName','cityCode','cityName']


conn = sqlite3.connect(DB_FILE_PATH)
create_table(conn, creat_table_sql)



###--- download medicine information and write into database file ---###
for city_nn in code[0:20]:
	city_nn = city_nn.rstrip()
	pageNo = 1
	req = compose_request(city_nn, pageNo)
	con = urllib2.urlopen(req)
	res = json.load(con) #automatically transform into dictionary
	con.close()

	if res["status"] != 0:
		print "something is wrong when downloading " + city_nn
		break

	totalCount = res["totalCount"]
	
	count = len(res["data"])
	data = res["data"]
	print ".",
	sys.stdout.flush()
	while count < totalCount:
		pageNo += 1
		req = compose_request(city_nn, pageNo)
		con = urllib2.urlopen(req)
		res = json.load(con)
		con.close()

		if res["status"] != 0:
			print "something is wrong when downloading " + city_nn
			break
		count += len(res["data"])
		data.extend(res["data"])
		print ".",
		sys.stdout.flush()  #make sure

	print "done. dowloading", city_nn, "with", len(data), "items"
	if len(data)>0:
		for dic in data:
			content = []
			for key in key_list:
				content.append(dic[key])
			content = tuple(content)
			save(conn,save_sql,content)
				
fetchall(conn,fetchall_sql)		
conn.close()

