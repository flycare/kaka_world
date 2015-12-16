#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.materialProduction_config import *
import time
import math
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import player as player_module
import modules.interaction_event as interaction_event

#开始生产
def startProduce(playerId,machineId,produceId):
    produceInfo = getProduceList(playerId)
    time_now = int(time.time())
    
    if produceInfo.has_key(str(machineId)):
        return {'status':0,'msg':'producing now'}
    
    player = db_tool.__getPlayerById(playerId)
    #is vip check for 5#
    if(str(machineId) == '5'):
        if not player_module.isVIP(player):
            return {'status':0,'msg':'not vip for machine 5'}
    
    #check gb
    
    produce_detail_dict = dict()
    produce_detail_dict['produceId']=str(produceId)
    produce_detail_dict['startTime']=time_now
    produce_detail_dict['friends']=''
    produceInfo[str(machineId)]=produce_detail_dict
    
    updateProduce(playerId,produceInfo)
    return {'status':1,'machineId':machineId,'produceId':produceId,'startTime':time_now}

#取消生产
def cancelProduce(playerId,machineId):
    produceInfo = getProduceList(playerId)
    if produceInfo.has_key(str(machineId)):
        produceInfo.pop(str(machineId))
        updateProduce(playerId,produceInfo)
        return {'status':1,'machineId':machineId}
    else:
        return {'status':0,'msg':'no produce '+str(machineId)}

#完成生产
def finishProduce(playerId,machineId):
    #get from db
    produceInfo = getProduceList(playerId)
    produceId = produceInfo[str(machineId)]['produceId']
    startProduceTime = produceInfo[str(machineId)]['startTime']
    #search from config
    definitionId = PRODUCE_CONFIG[produceId]['definitionID']
    definitionNum = PRODUCE_CONFIG[produceId]['num']
    needProduceTime = PRODUCE_CONFIG[produceId]['time']*60
    time_now = int(time.time())
    if((time_now - startProduceTime) >= needProduceTime):
        #add bag
        prop = db_tool.getAllProp(playerId)
        db_tool.__addPropItem(prop,definitionId,definitionNum)
        db_tool.saveAllProp(playerId,prop)
        #remove produce
        produceInfo.pop(str(machineId))
        updateProduce(playerId,produceInfo)
        return {'status':1,'machineId':machineId,'produceId':produceId,'bag':prop}
    else:
        return {'status':0,'msg':'need more time to produce '}

#获取生产信息
def getProduceInfo(playerId):
    produceInfo = getProduceById(playerId)
    returnVal = {}
    returnVal['info'] = producestr2dict(produceInfo['info'])
    returnVal['level'] = produceInfo['level']
    return returnVal


#更新生产信息
@getOneDBConn
def updateProduce(db,conn,playerId,produceInfoDict):
    produceInfo=dict2producestr(produceInfoDict)
    db.execute("update produce set info = %s where user_id = %s",(produceInfo,playerId));
    conn.commit()

@getOneDBConn
def updateProduceLevel(db,conn,playerId,level):
    db.execute("update produce set level = %s where user_id = %s",(level,playerId));
    conn.commit()

#获取生产的信息
def getProduceList(playerId):
    produce = getProduceById(playerId)
    return producestr2dict(produce['info'])

@getOneDBConn
def getProduceById(db,conn,playerId):
    db.execute("select * from produce where user_id=%s",(playerId,));
    produce = db.fetchone()
    if produce:
        produce = dict(produce)
    else:
        produce = {}
        produce['user_id'] = playerId
        produce['info'] = ''
        produce['level'] = 1
        saveProduce(produce)
    return produce


