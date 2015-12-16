#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.alchemy_config import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.interaction_event as interaction_event

import random

#开始炼化
@getOneDBConn
def startAlchemy(db,conn,playerId,alchemyId):
    
    if not ALCHEMY_CONFIG.has_key(alchemyId):
        return {'status':0,'msg':'no alchemyId '+alchemyId}
    
    formulaList = ALCHEMY_CONFIG[alchemyId]['formula']
    needLevel = ALCHEMY_CONFIG[alchemyId]['level']
    
    #背包数据
    prop = db_tool.getAllProp(playerId)
    #验证等级
    player = db_tool.__getPlayerById(playerId)
    if player['level'] < needLevel:
        return {'status':0,'msg':'alchemy need level '+str(needLevel)}
        
    for formula in formulaList:
        
        neetDefinitionId = formula['definitionID']
        neetDefinitionIdNum = formula['num']

        #验证炼化材料
        if not prop.has_key(str(neetDefinitionId)) or prop[str(neetDefinitionId)] < neetDefinitionIdNum:
            return {'status':0,'msg':'alchemy need more definitionId '+str(neetDefinitionId)}
    
        db_tool.__subtractPropItem(prop,neetDefinitionId,neetDefinitionIdNum)
    
    #正在或等待炼化的信息
    alchemyInfoList = getAlchemyInfo(playerId)
    alchemyTime = getAlchemyTime(alchemyInfoList)
    alchemydict = {'id':alchemyId,'time':alchemyTime,'friends':''}
    alchemyInfoList.append(alchemydict)
    
    updateAlchemy(playerId,alchemyInfoList)
    db_tool.saveAllProp(playerId,prop)
    return {'status':1,'time':alchemyTime,'alchemyId':alchemyId,'bag':prop}

#完成炼化
@getOneDBConn
def finishAlchemy(db,conn,playerId,alchemyId):
    
    #正在或等待炼化的信息
    alchemyInfoList = getAlchemyInfo(playerId)
    
    for alchemy in alchemyInfoList:
        if(alchemy['id'] == alchemyId):
            finishAlchemy = alchemy
            break;
    
    if not finishAlchemy:
        return {'status':0,'msg':'err alchemyId for finishAlchemy'}

    needTime = ALCHEMY_CONFIG[alchemyId]['time']
    alchemyTime = finishAlchemy['time']
    helpFriends = finishAlchemy['friends']
    successRate = getRateOfFriends(helpFriends)+ALCHEMY_CONFIG[alchemyId]['percent']
    totalCostTime = alchemyTime+needTime
    time_now = int(time.time())
    
    if time_now < totalCostTime:
        return {'status':0,'msg':'not enough time to finishAlchemy'}
    
    #炼化成功率
    randNum = random.randint(1,100)
    if 1 <= randNum <= successRate:
        success = True
    else:
        success = False
    
    #玩家+背包信息
    player = db_tool.__getPlayerById(playerId)
    prop = db_tool.getAllProp(playerId)
    
    #炼化失败
    if not success:
        alchemyInfoList.remove(finishAlchemy)
        formulaList = ALCHEMY_CONFIG[alchemyId]['formula']
        for formula in formulaList:
            neetDefinitionId = formula['definitionID']
            neetDefinitionIdNum = formula['num']
            
            db_tool.__addPropItem(prop,neetDefinitionId,neetDefinitionIdNum)
        updateAlchemy(playerId,alchemyInfoList)
        db_tool.saveAllProp(playerId,prop)
        #return {'status':0,'msg':'Alchemy failed ...'}
    else:
        rewardDefinitionID = ALCHEMY_CONFIG[finishAlchemy['id']]['award']['definitionID']
        rewardExp = ALCHEMY_CONFIG[finishAlchemy['id']]['award']['exp']
        
        player['exp']+=rewardExp
        db_tool.__updatePlayer(playerId,{'exp':player['exp']})
        db_tool.__addPropItem(prop,rewardDefinitionID,1)
        db_tool.saveAllProp(playerId,prop)
        
        #更新炼化信息
        alchemyInfoList.remove(finishAlchemy)
        updateAlchemy(playerId,alchemyInfoList)
    return {'status':1,'flag':success,'alchemyId':alchemyId,'player':player,'bag':prop}


#取消炼化
@getOneDBConn
def cancelAlchemy(db,conn,playerId,alchemyId):
    
    #正在或等待炼化的信息
    alchemyInfoList = getAlchemyInfo(playerId)
    #最后炼化的信息
    alchemy = alchemyInfoList.pop()
    
    if alchemy['id'] != alchemyId:
        return {'status':0,'msg':' canceled alchemy is not the end '+ str(alchemyId)}
    
    #背包数据
    prop = db_tool.getAllProp(playerId)
    
    formulaList = ALCHEMY_CONFIG[alchemyId]['formula']
    for formula in formulaList:
        neetDefinitionId = formula['definitionID']
        neetDefinitionIdNum = formula['num']
        
        db_tool.__addPropItem(prop,neetDefinitionId,neetDefinitionIdNum)
    
    updateAlchemy(playerId,alchemyInfoList)
    db_tool.saveAllProp(playerId,prop)
    return {'status':1,'alchemyId':alchemyId,'bag':prop}


#计算开始炼化时间
def getAlchemyTime(alchemyInfoList):
    startTime = 0
    time_now = int(time.time())
    for alchemy in alchemyInfoList:
        #分钟转换成秒
        needTime = ALCHEMY_CONFIG[alchemy['id']]['time']*60
        alchemyTime = alchemy['time']
        totalCostTime = alchemyTime+needTime
        if startTime == 0:
            if time_now < totalCostTime:
                startTime+=totalCostTime
        else:
            startTime+=needTime
    
    #默认当前时间
    if startTime == 0:
       startTime = time_now
    return startTime


#获取炼化信息
@getOneDBConn
def getAlchemyInfo(db,conn,playerId):
    db.execute("select * from alchemy where player_id=%s",(playerId,));
    alchemy = db.fetchone()
    
    if(not alchemy):
        alchemyInfo = ''
        db.execute("insert into alchemy(player_id,alchemy_info) values(%s,%s)",(playerId,alchemyInfo));
        conn.commit()
    else:
        alchemyInfo = alchemy['alchemy_info']
    
    return alchemystr2list(alchemyInfo)

#获取正在炼化的信息
def getActiveAlchemyInfo(playerId):
    #正在或等待炼化的信息
    alchemyInfoList = getAlchemyInfo(playerId)
    
    #正在炼化的信息
    active_alchemy = {}
    
    time_now = int(time.time())
    for alchemy in alchemyInfoList:
        #分钟转换成秒
        needTime = ALCHEMY_CONFIG[alchemy['id']]['time']*60
        alchemyTime = alchemy['time']
        totalCostTime = alchemyTime+needTime
        
        #正在炼化的信息
        if time_now < totalCostTime:
            active_alchemy = alchemy
            break

    return active_alchemy

#更新炼化信息
@getOneDBConn
def updateAlchemy(db,conn,playerId,alchemyInfoList):
    alchemyInfo=list2alchemystr(alchemyInfoList)
    db.execute("update alchemy set alchemy_info = %s where player_id = %s",(alchemyInfo,playerId));
    conn.commit()


