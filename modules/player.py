#-*- coding=utf8 -*-
from settings import *
import random
import time

from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.level_task as level_task
import modules.odds as odds
import modules.alchemy as alchemy_module
import modules.produce as produce_module
import modules.search_team as search_module
import modules.explore_team as explore_team
import item as item_module
import auction as auction
import purchase as purchase
import modules.life_tree as life_tree
import modules.interaction_event as interaction_event

from config.energy_config import *
from config.level_config import *
from config.search_config import *
from config.expand_config import *
from config.guide_config import *
from config.drawing_config import *

#判断玩家是否是VIP
def isVIP(player):
    time_now = int(time.time())
    isVIP = player['vip'] > time_now
    return isVIP


#获取玩家能量上限
def getMaxEnergy(player):
    maxEnergy = ENERGY_CONFIG[player['level']]
    lifeTreeInfo = life_tree.getLifeTreeInfo(player['id'])
    treeLevel = lifeTreeInfo['level']
    if ENERGY_EXPAND_CONFIG.has_key(treeLevel):
        maxEnergy += ENERGY_EXPAND_CONFIG[treeLevel]
    return maxEnergy


#更新玩家能量
def __updateEnergy(player):
    #300s -5分钟收获一次
    energyCircle = 300
    time_now = int(time.time())
    addEnergy = (time_now - player['last_energy_time'])/energyCircle
    remainTime = (time_now - player['last_energy_time'])%energyCircle
    
    maxEnergy = getMaxEnergy(player)
   
    if player['energy'] > maxEnergy:
        pass
    else:
        player['energy'] = (player['energy'] + addEnergy)
        if player['energy'] > maxEnergy:
            player['energy'] = maxEnergy
            remainTime = 0
     
    player['last_energy_time'] = time_now-remainTime
    
    #需要更新[energy] and [last_energy_time]
    #db_tool.__updatePlayer(player['id'],{'energy':player['energy'],'last_energy_time':player['last_energy_time']})
    return player


#扩展地图
def expandMap(playerId,type,snsObj):
    player = db_tool.__getPlayerById(playerId)
    returnVal = {}
    if type == 1:
        price = EXPAND_CONFIG[player['expand']+1]['KB']
        if player['kb'] - price >= 0:
            player['kb'] -= price
            db_tool.__updatePlayer(player['id'],{'kb':player['kb'],'expand':player['expand']+1})
            
            #add cost log
            addCostLog(player['id'],price,'expandMap')
            
            returnVal['status'] = 1
        else:
            returnVal['status'] = 0
            returnVal['msg'] = 'KB不足'
            return returnVal
    else:
        '''
        friends = len(snsObj.getFriends())
        if player['expand'] >= EXPAND_CONFIG[player['level']]['expand'] or friends <= EXPAND_CONFIG[player['level']]['friends']:
            returnVal['status'] = 0
            returnVal['msg'] = '好友数量不足'
            return returnVal
        '''
        price = EXPAND_CONFIG[player['expand']+1]['GB']
        if player['gb'] - price >= 0:
            player['gb'] -= price
            db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'expand':player['expand']+1})
            returnVal['status'] = 1
        else:
            returnVal['status'] = 0
            returnVal['msg'] = 'GB不足'
            return returnVal
    player['expand'] += 1
    returnVal['player'] = player
    return returnVal


#升级
def levelUp(playerId):
    player = db_tool.__getPlayerById(playerId)
    levelConfig = LEVEL_CONFIG
    dictKey = levelConfig.keys()
    dictKey.sort()
    for each in dictKey:
        if levelConfig[each] <= player['exp'] < levelConfig[each+1]:
            clevel = each
            break
    if player['level'] < clevel:
        player['level'] = clevel
        
        maxEnergy = getMaxEnergy(player)
        if player['energy'] > maxEnergy:
            maxEnergy = player['energy']
        
        db_tool.__updatePlayer(player['id'],{'level':player['level'],'energy':maxEnergy})
        
        #添加等级任务
        taskinfo = level_task.addLevelTask(playerId,clevel)
        
        return {'status':1,'level':clevel,'energy':maxEnergy,'new_task':taskinfo}
    else:
        return {'status':0,'msg':'level not change.'}


