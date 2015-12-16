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

def clearData():
    db,conn = createDb()
    
    db.execute("delete from auction_event")
    
    db.execute("delete from collection")
    
    db.execute("delete from collection_list")
    
    db.execute("delete from daily_task")
    
    db.execute("delete from event_log")
    
    db.execute("delete from free_gift")
    
    db.execute("delete from item0")
    db.execute("delete from item1")
    db.execute("delete from item2")
    db.execute("delete from item3")
    db.execute("delete from item4")
    db.execute("delete from item5")
    db.execute("delete from item6")
    db.execute("delete from item7")
    db.execute("delete from item8")
    db.execute("delete from item9")
    
    db.execute("delete from pay")
    
    db.execute("delete from player")
    
    db.execute("delete from prop")
    
    db.execute("delete from produce")
    
    db.execute("delete from search_team")
    
    db.execute("delete from session")
    
    db.execute("delete from task")
    
    db.execute("delete from transaction")
    
    db.execute("delete from user_box")
    
    db.execute("delete from visit_friend")

    conn.commit()

print 'are you sure to delete from',dbhost,'?(y or n)'
input = raw_input()
#3.x for input
#input = input()
if('y' == input):
    print 'delete start ...'
    clearData()
    print 'delete done'
else:
    print 'return false'
