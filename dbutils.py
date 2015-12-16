#!/usr/bin/env python

import psycopg2
import psycopg2.extras
from DBUtils.PooledDB import PooledDB
from settings import *

DBPARAMS ={  
    'creator': psycopg2,  #MySQLdb  
    #'failures': (psycopg2.InterfaceError, ),
    'host': 'localhost',   
    'user': 'kakaadmin',   
    'password': 'xiankaka',   
    'database': 'kakazoo',  
}  

pool = PooledDB(maxusage=100,  **DBPARAMS)

#print 'pool',pool
db = pool.connection()
#print 'db',db
#cur = db.cursor()

cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
print 'before cur',cur

cur.execute("SELECT * FROM \"treasure\"")

print 'execute cur',cur

result =cur.fetchone();
print result
#print result[2]
#print result['player_id']
#print result['sns_id']
cur.close()
print 'close cur',cur
