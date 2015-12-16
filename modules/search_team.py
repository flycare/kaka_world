#-*- coding=utf8 -*-
from settings import *
import time
import math
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.odds as odds
import player as player_module
import modules.interaction_event as interaction_event

from config.prop_config import *
from config.search_config import *

#派遣搜索队
def sendSearchTeam(playerId,param):
    areaId = param['map_id']
    searchTypeId = param['index']
    
    player = db_tool.__getPlayerById(playerId)
    if player['level'] < SEARCH_AREA[areaId]:
        return {'status':0,'msg':'you can not search this area in level ['+str(areaId)+']'}
        
    time_now = int(time.time())
    searchInfo = getSearchTeamById(playerId)
    
    if not searchInfo:
        searchInfo = {}
        searchInfo['user_id'] = playerId
        searchInfo['last_start_time'] = time_now
        searchInfo['area'] = areaId
        searchInfo['type'] = searchTypeId
        searchInfo['number'] = SEARCH_TYPE[searchTypeId]['rewards']
        searchInfo['blue_box'] = 0
        saveSearchTeamInfo(searchInfo)
    else:
        '''
        updateInfo = {}
        updateInfo['last_start_time'] = time_now
        updateInfo['area'] = areaId
        updateInfo['type'] = searchTypeId
        updateInfo['number'] = 0
        updateInfo['blue_box'] = 0
        updateSearchTeamInfo(playerId,updateInfo)
        '''
        return {'status':0,'msg':'can not send search_team for twice'}
    
    return {'status':1,'map_id':areaId,'index':searchTypeId,'start_time':time_now}


#收获好友的搜索队
@getOneDBConn
def stealSearchTeam(db,conn,param):
    playerId = param['player_id']
    playerName = param['player_name']
    playerPic = param['player_pic']
    friendId = param['friend_id']
    
    friendPlayer = db_tool.__getPlayerById(friendId)
    
    if not friendPlayer or player_module.isVIP(friendPlayer):
        return {'status':0,'error_type':2,'msg':'friend is null or is vip'}
    
    searchInfo = lockSearchTeamById(db,conn,friendId)
    
    if not searchInfo or searchInfo['blue_box'] != 1:
        searchInfo = getSearchTeamDetail(friendId)
        return {'status':0,'error_type':1,'searcher':searchInfo,'msg':'searchInfo is done or stealed by other friend'}
    
    number = searchInfo['number']
    searchTypeId = searchInfo['type']
    areaId = searchInfo['area']
    searchStartTime = searchInfo['last_start_time']
    needTime = SEARCH_TYPE[searchTypeId]['time']*3600
    time_now = int(time.time())
    
    if (searchStartTime+needTime) > time_now:
        return {'status':0,'msg':'need more time for searchInfo'}
    
    #记录好友信息
    friendsInfo = {}
    friendsInfo['id'] = playerId
    friendsInfo['name'] = playerName
    friendsInfo['pic'] = playerPic
    
    updateInfo = {}
    updateInfo['friends'] = db_tool.__dictToString(friendsInfo)
    updateInfo['number'] = number-1
    updateInfo['blue_box'] = 2
    updateSearchTeamInfoForLock(db,conn,friendId,updateInfo)
    
    #更新背包信息
    propDict = db_tool.getAllProp(playerId)
    prop_id,num = odds.getItemByArea(areaId)
    db_tool.__addPropItem(propDict,prop_id,num)
    db_tool.saveAllProp(playerId,propDict)
    
    searchInfo = getSearchTeamDetail(friendId)
    
    #添加交互日志
    log_info = {}
    log_info['player_id'] = playerId
    log_info['player_name'] = playerName
    log_info['prop_id'] = prop_id
    interaction_event.writeInteractionEventLog(log_info,friendId,1)
    
    return {'status':1,'definitionId':prop_id,'bag':propDict,'searcher':searchInfo}


#领取奖励
@getOneDBConn
def getSearchTeam(db,conn,playerId,isBlueBox):
    searchInfo = lockSearchTeamById(db,conn,playerId)
    if not searchInfo:
        return {'status':0,'msg':'no search team send'}
        
    #奖励的箱子个数
    number = searchInfo['number']
    searchTypeId = searchInfo['type']
    areaId = searchInfo['area']
    searchStartTime = searchInfo['last_start_time']
    blueBox = searchInfo['blue_box']
    needTime = SEARCH_TYPE[searchTypeId]['time']*3600
    time_now = int(time.time())
    
    if (searchStartTime+needTime) > time_now:
        return {'status':0,'msg':'need more time for searchInfo'}
    
    #奖励个数减一
    number -= 1
    
    #奖励个数为0 清除记录
    if number < 1:
        delSearchTeamByIdForLock(db,conn,playerId)
    else:
        updateInfo = {}
        if isBlueBox:
            if blueBox == 1:
                updateInfo['blue_box'] = 3
            else:
                return {'status':0,'error_type':1,'msg':'blue_box has bean opened or stealed'}
        updateInfo['number'] = number
        updateSearchTeamInfoForLock(db,conn,playerId,updateInfo)
    
    #更新背包信息
    propDict = db_tool.getAllProp(playerId)
    prop_id,num = odds.getItemByArea(areaId)
    db_tool.__addPropItem(propDict,prop_id,num)
    db_tool.saveAllProp(playerId,propDict)
    
    return {'status':1,'item':prop_id,'bag':propDict,'number':number}