#开始生长
def startGrowth(playerId,itemId):
    mapItem = db_tool.__getItem(playerId,itemId)
    if not mapItem:
        return {'status':0,'msg':'no such item'}
    
    definitionId = item_module.getDrawIdByMixId(mapItem['definitionId'])
    
    #消耗GB
    costGb = DRAWING_CONFIG[definitionId]['harvest']['cost']
    
    player = db_tool.__getPlayerById(playerId)
    player['gb'] -= costGb
    
    if player['gb'] < 0:
        return {'status':0,'msg':'not enough gb for growth'}
    
    db_tool.__updatePlayer(playerId,{'gb':player['gb']})
    
    time_now = int(time.time())
    updateInfo = {'created_time':time_now}
    db_tool.updateItem(playerId,itemId,updateInfo)
    
    return {'status':1,'id':itemId,'gb':costGb,'start_time':time_now}


#收获
@getOneDBConn
def harvest(db,conn,playerId,itemId):
    mapItem = db_tool.lockItem(db,conn,playerId,itemId)
    if not mapItem:
        return {'status':0,'msg':'no such item'}
        
    definitionId = item_module.getDrawIdByMixId(mapItem['definitionId'])
    startTime = mapItem['created_time']
    friends = mapItem['friends']
    
    #收获消耗的能量,时间,获得的GB
    costEnergy = 1
    addGb = DRAWING_CONFIG[definitionId]['harvest']['income']
    costTime = DRAWING_CONFIG[definitionId]['harvest']['duration']
    
    time_now = int(time.time())
    if (startTime+costTime) > time_now:
        return {'status':0,'msg':'need more time for growth'}
    
    player = db_tool.__getPlayerById(playerId)
    player=__updateEnergy(player)
    
    #是否被好友收过
    if friends:
        addGb = addGb*3/4
    else:
        player['energy'] -= costEnergy
        if player['energy'] < 0:
            return {'status':0,'msg':'not enough energy.'}
    
    player['gb'] += addGb
    db_tool.__updatePlayer(player['id'],{'energy':player['energy'],'gb':player['gb'],'last_energy_time':player['last_energy_time']})
    #生长时间置0
    updateInfo = {}
    updateInfo['created_time'] = 0
    updateInfo['friends'] = ''
    db_tool.updateItemById(db,conn,playerId,itemId,updateInfo)
    
    '''
    #掉落动力石
    stone=0
    randNum = random.randint(1,100)
    if 1 <= randNum <= 5:
        stone=1
    else:
        stone=0
    if stone>0:
        propDict = db_tool.getAllProp(playerId)
        db_tool.__addPropItem(propDict,10050,stone)
        db_tool.saveAllProp(playerId,propDict)
    '''
    
    return {'status':1,'gb':addGb,'playerInfo':player,'id':itemId}


#帮助好友收获
@getOneDBConn
def helpHarvest(db,conn,playerId,param):
    playerId = param['player_id']
    playerName = param['player_name']
    playerPic = param['player_pic']
    friendId = param['friend_id']
    itemId = param['id']
        
    mapItem = db_tool.lockItem(db,conn,friendId,itemId)
    if not mapItem:
        return {'status':0,'msg':'no such item'}
    
    definitionId = item_module.getDrawIdByMixId(mapItem['definitionId'])
    friends = mapItem['friends']
    
    if friends:
        return {'status':0,'msg':'has helped by others'}
        
    player = db_tool.__getPlayerById(playerId)
    
    #消耗免费能量
    player['help_energy'] -= 1
    if player['help_energy'] < 0:
        return {'status':0,'msg':'not enough helpEnergy'}
    
    #获得的GB
    addGb = DRAWING_CONFIG[definitionId]['harvest']['income']/4
    player['gb'] += addGb
    #获得奖励
    db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'help_energy':player['help_energy']})
    
    #记录好友信息
    friendsInfo = {}
    friendsInfo['id'] = playerId
    friendsInfo['name'] = playerName
    friendsInfo['pic'] = playerPic
    
    updateInfo = {'friends':db_tool.__dictToString(friendsInfo)}
    db_tool.updateItemById(db,conn,friendId,itemId,updateInfo)
    
    #添加交互日志
    log_info = {}
    log_info['player_id'] = playerId
    log_info['player_name'] = playerName
    interaction_event.writeInteractionEventLog(log_info,friendId,4)
    
    return {'status':1,'gb':addGb,'playerInfo':player,'id':itemId}


#访问好友获取玩家信息
def getUserInfo(id):
    player = db_tool.__getPlayerById(id)
    if player:
        returnVal = {}
        returnVal['status'] = 1
        returnVal['player'] = player
        #returnVal['map'] = db_tool.getMapsbyPlayerId(id)
        returnVal['map_level'] = item_module.getHabitatInfo(id)
        #添加拍卖行状态(是否有拍卖或求购信息)
        returnVal['auctionStatus'] = getAuctionStatus(id)
        #添加炼化信息
        returnVal['alchemyInfo'] = alchemy_module.getAlchemyInfo(id)
        #添加生产信息
        returnVal['produce'] = produce_module.getProduceInfo(id)
        #添加搜索信息
        returnVal['searcher'] = search_module.getSearchTeamDetail(id)
        #是否已经组队
        returnVal['explore_start']=explore_team.isExploreStart(id)
        #生命树
        returnVal['life_tree'] = life_tree.getLifeTreeInfo(id)
        
        return returnVal
    else:
        return {'status':0,'error_type':13,'msg':'can not find the friend by id :'+str(id)}
        

#是否有交易物品
def getAuctionStatus(playerId):
    purchaseCount = purchase.getPurchaseCounts(playerId)
    auctionCount = auction.__countTransaction(playerId)
    
    returnVal = {}
    returnVal['purchase'] = purchaseCount
    returnVal['auction'] = auctionCount
    
    return returnVal

#更新新手导读状态
def updateGuide(id,guide_id):
    
    bool= db_tool.__updatePlayer(id,{"guide":guide_id});
    if(bool):
        #做完新手导读
        if(guide_id == GUIDE_STEP['totalsteps']):
            reward = []
            for rewardType in GUIDE_CONFIG.keys():
                db_tool.addPropAndMoney(id,rewardType,GUIDE_CONFIG[rewardType])
                
                #format
                retval = {}
                retval['definationID'] = rewardType
                retval['num'] = GUIDE_CONFIG[rewardType]
                reward.append(retval)
            
            #增加3点经验使玩家升级
            player = db_tool.__getPlayerById(id)
            player['exp'] = player['exp']+3
            db_tool.__updatePlayer(id,{'exp':player['exp']});
                
            return {'status':1,'player':player,'guide':guide_id,'reward':reward,'bag':db_tool.getAllProp(id)}
        else:
            return {'status':1,'guide':guide_id}
    else:
        return {'status':0,'guide':guide_id}


def updateTitle(id,title_id):
    bool= db_tool.__updatePlayer(id,{"title_id":title_id});
    if(bool):
        return {'status':1,'title_id':title_id}
    else:
        return {'status':0,'title_id':title_id}

 
#挖宝
def startTreasure(playerId,info):
    player = db_tool.__getPlayerById(playerId)

    if not player:
        return {'status':0,'msg':'can not find player by player id :'+str(playerId)}
    player=__updateEnergy(player)

    #挖宝消耗的能量
    energyCost = 10

    #操作状态
    bool = False
    
    #免费挖宝次数['free_times']
    if(player['free_times'] > 0):
        player['free_times'] -= 1
        bool = db_tool.__updatePlayer(player['id'],{'free_times':player['free_times']})
    elif player['energy'] >= energyCost :
        player['energy'] -= energyCost
        bool = db_tool.__updatePlayer(player['id'],{'energy':player['energy'],'last_energy_time':player['last_energy_time']})
    else:
        return {'status':0,'msg':'not enough energy.','energy':player['energy'],'last_energy_time':player['last_energy_time']}
    
    treasureInfo = getTreasureInfo(playerId)
    if(bool):
        return {'status':1,'player':player,'confirmCode':treasureInfo['start_time']}
    else:
        return {'status':0,'msg':'update player info error.'}


