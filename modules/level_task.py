#-*- coding=utf8 -*-
from settings import *

from config.systemReward_config import *
from config.task_config import *

import time
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool


def getLevelTaskById(db,conn,playerId):
    db.execute("SELECT * FROM level_task WHERE player_id = %s",(playerId,))
    level_task = db.fetchone()
    return level_task


def updateLevelTaskById(db,conn,playerId,taskstr):
    db.execute("UPDATE level_task set task_info = %s WHERE player_id = %s",(taskstr,playerId))
    conn.commit()


#初始化获取玩家等级任务信息
@getOneDBConn
def getLevelTaskInfo(db,conn,playerId):
    level_task = getLevelTaskById(db,conn,playerId)
    
    if not level_task:
        taskinfo = ''
        db.execute("INSERT INTO level_task(player_id,task_info) VALUES(%s,%s)", (playerId,taskinfo))
        conn.commit()
    else:
        taskinfo = level_task['task_info']
    return taskinfo


#更新玩家等级任务信息
@getOneDBConn
def updateLevelTaskInfo(db,conn,playerId,taskId,taskInfo):
    
    level_task = getLevelTaskById(db,conn,playerId)
    taskdict = __stringToDict(level_task['task_info'])
    
    taskId = int(taskId)
    if taskdict.has_key(taskId):
        taskdict[taskId] = taskInfo
        #update task
        taskstr = __dictToString(taskdict)
        updateLevelTaskById(db,conn,playerId,taskstr)
        return {'status':1,'task_id':taskId,'task_message':taskdict[taskId]}
    else:
        return {'status':0,'msg':'没有相应的等级任务'}

#完成玩家等级任务
@getOneDBConn
def finishLevelTask(db,conn,playerId,taskId):
    
    taskinfo = getLevelTaskById(db,conn,playerId)
    taskdict = __stringToDict(taskinfo['task_info'])
    
    taskId = int(taskId)
    if(taskdict.has_key(taskId)):
        taskdict.pop(taskId)
        
        propDict = db_tool.getAllProp(playerId)
        
        #任务奖励
        taskReward = TASK_AWARD_CONFIG[taskId]
        if taskReward.has_key('gb'):
            db_tool.addPropAndMoney(playerId,'2',taskReward['gb'])
        if taskReward.has_key('exp'):
            db_tool.addPropAndMoney(playerId,'3',taskReward['exp'])
        if taskReward.has_key('item'):
            for item in taskReward['item']:
                db_tool.__addPropItem(propDict,item['definitionID'],item['num'])
            db_tool.saveAllProp(playerId,propDict)
        
        #更新任务状态
        taskstr = __dictToString(taskdict)
        updateLevelTaskById(db,conn,playerId,taskstr)
        player = db_tool.__getPlayerById(playerId)
        
        #触发的新任务
        triggerTasks = addTriggerTask(playerId,taskId)
        
        return{'status':1,'player':player,'bag':propDict,'task_id':taskId,'new_task':triggerTasks}
    else:
        return {'status':0,'msg':'没有相应的等级任务'}


def __stringToDict(propStr):
    collectionDict = dict()
    if len(propStr)>0:
        list = propStr.split('|')
        for each in list:
            theCollection = each.split(':')
            collectionDict[int(theCollection[0])] = str(theCollection[1])
    return collectionDict

def __dictToString(dict):
    theList = list()
    for key in dict:
        if dict[key]>=0:
            theList.append(str(key)+":"+str(dict[key]))
    collection = '|'.join(theList)
    return collection


#添加等级任务
@getOneDBConn
def addLevelTask(db,conn,playerId,level):
    
    level_task = getLevelTaskById(db,conn,playerId)
    taskdict = __stringToDict(level_task['task_info'])
    
    newTasks = []
    if TASK_CONFIG.has_key(level):
        
        newTasks = TASK_CONFIG[level]['task_list']
        for taskId in newTasks:
            taskdict[taskId]=''
        
        taskstr = __dictToString(taskdict)
        updateLevelTaskById(db,conn,playerId,taskstr)
        
    return newTasks

#任务触发任务
@getOneDBConn
def addTriggerTask(db,conn,playerId,taskId):
    level_task = getLevelTaskById(db,conn,playerId)
    taskdict = __stringToDict(level_task['task_info'])
    
    #触发的任务
    triggerTasks = []
    
    if TASK_TRIGGER_CONFIG.has_key(taskId):
        triggerTasks = TASK_TRIGGER_CONFIG[taskId]['task_list']
        for ataskId in triggerTasks:
            taskdict[ataskId]=''
        
        taskstr = __dictToString(taskdict)
        updateLevelTaskById(db,conn,playerId,taskstr)
    
    return triggerTasks