#收获时使用
def getSearchTeamInfo(playerId):
    searchInfo = getSearchTeamDetail(playerId)
    if searchInfo:
        searchInfo['status'] = 1
    else:
        searchInfo['status'] = 0
    return searchInfo

'''
#蓝色箱子状态
1:可以打开
2:被偷
3:已经打开
blue_box
'''
#获取自己及好友搜索队具体信息
def getSearchTeamDetail(playerId):
    searchInfo = getSearchTeamById(playerId)
    returnVal = {}
    if searchInfo:
        
        searchTypeId = searchInfo['type']
        areaId = searchInfo['area']
        searchStartTime = searchInfo['last_start_time']
        blueBox = searchInfo['blue_box']
        number = searchInfo['number']
        
        needTime = SEARCH_TYPE[searchTypeId]['time']*3600
        time_now = int(time.time())
    
        returnVal['index'] = searchTypeId
        returnVal['areaID'] = areaId
        returnVal['startTime'] = searchStartTime
        returnVal['blue_box'] = blueBox
        returnVal['number'] = number
        
        if searchInfo['friends']:
            returnVal['friends'] = db_tool.__auctionStringToDict(searchInfo['friends'])
        else:
            returnVal['friends'] = {}
        
        if (searchStartTime+needTime) <= time_now:
            if blueBox == 0:
                blueBox = 1
                updateInfo = {}
                updateInfo['blue_box'] = blueBox
                updateSearchTeamInfo(playerId,updateInfo)
                
                returnVal['blue_box'] = blueBox
        
    return returnVal


#使用道具加速搜索
def speedupSearch(playerId,param):
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
    
    searchInfo = getSearchTeamById(playerId)
    searchTypeId = searchInfo['type']
    areaId = searchInfo['area']
    searchStartTime = searchInfo['last_start_time']
    needTime = SEARCH_TYPE[searchTypeId]['time']*3600
    
    #获取搜索队上次搜索时间
    last_start_time = searchStartTime
    #剩余时间
    time_now = int(time.time())
    remainTime = needTime - (time_now - searchStartTime)
    
    #总使用道具数
    prop_num = useNum+needNum
    
    #加速时间一小时
    speedTime = PROP_CONFIG[int(prop_id)]['speed']
    
    #搜索时间重新赋值
    if remainTime > speedTime*prop_num:
        last_start_time -= speedTime*prop_num
    else:
        last_start_time -= remainTime
    
    #update and save
    db_tool.__updateSearchTeam(playerId,last_start_time)
    if useNum>0:
        db_tool.__subtractPropItem(propDict,prop_id,useNum)
        db_tool.saveAllProp(playerId,propDict)#update prop db
    if costKb > 0:
        db_tool.__updatePlayer(playerId,{'kb':player['kb']})
    
    return {'status':1,'last_start_time':last_start_time,'bag':propDict,'kb':player['kb']}


def friendstr2dict(friendstr):
    frienddict = dict()
    if len(friendstr)>0:
        list = friendstr.split('|')
        for each in list:
            friend = each.split('@')
            frienddict[int(friend[0])] = friend[1]
    return frienddict


def dict2friendstr(frienddict):
    friendlist = list()
    for index in frienddict:
        friendlist.append(str(index)+"@"+str(frienddict[index]));
    collection = '|'.join(friendlist)
    return collection


@getOneDBConn
def saveSearchTeamInfo(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into search_team (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()
    
@getOneDBConn
def getSearchTeamById(db,conn,playerId):
    db.execute("SELECT * FROM search_team WHERE user_id = %s",(playerId,))
    searchInfo = db.fetchone()
    if searchInfo:
        dict(searchInfo)
    return searchInfo

#lock and get
def lockSearchTeamById(db,conn,playerId):
    db.execute("SELECT * FROM search_team WHERE user_id = %s for update",(playerId,))
    searchInfo = db.fetchone()
    if searchInfo:
        dict(searchInfo)
    return searchInfo

@getOneDBConn
def updateSearchTeamInfo(db,conn,playerId,info):
    updateSearchTeamInfoForLock(db,conn,playerId,info)

def updateSearchTeamInfoForLock(db,conn,playerId,info):
    fields = info.keys()
    values = info.values()
    values.append(playerId)
    setField = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE search_team SET %s WHERE %s"%(setField,"user_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()
    
@getOneDBConn
def delSearchTeamById(db,conn,playerId):
    delSearchTeamByIdForLock(db,conn,playerId)

def delSearchTeamByIdForLock(db,conn,playerId):
    db.execute("DELETE FROM search_team WHERE user_id = %s",(playerId,))
    conn.commit()