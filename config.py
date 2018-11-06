#encoding: utf-8

import os

DEBUG = True
SECRET_KEY = os.urandom(24) #加密，需要24位随机字符串

# 数据库
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'flask_chat'
USERNAME = 'root'
PASSWORD = '123456'
DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI