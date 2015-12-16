#-*- coding=utf8 -*-
from settings import *

from config.exchange_config import *

import time
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool

#兑换物品
def startExchange(playerId,exchangeData):
    exchangeId = exchangeData['index']
    #检查兑换需要的物品并扣除物品
    propDict = db_tool.getAllProp(playerId)
    if not checkExchange(playerId,exchangeId,propDict):
        return {'status':0,'msg':'不满足兑换条件 or 活动结束 '+str(exchangeId)}
    #给玩家奖励
    propId = EXCHANGE_CONFIG[exchangeId]['goalDefinitionID']
    propNum = 1
    db_tool.__addPropItem(propDict,propId,propNum)
    db_tool.saveAllProp(playerId,propDict)
    return {'status':1,'exchangeId':exchangeId,'exchangeData':exchangeData,'num':propNum,'definitionId':propId,'bag':propDict}

#检查兑换条件是否满足
def checkExchange(playerId,exchangeId,propDict):
    needDrawingList = EXCHANGE_CONFIG[exchangeId]['drawingDefinitonID']
    needMaterailList = EXCHANGE_CONFIG[exchangeId]['materailDefinitonID']
    end_time_str = EXCHANGE_CONFIG[exchangeId]['end_time']
    end_time = time_tool.str2sec(end_time_str)
    
    time_now = int(time.time())
    
    #判断兑换活动时间
    if time_now > end_time:
        return False
        
    #检查背包
    for needDrawing in needDrawingList:
        definitionID = str(needDrawing['definitionID'])
        num = needDrawing['num']
        if propDict.has_key(definitionID) and propDict[definitionID]>=num:
            pass
        else:
            return False
            
    for needMaterail in needMaterailList:
        definitionID = str(needMaterail['definitionID'])
        num = needMaterail['num']
        if propDict.has_key(definitionID) and propDict[definitionID]>=num:
            pass
        else:
            return False
    
    #扣除背包相应物品
    for needDrawing in needDrawingList:
        definitionID = str(needDrawing['definitionID'])
        num = needDrawing['num']
        db_tool.__subtractPropItem(propDict,definitionID,num)
    
    for needMaterail in needMaterailList:
        definitionID = str(needMaterail['definitionID'])
        num = needMaterail['num']
        db_tool.__subtractPropItem(propDict,definitionID,num)
        
    #db_tool.saveAllProp(playerId,propDict)
    
    return True