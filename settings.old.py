#-*- coding=utf8 -*-
import os
import sys

#########
#路径配置
#########
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
print ROOT_PATH
sys.path.append(ROOT_PATH)
APPENDED_PATH = ['modules', 'sns_api', 'modules/opensocial']
for module in APPENDED_PATH:
    s = os.path.join(ROOT_PATH, module)
    sys.path.insert(0, s)
    
SERVER_PLATFORM = 'renren'

#########
#日志文件配置
#########
import logging
from logging.handlers import RotatingFileHandler

'''
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
import psycopg2
import psycopg2.extras
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB
import time

dbhost = "localhost"
dbname = "kakazoo"
#dbuser = "kakaadmin"
#dbpwd = "xiankaka"
dbuser = "postgres"
dbpwd = "postgres"

#conn = psycopg2.connect(host=dbhost,database=dbname,user=dbuser,password=dbpwd)
#db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

DBPARAMS ={  
    'creator': psycopg2,
    'failures':(psycopg2.InterfaceError, ),
    'host': dbhost,   
    'user': dbuser,   
    'password': dbpwd,   
    'database': dbname,  
}  

pool = PooledDB(maxusage=100,  **DBPARAMS)
#pool = PersistentDB(maxusage=100,  **DBPARAMS)