#帮助生产
@getOneDBConn
def helpProduce(db,conn,playerId,snsName,snsPic,friendId,machineId):
    time_now = int(time.time())
    produceList = getProduceList(friendId)
    
    if not produceList.has_key(str(machineId)):
        return {'status':0,'msg':'no produce machineId for help'}
    
    produce_start_time = produceList[str(machineId)]['startTime']
    produce_id = produceList[str(machineId)]['produceId']
    produce_friends = produceList[str(machineId)]['friends']
    
    #是否有好友帮助
    if produce_friends:
        return {'status':0,'msg':'helpProduce completed'}
    
    produce_circle = PRODUCE_CONFIG[produce_id]['time']*60
    helpUserInfo = str(playerId)+'#'+snsName+'#'+snsPic
    
    #剩余时间
    remainTime = produce_circle-(time_now-produce_start_time)
    #减去总时间的10%
    subtractTime = produce_circle/10
    #subtractTime = int(math.ceil(remainTime*0.1))
    if remainTime < subtractTime:
        produce_start_time -= remainTime
    else:
        produce_start_time -= subtractTime
        
    produceList[str(machineId)]['friends'] = helpUserInfo
    produceList[str(machineId)]['startTime'] = produce_start_time
    
    updateProduce(friendId,produceList)
    
    #添加交互日志
    log_info = {}
    log_info['player_id'] = playerId
    log_info['player_name'] = snsName
    interaction_event.writeInteractionEventLog(log_info,friendId,3)
    
    return {'status':1,'pid':machineId,'produce':produceList[str(machineId)]}
    

#加速生产
def speedupProduce(playerId,param):
    machineId = param['machineId']
    useNum = param['use_num']
    needNum = param['need_num']
    
    player = db_tool.__getPlayerById(playerId)
    #验证KB
    costKb = 0
    if needNum>0:
        costKb = needNum*10
        player['kb'] -= costKb
        if player['kb'] < 0:
            return {'status':0,'msg':'not enough kb'}
    
    propDict = db_tool.getAllProp(playerId)
    prop_id='2020'
    
    #验证加速道具
    if useNum > 0:
        if not propDict.has_key(prop_id) or propDict[prop_id]<useNum :
            return {'status':0,'msg':'no or not enough '+prop_id}
    
    produceList = getProduceList(playerId)
    produce_start_time = produceList[str(machineId)]['startTime']
    
    #总使用道具数
    prop_num = useNum+needNum
    
    #加速时间一小时
    speedTime = PROP_CONFIG[int(prop_id)]['speed']
    
    #生产时间重新赋值
    produce_start_time -= speedTime*prop_num
    
    produceList[str(machineId)]['startTime'] = produce_start_time
    updateProduce(playerId,produceList)
    if useNum>0:
        db_tool.__subtractPropItem(propDict,prop_id,useNum)
        db_tool.saveAllProp(playerId,propDict)#update prop db
    if costKb > 0:
        db_tool.__updatePlayer(playerId,{'kb':player['kb']})
    
    return {'status':1,'bag':propDict,'pid':machineId,'produce':produceList[str(machineId)],'kb':player['kb']}
    
    
def producestr2dict(producestr):
    producedict = dict()
    if len(producestr)>0:
        list = producestr.split('|')
        for each in list:
            produce = each.split(':')
            produce_detail_dict = dict()
            produce_detail_dict['produceId'] = int(produce[1])
            produce_detail_dict['startTime'] = int(produce[2])
            if len(produce)>3:
                produce_detail_dict['friends'] = produce[3]
            else:
                produce_detail_dict['friends'] = ''
            producedict[str(produce[0])] = produce_detail_dict
    return producedict


def dict2producestr(producedict):
    producelist = list()
    for machineId in producedict:
        producelist.append(str(machineId)+":"+str(producedict[machineId]['produceId'])+":"+str(producedict[machineId]['startTime'])+":"+str(producedict[machineId]['friends']));
    collection = '|'.join(producelist)
    return collection

@getOneDBConn
def saveProduce(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into produce (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()
    
'''
def producestr2list(producestr):
    producelist = []
    if len(producestr)>0:
        list = producestr.split('|')
        for each in list:
            produce = each.split(':')
            producedict = dict()
            producedict['machineId'] = str(produce[0])
            producedict['produceId'] = str(produce[1])
            producedict['startTime'] = str(produce[2])
            producelist.append(producedict)
    return producelist
    
def list2producestr(producedict):
    producelist = list()
    for produce in producedict:
        if(len(produce))>0:
            producelist.append(str(produce['machineId'])+":"+str(produce['produceId'])+":"+str(produce['startTime']));
    collection = '|'.join(producelist)
    return collection
'''

