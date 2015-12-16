#-*- coding=utf8 -*-
import random
import traceback
import hashlib
from settings import *

import modules.memory_cache as memory_cache

#########
#装饰器
#########

def getOneDBConn(func):
    def decoFun(*arg):
        try:
            cur,conn = getCursorAndConnection()
            execFun=func(cur,conn,*arg)
            return execFun
        except Exception,e:
            exstr = traceback.format_exc()
            root_logger.error(exstr)
        finally:
            cur.close() # or del cur
            conn.close() # or del db
    return decoFun

# player table
@getOneDBConn
def __getPlayer(db,conn,sns_id):
    db.execute("SELECT * FROM player WHERE sns_id = %s",(sns_id,))
    player = db.fetchone()
    if  not player:
        return 0
    return dict(player)

   
@getOneDBConn
def __getPlayerById(db,conn,playerId):
    #root_logger.debug('__getPlayerById playeri_d='+str(playerId))
    db.execute("SELECT * FROM player WHERE id = %s",(playerId,))
    player = db.fetchone()
    if not player:
        return 0
    return dict(player)


@getOneDBConn
def __updatePlayer(db,conn,playerId,playerInfo):
    fields = playerInfo.keys()
    values = playerInfo.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE player SET %s WHERE %s"%(setField,"id = %s")
    #print sql
    db.execute(sql,setValue)
    conn.commit()
    return True


@getOneDBConn
def __getSearchTeam(db,conn,playerId):
    db.execute("SELECT * FROM search_team WHERE user_id = %s",(playerId,))
    searchTeam = db.fetchone()
    return searchTeam['last_start_time'],searchTeam['area'],searchTeam['friends']

@getOneDBConn
def __updateSearchTeam(db,conn,playerId,last_start_time):
    db.execute("UPDATE search_team set last_start_time = %s WHERE user_id = %s",(last_start_time,playerId))
    conn.commit()

@getOneDBConn
def __updateSearchTeamInfo(db,conn,playerId,last_start_time,friends):
    db.execute("UPDATE search_team set last_start_time = %s , friends= %s WHERE user_id = %s",(last_start_time,friends,playerId))
    conn.commit()

# Prop table 
@getOneDBConn
def getAllProp(db,conn,playerId):
    
    db.execute("SELECT * FROM prop WHERE user_id = %s",(playerId,))
    propInfo = db.fetchone()
    if  not propInfo:
        propStr='13000500:1|13000520:1|10000:10|10010:10|10020:10|10030:10|2020:10'
        db.execute("INSERT INTO prop(user_id,props,capacity) VALUES(%s,%s,%s)",(playerId,propStr,120))
        conn.commit()
    else:
        propStr=propInfo['props']
    
    props=__stringToDict(propStr)

    return props
    
    
@getOneDBConn
def saveAllProp(db,conn,playerId,dict):
    str=__dictToString(dict)
    db.execute("UPDATE prop set props = %s WHERE user_id = %s",(str,playerId))
    conn.commit()
    
    
def __addPropItem(dict,prop_id,prop_num):
    #not update db
    if dict.has_key(str(prop_id)):
        dict[str(prop_id)]+=prop_num
    else:
        dict[str(prop_id)]=prop_num

def __subtractPropItem(dict,prop_id,prop_num):
    if dict.has_key(str(prop_id)):
        dict[str(prop_id)]-=prop_num
    else:
        dict[str(prop_id)]=0
        #throw error


def __auctionStringToDict(propStr):
    collectionDict = dict()
    if len(propStr)>0:
        list = propStr.split('|')
        for each in list:
            theCollection = each.split(':')
            collectionDict[str(theCollection[0])] = str(theCollection[1])
    return collectionDict


def __stringToDict(propStr):
    collectionDict = dict()
    if len(propStr)>0:
        list = propStr.split('|')
        for each in list:
            theCollection = each.split(':')
            collectionDict[str(theCollection[0])] = int(theCollection[1])
    return collectionDict

def __dictToString(dict):
    theList = list()
    for key in dict:
        if dict[key]>0:
            theList.append(str(key)+":"+str(dict[key]))
    collection = '|'.join(theList)
    return collection


# Collection table 
@getOneDBConn
def updateCollection(db,conn,status,playerId):
    db.execute("UPDATE collection set status = %s WHERE user_id = %s",(status,playerId))
    conn.commit()
    
@getOneDBConn
def updateCollectionList(db,conn,status,playerId):
    db.execute("UPDATE collection_list set status = %s WHERE user_id = %s",(status,playerId))
    conn.commit()

@getOneDBConn
def __getPlayerCollection(db,conn,playerId):
    db.execute("SELECT * FROM collection WHERE user_id = %s",(playerId,))
    collection = db.fetchone()
    returnVal = {}
    if collection:
        returnVal['uid'] = collection['user_id']
        returnVal['status'] = collection['status']

    else:
        db.execute("INSERT INTO collection(status,user_id) VALUES(%s,%s)",('',playerId,))
        conn.commit()
        returnVal['uid'] = playerId
        returnVal['status'] = ""
    return returnVal

@getOneDBConn
def __getPlayerCollectionList(db,conn,playerId):
    db.execute("SELECT * FROM collection_list WHERE user_id = %s",(playerId,))
    collection = db.fetchone()
    returnVal = {}
    if collection:
        returnVal['uid'] = collection['user_id']
        returnVal['status'] = collection['status']
    else:
        db.execute("INSERT INTO collection_list(status,user_id) VALUES(%s,%s)",('',playerId,))
        conn.commit()
        returnVal['uid'] = playerId
        returnVal['status'] = ""
    return returnVal


# item table and map info
@getOneDBConn
def getMapsbyPlayerId(db,conn,playerId,habitatId):

    search_sql = 'SELECT * FROM %s WHERE user_id = %s and habitat= %s' % (getItemTableName(playerId),playerId,habitatId)
    db.execute(search_sql)
    try:
        infos = db.fetchall()
    except:
        infos = []
    items = __parseItems(infos)

    return items

def __parseItems(items):
    returnVal = []
    for each in items:
        friendsDict = {}
        if each['friends']:
            friendsDict = __auctionStringToDict(each['friends'])
        returnVal.append({'id':each['id'],
                          'definitionId':each['item_id'],
                          'row':each['x'],
                          'col':each['y'],
                          'time':each['created_time'],
                          'detail':each['detail'],
                          'habitat':each['habitat'],
                          'friends':friendsDict})
    return returnVal

@getOneDBConn
def __getItem(db,conn,player_id,id):
    search_sql = 'SELECT * FROM %s WHERE id = %s' % (getItemTableName(player_id),id)
    db.execute(search_sql)
    item = db.fetchone()
    returnVal = {}
    returnVal['id'] = item['id']
    returnVal['x'] = item['x']
    returnVal['y'] = item['y']
    returnVal['definitionId'] = item['item_id']
    returnVal['user_id'] = item['user_id']
    returnVal['created_time'] = item['created_time']
    returnVal['habitat'] = item['habitat']
    returnVal['friends'] = item['friends']
    return returnVal

#lock and get
def lockItem(db,conn,player_id,id):
    search_sql = 'SELECT * FROM %s WHERE id = %s for update' % (getItemTableName(player_id),id)
    db.execute(search_sql)
    item = db.fetchone()
    returnVal = {}
    returnVal['id'] = item['id']
    returnVal['x'] = item['x']
    returnVal['y'] = item['y']
    returnVal['definitionId'] = item['item_id']
    returnVal['user_id'] = item['user_id']
    returnVal['created_time'] = item['created_time']
    returnVal['habitat'] = item['habitat']
    returnVal['friends'] = item['friends']
    return returnVal

@getOneDBConn
def updateItem(db,conn,player_id,id,info):
    updateItemById(db,conn,player_id,id,info)
    
def updateItemById(db,conn,player_id,id,info):
    fields = info.keys()
    values = info.values()
    values.append(id)
    setField = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE %s SET %s WHERE %s"%(getItemTableName(player_id),setField,"id = %s")
    
    db.execute(sql,setValue)
    conn.commit()
    
@getOneDBConn
def __updateItemDetail(db,conn,player_id,id,item_detail):
    updateInfo = {'detail':item_detail}
    updateItemById(db,conn,player_id,id,updateInfo)

    
@getOneDBConn
def updateMapItemsXY(db,conn,player_id,habitatId,items):
    itemTable = getItemTableName(player_id)
    
    paramList = []
    for item in items:
        itemList = []
        itemList.append(item['row'])
        itemList.append(item['col'])
        itemList.append(item['id'])
        paramList.append(tuple(itemList))
    
    #list append value 并转换成tuple使用
    if paramList:
        update_sql = 'UPDATE '+itemTable+' set x = %s,y = %s WHERE id = %s'
        db.executemany(update_sql,tuple(paramList))
        conn.commit()
    
    return items


#添加多个地图信息
@getOneDBConn 
def addMapItemList(db,conn,playerId,habitatId,items):
    itemTable = getItemTableName(playerId)
    time_now = int(time.time())
    
    for item in items:
        #用于组装SQL
        prefix_sql = 'INSERT INTO %s (x,y,item_id,user_id,created_time,habitat) VALUES (%s,%s,%s,%s,%s,%s)'
        suffix_sql = (itemTable,item['row'],item['col'],item['definitionId'],playerId,0,habitatId)
        
        if DATABASE_TYPE == "postgres":
            prefix_sql = prefix_sql+'RETURNING id'
            add_sql = prefix_sql % suffix_sql
            db.execute(add_sql)
            new_item = db.fetchone()
            item['id'] = new_item[0]
        else:
            add_sql = prefix_sql % suffix_sql
            db.execute(add_sql)
            item['id'] = db.lastrowid
        
    conn.commit()
    
    return items


