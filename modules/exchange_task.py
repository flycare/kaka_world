#-*- coding=utf8 -*-
from settings import *

from config.exchange_config import *

import time
import random
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool
import modules.player as player_module


def getExchangeLevelTaskIds(playerId):
    player = db_tool.__getPlayerById(playerId)
    level = player['level']
    ids = []
    if level <= 5:
        ids = EXCHANGE_LEVEL_TASK_CONFIG[5]
    elif level <= 10:
        ids = EXCHANGE_LEVEL_TASK_CONFIG[10]
    elif level <= 15:
        ids = EXCHANGE_LEVEL_TASK_CONFIG[15]
    elif level <= 20:
        ids = EXCHANGE_LEVEL_TASK_CONFIG[20]
    elif level <= 25:
        ids = EXCHANGE_LEVEL_TASK_CONFIG[25]
    
    return ids


#获得兑换任务信息
def getExchangeTaskInfo(playerId):
    taskInfo = getExchangeTask(playerId)
    
    #返回的任务ID
    retTaskId = 0
    
    taskIds = getExchangeLevelTaskIds(playerId)
    
    #没有相应的兑换任务
    if not taskIds:
        return retTaskId
    
    if not taskInfo:
        time_now = int(time.time())
        taskId = random.choice(taskIds)
        
        taskInfo = {}
        taskInfo['player_id'] = playerId
        taskInfo['create_time'] = time_now
        taskInfo['task_id'] = taskId
        taskInfo['status'] = 0
        
        saveExchangeTask(taskInfo)
        
        retTaskId = taskId
    else:
        if time_tool.isToday(taskInfo['create_time']):
            
            #今天是否已经兑换
            if taskInfo['status'] == 0:
                retTaskId = taskInfo['task_id']
            else:
                pass
        else:
            time_now = int(time.time())
            taskId = random.choice(taskIds)
            
            updTaskInfo = {}
            updTaskInfo['create_time'] = time_now
            updTaskInfo['task_id'] = taskId
            updTaskInfo['status'] = 0
            updateExchangeTask(playerId,updTaskInfo)
            
            retTaskId = taskId
    
    return retTaskId


#开始兑换
def startExchangeTask(playerId):
    propDict = db_tool.getAllProp(playerId)
    player = db_tool.__getPlayerById(playerId)
    player = player_module.__updateEnergy(player)
    
    taskInfo = getExchangeTask(playerId)
    taskId = taskInfo['task_id']
    
    if not EXCHANGE_TASK_CONFIG.has_key(taskId):
        return {'status':0,'msg':'没有相应的兑换任务 '+str(taskId)}
    
    needDefinitonList = EXCHANGE_TASK_CONFIG[taskId]['needDefinitonID']
    
    if not checkBag(playerId,needDefinitonList,propDict):
        return {'status':0,'msg':'不满足兑换条件 '+str(taskId)}
    
    rewardList = EXCHANGE_TASK_CONFIG[taskId]['reward']
    
    rewardGb = 0
    rewardExp = 0
    rewardEnergy = 0
    rewardDefinitionId = 0
    
    for reward in rewardList:
        rewardType = reward['type']
        rewardNum = reward['num']
        
        #金币
        if rewardType == 2:
            rewardGb = rewardNum
            player['gb'] += rewardNum
        #经验
        if rewardType == 3:
            rewardExp = rewardNum
            player['exp'] += rewardNum
        #能量
        elif rewardType == 4:
            rewardEnergy = rewardNum
            player['energy'] += rewardNum
        #物品
        else:
            rewardDefinitionId = rewardType
            db_tool.__addPropItem(propDict,rewardType,rewardNum)
        
    
    #更新player
    db_tool.__updatePlayer(playerId,{'gb':player['gb'],'exp':player['exp'],'energy':player['energy'],'last_energy_time':player['last_energy_time']})
    db_tool.saveAllProp(playerId,propDict)
    
    #更新兑换状态
    updTaskInfo = {}
    updTaskInfo['status'] = 1
    updateExchangeTask(playerId,updTaskInfo)
    
    return {'status':1,'reward':rewardList,'player':player,'bag':propDict}
    

#检查背包中是否有相应的物品
def checkBag(playerId,needDefinitonList,propDict):
    #检查背包
    for needDefiniton in needDefinitonList:
        definitionID = str(needDefiniton['definitionID'])
        num = needDefiniton['num']
        if propDict.has_key(definitionID) and propDict[definitionID]>=num:
            pass
        else:
            return False
            
    #扣除背包相应物品
    for needDefiniton in needDefinitonList:
        definitionID = str(needDefiniton['definitionID'])
        num = needDefiniton['num']
        db_tool.__subtractPropItem(propDict,definitionID,num)
    
    return True


@getOneDBConn
def saveExchangeTask(db,conn,taskInfo):
    fields = ','.join(taskInfo.keys())
    values = tuple(taskInfo.values())
    buildstr = ','.join(['%s']*len(taskInfo))
    sql = "insert into exchange_task (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()

@getOneDBConn
def updateExchangeTask(db,conn,playerId,taskInfo):
    fields = taskInfo.keys()
    values = taskInfo.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE exchange_task SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()
    
@getOneDBConn
def getExchangeTask(db,conn,playerId):
    db.execute("SELECT * FROM exchange_task WHERE player_id = %s",(playerId,))
    taskInfo = db.fetchone()
    return taskInfo