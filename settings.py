#-*- coding=utf8 -*-
import os
import sys
import time
#########
#日志文件配置
#########
import logging
from logging.handlers import RotatingFileHandler

'''
#单一配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s',
    filename = os.path.join(os.getcwd(),"kakaZoo.log"),
    filemode = 'w',
)
'''

#定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)

fileHandler = RotatingFileHandler("logs/kakaZoo.log",mode='w',maxBytes=1*1024*1024,backupCount=5)
file_format = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
fileHandler.setFormatter(logging.Formatter(file_format))
fileHandler.setLevel(logging.DEBUG)

root_logger.addHandler(fileHandler)


#########
#数据库配置
#########
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB

#数据库类型 postgres or mysql
DATABASE_TYPE = "postgres"

dbhost = "localhost"
dbname = "kakazoo"
dbuser = "postgres"
dbpwd = "postgres"

import psycopg2
import psycopg2.extras
import MySQLdb

if DATABASE_TYPE == "postgres":
    DBPARAMS ={  
        'creator': psycopg2,
        'failures':(psycopg2.InterfaceError, ),
        'host': dbhost,   
        'user': dbuser,   
        'password': dbpwd,
        'database': dbname,
    }  
else:
    DBPARAMS ={  
        'creator': MySQLdb,
        'failures':(MySQLdb.InterfaceError, ),
        'host': dbhost,   
        'user': dbuser,   
        'passwd': dbpwd,   
        'db': dbname,  
    }

pool = PooledDB(mincached=5,maxcached=0,maxconnections=0,maxusage=0,**DBPARAMS)
#pool = PersistentDB(maxusage=0,  **DBPARAMS)

#获取cur and conn
def getCursorAndConnection():
    conn = pool.connection()
    if DATABASE_TYPE == "postgres":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    else:
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    return cur,conn

#########
#Memcache配置
#########
import memcache

#定义memcache服务地址
MEMCACHE_SERVER = ['192.168.3.111:11211']

#创建一个client
MEMCACHE_CLIENT = memcache.Client(MEMCACHE_SERVER,debug=1)

##########
#服务监听端口
##########
SERVER_PORT = 8081

PLATFORM = 'TEST'