#添加一个地图信息
@getOneDBConn 
def addMapItem(db,conn,playerId,habitatId,item):
    time_now = int(time.time())

    prefix_sql = 'INSERT INTO %s (x,y,item_id,user_id,created_time,habitat) VALUES (%s,%s,%s,%s,%s,%s)'
    suffix_sql = (getItemTableName(playerId),item['row'],item['col'],item['definitionId'],playerId,0,habitatId)
    
    if DATABASE_TYPE == "postgres":
        prefix_sql = prefix_sql+'RETURNING id'
        add_sql = prefix_sql % suffix_sql
        db.execute(add_sql)
        new_item = db.fetchone()
        item['id'] = new_item[0]
    else:
        add_sql = prefix_sql % suffix_sql
        db.execute(add_sql)
        item['id'] = db.lastrowid
    
    conn.commit()
    
    return item
    
@getOneDBConn 
def delMapItems(db,conn,playerId,habitatId,items):

    itemTable = getItemTableName(playerId)

    itemIds = []
    for item in items:
        itemIds.append(str(item['id']))

    if itemIds:
        del_sql = 'DELETE FROM %s WHERE id in (%s)' % (itemTable,','.join(itemIds))
        db.execute(del_sql)
        conn.commit()

    return items
    

#-----------task table-----------
@getOneDBConn
def __getTaskStatus(db,conn,playerId):
    db.execute("SELECT * FROM task WHERE user_id = %s",(playerId,))
    task = db.fetchone()
    collection = task['collection']
    return collection

    
@getOneDBConn
def getGlobalDefinitionNum(db,conn,definition_id):
    db.execute("SELECT * FROM global_achievement WHERE definitionId = %s",(definition_id,))
    item = db.fetchall()
    if not item:
        db.execute("INSERT INTO global_achievement(definitionId,num) VALUES(%s,%s)",(definition_id,1))
        num=1
    else:
        db.execute("UPDATE global_achievement SET num = num+1 WHERE definitionId = %s",(definition_id))
        num = item["num"]
    conn.commit()
    return num


def md5(str):
    m = hashlib.md5(str)
    return m.hexdigest()


#----------event_log table-------------
@getOneDBConn
def writeEventLog(db,conn,log_info,playerId):
    time_now = int(time.time())
    log_str = __dictToString(log_info)
    db.execute("INSERT INTO event_log(type,user_id,info,create_time) VALUES(%s,%s,%s,%s)",(1,playerId,log_str,time_now))
    conn.commit()
    
    #clear cache
    memory_cache.setAuctionEventLogCache(playerId,None)

@getOneDBConn
def getEventLog(db,conn,e_type,playerId):
    #先从cache中获取
    info = memory_cache.getAuctionEventLogCache(playerId)
    if info:
        return info
        
    db.execute("SELECT * FROM event_log WHERE type = %s AND user_id = %s order by create_time desc limit 16",(e_type,playerId))
    info = []
    try:
        logs = db.fetchall()
        '''
        #删除过期数据
        if len(logs) > 16:
            #evengLog = logs[15]
            evengLog = logs.pop()
            db.execute("delete from event_log where user_id = %s and create_time < %s",(evengLog['user_id'],evengLog['create_time']))
            conn.commit()
        '''
    except:
        return info
    for log in logs:
        temp = __auctionStringToDict(log['info'])
        temp['time'] = log['create_time']
        info.append(temp)
    
    #set cache
    memory_cache.setAuctionEventLogCache(playerId,info)
    
    return info


#加道具或钱
@getOneDBConn
def addPropAndMoney(db,conn,playerId,rewardType,rewardNum):
    player = __getPlayerById(playerId)
    playerkb = player['kb']
    playergb = player['gb']
    playerexp = player['exp']
    playerenergy = player['energy']
    
    if str(rewardType) == '1':
        #add KB
        totalkb = playerkb+rewardNum
        bool= __updatePlayer(playerId,{'kb':totalkb})
    elif str(rewardType) == '2':
        #add GB
        totalgb = playergb+rewardNum
        bool= __updatePlayer(playerId,{'gb':totalgb})
    elif str(rewardType) == '3':
        #add exp
        totalexp = playerexp+rewardNum
        bool= __updatePlayer(playerId,{'exp':totalexp})
    elif str(rewardType) == '4':
        #add energy
        totalenergy = playerenergy+rewardNum
        bool= __updatePlayer(playerId,{'energy':totalenergy})
    else:
        #add prop
        prop = getAllProp(playerId)
        __addPropItem(prop,rewardType,rewardNum)
        saveAllProp(playerId,prop)

#通过playerId获取分表名
def getItemTableName(playerId):
    #return 'item'+str(playerId)[-1]
    #key = playerId/10000
    #return 'item'+str(key)
    return 'item'+str(playerId%10)