#完成+继续
def finishTreasure(playerId,info):
    
    player = db_tool.__getPlayerById(playerId)
    if not player:
        return {'status':0,'msg':'can not find player by player id :'+str(playerId)}
    
    energyCost = 10
    player=__updateEnergy(player)
    
    player['gb']+=info['gb']   
    player['energy']+=info['energy']
    player['exp']+=info['exp']
    
    if(info['continue']):
        if(player['free_times'] > 0):
            player['free_times'] -= 1
        elif(player['energy']<energyCost):
            return {'status':0,'msg':'not enough energy.'}    
        else:
            player['energy']-= energyCost
        
        #重置confirmCode
        treasureInfo = getTreasureInfo(playerId)
        info['confirmCode'] = treasureInfo['start_time']
    else:
        #验证是否可以挖宝
        if not checkTreasure(playerId,info['confirmCode']):
            return {'status':0,'msg':'confirmCode error, player id :'+str(playerId)}
    
    bool= db_tool.__updatePlayer(playerId,{'gb':player['gb'],'exp':player['exp'],'energy':player['energy'],'last_energy_time':player['last_energy_time'],'free_times':player['free_times']})
    
    if(bool):
        return {'status':1,'player':player,'info':info}
    else:
        return {'status':0,'player':player,'info':info}
        
        
#获取宝藏
@getOneDBConn
def getTreasure(db,conn,playerId,info):
    import random
    area=info['map_id']
    player = db_tool.__getPlayerById(playerId)
    
    if player['level'] < SEARCH_AREA[area]:
        return {'status':0,'msg':'等级不足，不能到该区域挖宝'}
    
    #验证并设置获得宝藏状态status=1
    db.execute("SELECT * FROM treasure WHERE player_id =%s ",(playerId,))
    treasureInfo = db.fetchone()
    
    if (treasureInfo['status'] == 0):
        #设置status=1
        db.execute("UPDATE treasure set status=1 where player_id=%s",(playerId,))
        
        definitionId,num=odds.getItemByAreaForTreasure(area)
        propDict = db_tool.getAllProp(playerId)
        db_tool.__addPropItem(propDict,definitionId,num)
        db_tool.saveAllProp(playerId,propDict)
        
        conn.commit()
    else:
        return {'status':0,'msg':'已挖到宝藏'}
    
    return {'status':1,'definitionId':definitionId,'num':num,'bag':propDict}

    
#验证挖宝操作
@getOneDBConn
def checkTreasure(db,conn,playerId,startTime):
    db.execute("SELECT * FROM treasure WHERE player_id =%s ",(playerId,))
    treasureInfo = db.fetchone()

    if (treasureInfo['start_time'] == int(startTime)):
        time_now = int(time.time())
        db.execute("UPDATE treasure set start_time=%s,status=0 where player_id=%s",(time_now,playerId))
        conn.commit()
        return True
    else:
        return False

@getOneDBConn
def getTreasureInfo(db,conn,playerId):
    db.execute("SELECT * FROM treasure WHERE player_id =%s ",(playerId,))
    treasureInfo = db.fetchone()
    time_now = int(time.time())
    defTreasureInfo = {'player_id':playerId,'start_time':time_now,'status':0}
    if not treasureInfo:
        db.execute("INSERT INTO treasure(player_id,start_time,status) VALUES(%s,%s,%s)",(playerId,time_now,0))
        conn.commit()
        treasureInfo = defTreasureInfo
    #挖到宝藏单没有领取的情况下，重置状态
    elif treasureInfo['status'] == 1:
        db.execute("UPDATE treasure set start_time=%s,status=0 where player_id=%s",(time_now,playerId))
        conn.commit()
        treasureInfo = defTreasureInfo
    return treasureInfo


#记录消费日志
#method : buildingLevelUp、expandMap、decorateInShop、buyPropInShop、becomeVIP
@getOneDBConn
def addCostLog(db,conn,playerId,costKbs,costAction):
    time_now = int(time.time())
    db.execute("INSERT INTO cost_log(player_id,cost_kb,cost_action,cost_time) VALUES(%s,%s,%s,%s)",(playerId,costKbs,costAction,time_now))
    conn.commit()