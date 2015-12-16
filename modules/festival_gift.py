#-*- coding=utf8 -*-
from settings import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool

#领取礼物
def receiveGift(playerId,giftId,giftNum):
    giftId = str(giftId)
    time_now = int(time.time())
    festivalInfo = getFestivalGift(playerId)
    
    #今日送过礼物的好友
    friends = ''
    #剩余礼物个数
    total_gifts = 0

    if not festivalInfo:
        giftDict = {giftId:giftNum}
        
        festivalInfo = {}
        festivalInfo['player_id'] = playerId
        festivalInfo['gifts'] = dict2str(giftDict)
        festivalInfo['presented_friends'] = ''
        festivalInfo['start_time'] = time_now
        
        saveFestivalGift(festivalInfo)
    else:
        giftDict = str2dict(festivalInfo['gifts'])
        
        if not time_tool.isToday(festivalInfo['start_time']):
            
            if giftDict.has_key(giftId):
                giftDict[giftId] += giftNum
            else:
                giftDict[giftId] = giftNum
            
            updateInfo = {}
            updateInfo['gifts'] = dict2str(giftDict)
            updateInfo['presented_friends'] = ''
            updateInfo['start_time'] = time_now
            updateFestivalGift(playerId,updateInfo)

        else:
            friends = festivalInfo['presented_friends']
    
    if giftDict.has_key(giftId):
        total_gifts = giftDict[giftId]
    
    return {'giftId':giftId,'giftNum':total_gifts,'friends':friends}


#赠送好友礼物
def presentGift(playerId,playerName,friendId,giftId):
    giftId = str(giftId)
    festivalInfo = getFestivalGift(playerId)
    
    presentedFriendsList = str2list(festivalInfo['presented_friends'])
    if friendId in presentedFriendsList:
        return {'status':0,'msg':'Only allow presentGift for once a day '}
    else:
        giftDict = str2dict(festivalInfo['gifts'])
        
        if giftDict[giftId] < 1:
            return {'status':0,'msg':'not enough gifts to present'}
        
        giftDict[giftId] -= 1
        presentedFriendsList.append(friendId)
        
        updateInfo = {}
        updateInfo['gifts'] = dict2str(giftDict)
        updateInfo['presented_friends'] = list2str(presentedFriendsList)
        updateFestivalGift(playerId,updateInfo)
        
        #给好友背包添加礼物
        propDict = db_tool.getAllProp(friendId)
        db_tool.__addPropItem(propDict,giftId,1)
        db_tool.saveAllProp(friendId,propDict)
        
        log_info = {}
        log_info['player_id'] = playerId
        log_info['player_name'] = playerName
        log_info['number'] = 1
        log_info['prop_id'] = giftId
        #添加赠送记录
        writeGiftEventLog(log_info,friendId)
        
        return {'status':1,'gifts':giftDict,'friends':updateInfo['presented_friends']}
        
    
def str2list(astr):
    alist = []
    if len(astr)>0:
        alist = astr.split('|')
    return alist


def list2str(alist):
    if(not alist):
        alist = list()
    return '|'.join(alist)

def str2dict(astr):
    adict = dict()
    if len(astr)>0:
        list = astr.split('|')
        for each in list:
            obj = each.split(':')
            adict[str(obj[0])] = int(obj[1])
    return adict

def dict2str(adict):
    alist = list()
    for key in adict:
        if adict[key]>0:
            alist.append(str(key)+":"+str(adict[key]))
    astr = '|'.join(alist)
    return astr


@getOneDBConn
def getFestivalGift(db,conn,playerId):
    db.execute("select * from festival_gift where player_id=%s",(playerId,))
    festivalInfo = db.fetchone()
    return festivalInfo

@getOneDBConn
def saveFestivalGift(db,conn,festivalInfo):
    fields = ','.join(festivalInfo.keys())
    values = tuple(festivalInfo.values())
    buildstr = ','.join(['%s']*len(festivalInfo))
    sql = "insert into festival_gift (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()
    
@getOneDBConn
def updateFestivalGift(db,conn,playerId,festivalInfo):
    fields = festivalInfo.keys()
    values = festivalInfo.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE festival_gift SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()

@getOneDBConn
def updateGiftEventStatus(db,conn,playerId):
    db.execute("UPDATE gift_event_log SET status=1 WHERE player_id=%s",(playerId,))
    conn.commit()

@getOneDBConn
def getGiftEventCounts(db,conn,playerId):
    db.execute("select count(id) from gift_event_log WHERE player_id=%s and status=0",(playerId,))
    num = db.fetchone()
    #return num[0]
    return num.values()[0]

@getOneDBConn
def writeGiftEventLog(db,conn,log_info,playerId):
    time_now = int(time.time())
    log_str = db_tool.__dictToString(log_info)
    db.execute("INSERT INTO gift_event_log(player_id,info,create_time) VALUES(%s,%s,%s)",(playerId,log_str,time_now))
    conn.commit()


@getOneDBConn
def getGiftEventLog(db,conn,playerId):
    db.execute("SELECT * FROM gift_event_log WHERE player_id = %s order by create_time desc limit 30",(playerId,))
    info = []
    
    try:
        logs = db.fetchall()
    except:
        return info
    
    for log in logs:
        temp = db_tool.__auctionStringToDict(log['info'])
        temp['time'] = log['create_time']
        temp['status'] = log['status']
        info.append(temp)
    
    return info
