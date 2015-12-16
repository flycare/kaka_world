import psycopg2
import psycopg2.extras

dbhost = '1.85.2.109'
dbname = 'kakazoo'
dbuser = 'kakaadmin'
dbpwd = 'xiankaka'

def createDb():
    conn = psycopg2.connect(host=dbhost,database=dbname,user=dbuser,password=dbpwd)
    db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return db,conn

def getItemTableName(playerId):
    #return 'item'+str(playerId%10)[-1]
    return 'item'+str(playerId%10)

def getItems():
    db,conn = createDb()
    db.execute("SELECT * FROM item")
    list = db.fetchall()
    return list

count = 0
db,conn = createDb()

def addItem(item):
    add_sql = 'INSERT INTO %s (x,y,item_id,user_id,created_time) VALUES \
        (%s,%s,%s,%s,%s)' % (getItemTableName(item['user_id']),item['x'],item['y'],item['item_id'],item['user_id'],item['created_time'])
    print add_sql
    db.execute(add_sql)
    conn.commit()

print 'are you sure for partion from',dbhost,'?(y or n)'
input = raw_input()

if('y' == input):
    print 'partion start ...'
    itemlist = getItems()
    for item in itemlist:
        addItem(item)
    print 'partion done'
else:
    print 'return false'