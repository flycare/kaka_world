#-*- coding=utf8 -*-
from settings import *

from config.visit_config import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool
import modules.random_tool as random_tool


@getOneDBConn
def getManyPlayer(db,conn,sns_ids):
    temp = []
    for each in sns_ids:
        temp.append('%s')
    sstr = ','.join(temp)
    db.execute("SELECT * FROM player WHERE sns_id in ("+sstr+")",sns_ids)
    players = db.fetchall()
    ret = []
    for each in players:
        temp = {'id':each['id'],
                 'sns_id':each['sns_id'],
                 #'gb':each['gb'],
                 #'kb':each['kb'],
                 #'energy':each['energy'],
                 'vip':each['vip'],
                 #'last_login_time':each['last_login_time'],
                 #'last_energy_time':each['last_energy_time'],
                 'exp':each['exp'],
                 'level':each['level'],
                 #'expand':each['expand']
                 }
        ret.append(temp)
        
        del temp
    return ret


# friends table
@getOneDBConn
def getFriendsInfo(db,conn,playerId,sns_ids):
    players = []
    if(sns_ids):
        players = getManyPlayer(sns_ids)
    
    visits = getVisitFriends(playerId)
    return {'status':1,'friends':players,'visit_info':visits}

@getOneDBConn
def getVisitFriends(db,conn,player_id):
    returnVal = {}
    db.execute("SELECT * FROM visit_friend WHERE player_id = %s",(player_id,))
    visitInfo = db.fetchone()
    if(not visitInfo):
        time_now = int(time.time())
        db.execute("INSERT INTO visit_friend(player_id,first_visit,daily_visit,visit_time) VALUES(%s,%s,%s,%s)",
                    (player_id,'','',time_now))
        conn.commit()
        returnVal['first_visit']=''
        returnVal['daily_visit']=''
    else:
        returnVal['first_visit']=visitInfo['first_visit']
        returnVal['daily_visit']=visitInfo['daily_visit']
        if not time_tool.isToday(visitInfo['visit_time']):
            daily_visit = ''
            todayTime = int(time.time())
            db.execute("UPDATE visit_friend set daily_visit = %s,visit_time = %s WHERE player_id = %s",(daily_visit,todayTime,player_id))
            conn.commit()
            returnVal['daily_visit']=[]
    return returnVal

#访问好友营地搜索礼物
@getOneDBConn
def visitFriend(db,conn,player_id,friend_id):

    db.execute("SELECT * FROM visit_friend WHERE player_id = %s",(player_id,))
    visitInfo = db.fetchone()
    
    first_visit = visitInfo['first_visit']
    daily_visit = visitInfo['daily_visit']
    visit_time = visitInfo['visit_time']

    todayTime = int(time.time())
    todayTimeStr = time.strftime("%Y%m%d",time.localtime(todayTime))
    visitTimeStr = time.strftime("%Y%m%d",time.localtime(visit_time))
    
    friend_id = str(friend_id)
    
    friendlist = friendstr2list(first_visit)
    dailylist = friendstr2list(daily_visit)

    #是否初次访问
    if(friend_id not in friendlist):
        friendlist.append(friend_id)
        db.execute("UPDATE visit_friend set first_visit = %s WHERE player_id = %s",(list2friendstr(friendlist),player_id))
        conn.commit()

        reward = addVisitReward(player_id,0)
        return{'status':1,'type':0,'reward':reward,'bag':db_tool.getAllProp(player_id)}
        
    #当日是否访问
    elif(friend_id not in dailylist):
        dailylist.append(friend_id)
        db.execute("UPDATE visit_friend set daily_visit = %s,visit_time = %s WHERE player_id = %s",(list2friendstr(dailylist),todayTime,player_id))
        conn.commit()
    
        reward = addVisitReward(player_id,1)
        return{'status':1,'type':1,'reward':reward,'bag':db_tool.getAllProp(player_id)}
    else:
        return{'status':0,'reward':'has get visit reward'}

def friendstr2list(friendStr):
    friendslist = []
    if len(friendStr)>0:
        friendslist = friendStr.split('|')
    return friendslist

def list2friendstr(friendlist):
    if(not friendlist):
        friendlist = list()
    return '|'.join(friendlist)

#0:初次访问
#1:每日访问
def addVisitReward(playerId,type):
    rewardInfo = {}
    if(type == 0):
        rewardInfo = FIRST_VISIT
    elif(type == 1):
        item = random_tool.getRandomItem('daily_visit_random_table',DAILY_VISIT)
        rewardInfo = item
    
    #print 'type=',type,' rewardinfo=',rewardInfo
    rewardType = rewardInfo['type']
    rewardNum = rewardInfo['num']
    reward = {rewardType:rewardNum}
    db_tool.addPropAndMoney(playerId,rewardType,rewardNum)
    return reward