#好友帮助炼化
@getOneDBConn
def helpAlchemy(db,conn,playerId,snsName,snsPic,friendId):
    player = db_tool.__getPlayerById(playerId)
    sns_id = player['sns_id']
    
    #正在或等待炼化的信息
    alchemyInfoList = getAlchemyInfo(friendId)
    
    #正在炼化的信息
    active_alchemy = {}
    
    time_now = int(time.time())
    for alchemy in alchemyInfoList:
        #分钟转换成秒
        needTime = ALCHEMY_CONFIG[alchemy['id']]['time']*60
        alchemyTime = alchemy['time']
        totalCostTime = alchemyTime+needTime
        
        #正在炼化的信息
        if time_now < totalCostTime:
            active_alchemy = alchemy
            break
    
    if not active_alchemy:
        return {'status':0,'msg':'no active_alchemy info'}
    
    helpUserInfo = str(playerId)+'#'+snsName+'#'+snsPic
    friends = active_alchemy['friends']
    
    #默认空
    if friends == '':
        friendsList = []
    else:
        friendsList = friends.split('@')
        
    if helpUserInfo not in friendsList:
        friendsList.append(helpUserInfo)
    
    active_alchemy['friends'] = '@'.join(friendsList)
    
    updateAlchemy(friendId,alchemyInfoList)
    
    #添加交互日志
    log_info = {}
    log_info['player_id'] = playerId
    log_info['player_name'] = snsName
    interaction_event.writeInteractionEventLog(log_info,friendId,2)
    
    return {'status':1,'alchemyInfo':alchemyInfoList}

#加速炼化
def speedupAlchemy(playerId,param):
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
    
    #获取当前正在炼化的信息
    active_alchemy = getActiveAlchemyInfo(playerId)
    
    if not active_alchemy:
        return {'status':0,'msg':'no active_alchemy '+str(playerId)}
    
    startTime = active_alchemy['time']
    alchemy_circle = ALCHEMY_CONFIG[active_alchemy['id']]['time']*60
    time_now = int(time.time())
    remainTime = alchemy_circle - (time_now - startTime)%alchemy_circle
    
    #总使用道具数
    prop_num = useNum+needNum
    
    #加速时间一小时
    speedTime = PROP_CONFIG[int(prop_id)]['speed']
    
    #炼化时间重新赋值
    if remainTime > speedTime*prop_num:
        subtractTime = speedTime*prop_num
    else:
        subtractTime = remainTime
        
    #正在或等待炼化的信息
    alchemyInfoList = getAlchemyInfo(playerId)
    for alchemy in alchemyInfoList:
        alchemy['time'] -= subtractTime
    
    updateAlchemy(playerId,alchemyInfoList)
    if useNum>0:
        db_tool.__subtractPropItem(propDict,prop_id,useNum)
        db_tool.saveAllProp(playerId,propDict)#update prop db
    if costKb > 0:
        db_tool.__updatePlayer(playerId,{'kb':player['kb']})
    
    return {'status':1,'bag':propDict,'alchemy':alchemyInfoList,'kb':player['kb']}
    

#每个好友加2点成功率
def getRateOfFriends(friendstr):
    if friendstr:
        friends = len(friendstr.split('@'))
        rate = friends*2
    else:
        rate = 0
    return rate

def alchemystr2list(alchemystr):
    alchemylist = []
    if len(alchemystr)>0:
        list = alchemystr.split('|')
        for each in list:
            alchemy = each.split(':')
            alchemydict = dict()
            alchemydict['id']=int(alchemy[0])
            alchemydict['time']=int(alchemy[1])
            alchemydict['friends']=str(alchemy[2])
            #alchemydict[int(alchemy[0])] = int(alchemy[1])
            alchemylist.append(alchemydict)
    return alchemylist

def list2alchemystr(alchemylist):
    alist = list()
    for alchemy in alchemylist:
        #for key in alchemy:
        #    alist.append(str(key)+':'+str(alchemy[key]))
        alist.append(str(alchemy['id'])+':'+str(alchemy['time'])+':'+str(alchemy['friends']))
    alchemystr = '|'.join(alist)
    return alchemystr

'''
#dict 无序的， list有序的

def alchemystr2dict(alchemystr):
    alchemydict = dict()
    if len(alchemystr)>0:
        list = alchemystr.split('|')
        for each in list:
            alchemy = each.split(':')
            alchemydict[int(alchemy[0])] = int(alchemy[1])
    return alchemydict

def dict2alchemystr(alchemydict):
    alchemylist = list()
    for alchemyId in alchemydict:
        alchemylist.append(str(alchemyId)+":"+str(alchemydict[alchemyId]));
    collection = '|'.join(producelist)
    return collection
'''