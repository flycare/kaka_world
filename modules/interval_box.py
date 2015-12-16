#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.box_config import *
import time
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool

    
#领取奖励
def getIntervalBoxReward(playerId):
    boxInfo = getIntervalBoxInfo(playerId)
    number = boxInfo['number']+1
    
    if not INTERVAL_BOX.has_key(number):
        return {'status':0,'msg':'getIntervalBoxReward : error number '}
    
    time_now = int(time.time())
    updateInfo = {}
    updateInfo['op_time'] = time_now
    updateInfo['number'] = number
    updateIntervalBoxInfo(playerId,updateInfo)
    
    prop = db_tool.getAllProp(playerId)
    rewardList = INTERVAL_BOX[number]['reward']
    for reward in rewardList:
        propId = reward['id']
        propNum = reward['num']
        db_tool.__addPropItem(prop,propId,propNum)
    db_tool.saveAllProp(playerId,prop)
    
    return {'status':1,'bag':prop,'op_time':updateInfo['op_time'],'number':number}
    

#获得限时箱子信息
@getOneDBConn
def getIntervalBoxInfo(db,conn,playerId):
    db.execute("SELECT * FROM interval_box WHERE player_id = %s",(playerId,))
    boxInfo = db.fetchone()
    
    time_now = int(time.time())
    if not boxInfo:
        boxInfo = {}
        boxInfo['player_id'] = playerId
        boxInfo['op_time'] = time_now
        boxInfo['number'] = 0
        saveIntervalBoxInfo(boxInfo)
    else:
        #强制转换
        boxInfo = dict(boxInfo)
        '''
        if not time_tool.isToday(boxInfo['op_time']):
            updateInfo = {}
            updateInfo['op_time'] = time_now
            updateInfo['number'] = 0
            updateIntervalBoxInfo(playerId,updateInfo)
            
            boxInfo['op_time'] = time_now
            boxInfo['number'] = 0
        '''
    return boxInfo

@getOneDBConn
def saveIntervalBoxInfo(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into interval_box (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()
    
@getOneDBConn
def updateIntervalBoxInfo(db,conn,playerId,info):
    fields = info.keys()
    values = info.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE interval_box SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()
