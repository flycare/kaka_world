#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.daily_config import *

import time
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool

#做每日任务
@getOneDBConn
def doDailyTask(db,conn,playerId,task_id):
    db.execute("SELECT * FROM daily_task WHERE player_id = %s",(playerId,))
    taskinfo = db.fetchone()
    taskdict = __stringToDict(taskinfo['task_info'])

    if(taskdict.has_key(task_id)):
        taskdict.pop(task_id)
        taskstr = __dictToString(taskdict)

        db.execute("UPDATE daily_task set task_info = %s WHERE player_id = %s",(taskstr,playerId))
        conn.commit()
        
        #任务奖励 100gb
        rewardType = '2'
        rewardNum = 100
        reward = {rewardType:rewardNum}
        db_tool.addPropAndMoney(playerId,rewardType,rewardNum)
        
        player = db_tool.__getPlayerById(playerId)
        playergb = player['gb']
    
        return{'status':1,'reward':reward,'playergb':playergb,'daily_task':taskdict,'task_id':task_id}
    else:
        return {'status':0,'msg':'has get daily task reward'}

#更新相关任务的次数
@getOneDBConn
def updateDailyTask(db,conn,playerId,task_id,status):
    db.execute("SELECT * FROM daily_task WHERE player_id = %s",(playerId,))
    taskinfo = db.fetchone()
    taskdict = __stringToDict(taskinfo['task_info'])
    taskdict[task_id] = status
    taskstr = __dictToString(taskdict)
    db.execute("UPDATE daily_task set task_info = %s WHERE player_id = %s",(taskstr,playerId))
    conn.commit()
    return {'status':1,'task_id':task_id,'task_message':taskdict[task_id]}

#获得每日任务信息
@getOneDBConn
def getTaskInfo(db,conn,playerId):
    db.execute("SELECT * FROM daily_task WHERE player_id = %s",(playerId,))
    taskinfo = db.fetchone()
    #默认任务状态
    default_info = '10001:0|10002:0|10003:0|10004:0'
    time_now = int(time.time())
    
    if(not taskinfo):
        db.execute("INSERT INTO daily_task(player_id,task_info,task_time) VALUES(%s,%s,%s)",
                    (playerId,default_info,time_now))
        conn.commit()
        return __stringToDict(default_info)
    else:
        #判断初始化任务时间
        task_time = taskinfo['task_time']
        todayTimeStr = time.strftime("%Y%m%d",time.localtime(time_now))
        taskTimeStr = time.strftime("%Y%m%d",time.localtime(task_time))
        
        if(taskTimeStr != todayTimeStr):
            db.execute("UPDATE daily_task set task_info = %s, task_time = %s WHERE player_id = %s",(default_info,time_now,playerId))
            conn.commit()
            return __stringToDict(default_info)
        else:
            return __stringToDict(taskinfo['task_info'])


def __stringToDict(propStr):

    collectionDict = dict()
    if len(propStr)>0:
        list = propStr.split('|')
        for each in list:
            theCollection = each.split(':')
            #print 'theCollection[0]------',theCollection[0]
            collectionDict[str(theCollection[0])] = int(theCollection[1])
    return collectionDict

def __dictToString(dict):
    theList = list()
    for key in dict:
        if dict[key]>=0:
            theList.append(str(key)+":"+str(dict[key]))
    collection = '|'.join(theList)
    return collection
