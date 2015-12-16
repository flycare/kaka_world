#-*- coding=utf8 -*-
from twisted.web import resource ,server
from twisted.application import service, strports
from pyamf.remoting.gateway.twisted import TwistedGateway

import sys
import os
import traceback
C_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(C_PATH)

from settings import *
from modules.session import getPlayerSession

import modules.auction as auction
import modules.collection as collection
import modules.db_tool as db_tool
import modules.friend as friend
import modules.item as item
import modules.player as player_module
import modules.prop as prop
import modules.search_team as search_team
import modules.user_box as user_box
import modules.daily_reward as daily_reward
import modules.daily_task as daily_task
import modules.level_task as level_task
import modules.produce as produce
import modules.system_reward as system_reward
import modules.exchange as exchange
import modules.alchemy as alchemy
import modules.invite as invite
import modules.explore_team as explore_team
import modules.festival_gift as festival_gift
import modules.exchange_task as exchange_task
import modules.life_tree as life_tree
import modules.purchase as purchase
import modules.interval_box as interval_box
import modules.interaction_event as interaction_event


def hstoreToDict(hstore):
    return eval("{"+hstore+"}")

def init(serverInfo,is_fan):
    playerId = serverInfo['playerId']
    sns_id = serverInfo['sns_id']

    #add weekly reward
    daily_reward.getWeeklyReward(playerId)
    #add daily reward (notice: update last_login_time)
    dailyReward = daily_reward.getDailyReward(playerId,is_fan);
    #add festival reward
    festivalDailyReward = daily_reward.getFestivalDailyReward(playerId)
    
    #get player info
    player = db_tool.__getPlayerById(playerId)
    if not player:
        return {'status':0,'msg':'player not exist'}
    
    time_now = int(time.time())

    player_module.__updateEnergy(player)
    
    returnVal = {'status':1}
    returnVal['player'] = player
    #returnVal['map'] = db_tool.getMapsbyPlayerId(playerId)
    returnVal['map_level'] = item.getHabitatInfo(playerId)
    returnVal['searcher'] = search_team.getSearchTeamDetail(playerId)
    returnVal['bag'] = db_tool.getAllProp(playerId)
    returnVal['bagMax'] = prop.getBagCapacity(playerId)
    returnVal['collection'] = collection.getCollection(playerId)
    returnVal['time_now']=time_now
    returnVal['box_status']=user_box.getUserBoxStatus(sns_id)
    returnVal['daily_reward']=dailyReward
    returnVal['festival_daily_reward']=festivalDailyReward
    returnVal['daily_task']=daily_task.getTaskInfo(playerId)
    returnVal['level_task']=level_task.getLevelTaskInfo(playerId)
    returnVal['produce']=produce.getProduceInfo(playerId)
    returnVal['invite_info']=invite.getInviteInfo(sns_id)
    returnVal['system_reward']=system_reward.getSystemRewardInfo(playerId)
    returnVal['auctionStatus'] = player_module.getAuctionStatus(playerId)
    returnVal['alchemy']=alchemy.getAlchemyInfo(playerId)
    returnVal['event_num']=interaction_event.getEventCount(playerId)
    returnVal['exchange_task']=exchange_task.getExchangeTaskInfo(playerId)
    returnVal['explore_start']=explore_team.isExploreStart(playerId)
    returnVal['life_tree'] = life_tree.getLifeTreeInfo(playerId)
    returnVal['interval_box'] = interval_box.getIntervalBoxInfo(playerId)
    
    return returnVal


#gateway函数

@getPlayerSession
def initGame(serverInfo,is_fan):
    return init(serverInfo,is_fan)     

@getPlayerSession
def decorativeScene(serverInfo,param):
    return item.decorativeScene(serverInfo,param)

def getUserInfo(serverInfo,param):
    return player_module.getUserInfo(param)

@getPlayerSession
def getFriendsInfo(serverInfo,param):
    return friend.getFriendsInfo(serverInfo['playerId'],param)
        
@getPlayerSession
def buyPropInShop(serverInfo,param):
    return prop.buyPropInShop(serverInfo['playerId'],param)

@getPlayerSession
def sellProps(serverInfo,param):
    return prop.sellProps(serverInfo['playerId'],param)
    
@getPlayerSession
def sellPropInBag(serverInfo,param):
    return prop.sellPropInBag(serverInfo['playerId'],param)

@getPlayerSession        
def becomeVIP(serverInfo,param):
    return prop.becomeVIP(serverInfo['playerId'],param)   

@getPlayerSession
def getSearchTeam(serverInfo,isBlueBox):
    return search_team.getSearchTeam(serverInfo['playerId'],isBlueBox)
        
@getPlayerSession
def Auction(serverInfo,param):
    returnVal = auction.Auction(serverInfo['playerId'],param)
    returnVal['auctionStatus'] = player_module.getAuctionStatus(serverInfo['playerId'])
    return returnVal
    
@getPlayerSession    
def getAuction(serverInfo,playerId):
    return auction.getAuction(playerId)
        
@getPlayerSession
def buyAuction(serverInfo,info):
    return auction.buyAuction(serverInfo['playerId'],info['auctionId'],info['name'])
        
@getPlayerSession
def cancelAuction(serverInfo,id):
    returnVal = auction.cancelAuction(serverInfo['playerId'],id)
    returnVal['auctionStatus'] = player_module.getAuctionStatus(serverInfo['playerId'])
    return returnVal
        
@getPlayerSession
def expandMap(serverInfo,type):
    snsObj = []
    return player_module.expandMap(serverInfo['playerId'],type,snsObj)
    
@getPlayerSession
def getAuctionEvent(serverInfo,playerId):
    return auction.getAuctionEvent(serverInfo['playerId'])

@getPlayerSession
def getEventLogs(serverInfo):
    return interaction_event.getEventLogs(serverInfo['playerId'])

@getPlayerSession
def mix(serverInfo,definitionId):
    return collection.mix(serverInfo['playerId'],definitionId)
        
@getPlayerSession
def harvest(serverInfo,param):
    return player_module.harvest(serverInfo['playerId'],param)
        
@getPlayerSession
def resolve(serverInfo,param):
    definitionId = param['definitionId']
    definitionNum = param['number']
    return collection.resolve(serverInfo['playerId'],definitionId,definitionNum)
        
@getPlayerSession
def getCollection(serverInfo):
    return collection.getCollection(serverInfo['playerId'])
       
@getPlayerSession 
def usePropInBag(serverInfo,prop_id):
    return prop.usePropInBag(serverInfo['playerId'],prop_id)

@getPlayerSession
def levelUp(serverInfo):
    return player_module.levelUp(serverInfo['playerId'])

@getPlayerSession        
def buildingLevelUp(serverInfo,array):
    return item.buildingLevelUp(serverInfo['playerId'],array)

@getPlayerSession 
def habitatLevelUp(serverInfo,array):
    return item.habitatLevelUp(serverInfo['playerId'],array)
    
@getPlayerSession
def finishCollection(serverInfo,definitionId):
    return collection.finishCollection(serverInfo['playerId'],definitionId)
    
@getPlayerSession
def updateItemDetail(serverInfo,info):
    return item.updateDetail(serverInfo['playerId'],info['id'],info['detail'])    

@getPlayerSession
def updateUserTitle(serverInfo,title_id):
    return player_module.updateTitle(serverInfo['playerId'],title_id)  

@getPlayerSession
def updateGuide(serverInfo,guide_id):
    return player_module.updateGuide(serverInfo['playerId'],guide_id) 

@getPlayerSession
def startTreasure(serverInfo,info):
    return player_module.startTreasure(serverInfo['playerId'],info)  

@getPlayerSession
def finishTreasure(serverInfo,info):
    return player_module.finishTreasure(serverInfo['playerId'],info) 

@getPlayerSession
def getTreasure(serverInfo,info):
    return player_module.getTreasure(serverInfo['playerId'],info) 

@getPlayerSession
def getBoxInfo(serverInfo):
    return user_box.getBoxInfo(serverInfo['sns_id'])

@getPlayerSession
def openBox(serverInfo):
    return user_box.openBox(serverInfo['sns_id'])

@getPlayerSession
def updateDailyTask(serverInfo,info):
    return daily_task.updateDailyTask(serverInfo['playerId'],info['task_id'],info['status']);

@getPlayerSession
def visitFriend(serverInfo,friend_id):
    return friend.visitFriend(serverInfo['playerId'],friend_id)

@getPlayerSession
def doDailyTask(serverInfo,task_id):
    return daily_task.doDailyTask(serverInfo['playerId'],task_id)

@getPlayerSession
def startProduce(serverInfo,produce_info):
    return produce.startProduce(serverInfo['playerId'],produce_info['machineId'],produce_info['produceId'])
    
@getPlayerSession
def cancelProduce(serverInfo,machineId):
    return produce.cancelProduce(serverInfo['playerId'],machineId)

@getPlayerSession
def finishProduce(serverInfo,machineId):
    return produce.finishProduce(serverInfo['playerId'],machineId)

@getPlayerSession
def acceptSystemReward(serverInfo,sysRewardId):
    return system_reward.acceptSystemReward(serverInfo['playerId'],sysRewardId)

@getPlayerSession
def startExchange(serverInfo,exchangeData):
    return exchange.startExchange(serverInfo['playerId'],exchangeData)

@getPlayerSession
def updateLevelTaskInfo(serverInfo,parms):
    return level_task.updateLevelTaskInfo(serverInfo['playerId'],parms['id'],parms['content'])

@getPlayerSession
def finishLevelTask(serverInfo,parms):
    return level_task.finishLevelTask(serverInfo['playerId'],parms)

@getPlayerSession
def decorateInBag(serverInfo,parms):
    return prop.decorateInBag(serverInfo['playerId'],parms)

@getPlayerSession
def decorateInShop(serverInfo,parms):
    return prop.decorateInShop(serverInfo['playerId'],parms)

@getPlayerSession
def decorateGroupInShop(serverInfo,parms):
    return prop.decorateGroupInShop(serverInfo['playerId'],parms)
    
@getPlayerSession
def expandBagCapacity(serverInfo,parms):
    return prop.expandBagCapacity(serverInfo['playerId'],parms)

@getPlayerSession
def refining(serverInfo,param):
    definitionId = param['definitionId']
    definitionNum = param['number']
    return collection.refining(serverInfo['playerId'],definitionId,definitionNum)

@getPlayerSession
def getAlchemyInfo(serverInfo):
    returnVal = {'status':1}
    returnVal['alchemy']=alchemy.getAlchemyInfo(serverInfo['playerId'])
    return returnVal
    
@getPlayerSession
def startAlchemy(serverInfo,alchemyId):
    return alchemy.startAlchemy(serverInfo['playerId'],alchemyId)
    
@getPlayerSession
def finishAlchemy(serverInfo,alchemyId):
    return alchemy.finishAlchemy(serverInfo['playerId'],alchemyId)

@getPlayerSession
def cancelAlchemy(serverInfo,alchemyId):
    return alchemy.cancelAlchemy(serverInfo['playerId'],alchemyId)

@getPlayerSession
def helpAlchemy(serverInfo,param):
    return alchemy.helpAlchemy(serverInfo['playerId'],param['snsName'],param['snsPic'],param['friendId'])

@getPlayerSession
def speedupAlchemy(serverInfo,param):
    return alchemy.speedupAlchemy(serverInfo['playerId'],param)

@getPlayerSession
def speedupSearch(serverInfo,param):
    return search_team.speedupSearch(serverInfo['playerId'],param)

@getPlayerSession
def speedupProduce(serverInfo,param):
    return produce.speedupProduce(serverInfo['playerId'],param)

@getPlayerSession
def helpProduce(serverInfo,param):
    return produce.helpProduce(serverInfo['playerId'],param['snsName'],param['snsPic'],param['friendId'],param['machineId'])

@getPlayerSession
def getDigItemReward(serverInfo):
    return explore_team.getDigItemReward(serverInfo['playerId'])

@getPlayerSession
def getTeamUpInfo(serverInfo,friendId):
    return explore_team.getFriendTeamUpInfo(serverInfo['playerId'],friendId)

@getPlayerSession
def launchTeamUp(serverInfo,launchInfo):
    return explore_team.launchTeamUp(launchInfo)

@getPlayerSession
def joinTeamUp(serverInfo,launchInfo):
    return explore_team.joinTeamUp(launchInfo)

@getPlayerSession
def kickTeamUp(serverInfo,kickedId):
    return explore_team.kickTeamUp(kickedId)
    
@getPlayerSession
def quitTeamUp(serverInfo):
    return explore_team.quitTeamUp(serverInfo['playerId'])

@getPlayerSession
def getStepReward(serverInfo,step):
    return explore_team.getStepReward(serverInfo['playerId'],step)

@getPlayerSession
def presentFestivalGift(serverInfo,presentInfo):
    friendId = presentInfo['friendId']
    giftId = presentInfo['giftId']
    playerName = presentInfo['snsName']
    return festival_gift.presentGift(serverInfo['playerId'],playerName,friendId,giftId)

@getPlayerSession
def startLittleGame(serverInfo):
    return explore_team.startLittleGame(serverInfo['playerId'])
    
@getPlayerSession
def finishLittleGame(serverInfo,info):
    score = info['score']
    gameName = info['gameName']
    securityCode = info['checksum']
    return explore_team.finishLittleGame(serverInfo['playerId'],gameName,score,securityCode)

@getPlayerSession
def startExchangeTask(serverInfo):
    return exchange_task.startExchangeTask(serverInfo['playerId'])

@getPlayerSession
def addLotteryReward(serverInfo):
    return daily_reward.addLotteryReward(serverInfo['playerId'])

@getPlayerSession
def lifeTreeLevelUp(serverInfo,mapId):
    return life_tree.lifeTreeLevelUp(serverInfo['playerId'],mapId)

@getPlayerSession
def launchPurchase(serverInfo,parm):
    returnVal = purchase.launchPurchase(serverInfo['playerId'],parm)
    returnVal['auctionStatus'] = player_module.getAuctionStatus(serverInfo['playerId'])
    return returnVal

@getPlayerSession
def cancelPurchase(serverInfo,purchaseId):
    returnVal = purchase.cancelPurchase(serverInfo['playerId'],purchaseId)
    returnVal['auctionStatus'] = player_module.getAuctionStatus(serverInfo['playerId'])
    return returnVal

@getPlayerSession
def purchaseResponse(serverInfo,parm):
    returnVal = purchase.purchaseResponse(parm['buyer_id'],parm['u_id'],parm['u_name'],parm['auction_id'])
    returnVal['auctionStatus'] = player_module.getAuctionStatus(parm['buyer_id'])
    return returnVal

@getPlayerSession
def getIntervalBoxReward(serverInfo):
    return interval_box.getIntervalBoxReward(serverInfo['playerId'])

@getPlayerSession
def getMapsInfo(serverInfo,parm):
    playerId = parm['playerid']
    habitatId = parm['map_index']
    return item.getMapsInfo(playerId,habitatId)

@getPlayerSession
def sendSearchTeam(serverInfo,parm):
    return search_team.sendSearchTeam(serverInfo['playerId'],parm)

@getPlayerSession
def getSearchTeamInfo(serverInfo):
    return search_team.getSearchTeamInfo(serverInfo['playerId'])

@getPlayerSession
def startGrowth(serverInfo,itemId):
    return player_module.startGrowth(serverInfo['playerId'],itemId)

@getPlayerSession
def stealSearchTeam(serverInfo,param):
    return search_team.stealSearchTeam(param)

@getPlayerSession
def helpHarvest(serverInfo,param):
    return player_module.helpHarvest(serverInfo['playerId'],param)


# Ideally, just the imports and the code below this comment would be
# in the .tac file; the AMF service would be defined in a module of
# your making

# Create a dictionary mapping the service namespaces to a function
# or class instance
services = { 
    'init': initGame,
    'decorativeScene':decorativeScene,
    'getUserInfo':getUserInfo,
    'getFriendsInfo':getFriendsInfo,
    'buyPropInShop':buyPropInShop,
    'sellProps':sellProps,
    'sellPropInBag':sellPropInBag,
    'getSearchTeam':getSearchTeam,
    'Auction':Auction,
    'getAuction':getAuction,
    'getEventLogs':getEventLogs,
    'buyAuction':buyAuction,
    'cancelAuction':cancelAuction,
    'expandMap':expandMap,
    'getAuctionEvent':getAuctionEvent,
    'mix':mix,
    'harvest':harvest,
    'resolve':resolve,
    'getCollection':getCollection,
    'usePropInBag':usePropInBag,
    'levelUp':levelUp,
    'buildingLevelUp':buildingLevelUp,
    'habitatLevelUp':habitatLevelUp,
    'finishCollection':finishCollection,
    'updateItemDetail':updateItemDetail,
    'becomeVIP':becomeVIP,
    'updateUserTitle':updateUserTitle,
    'updateGuide':updateGuide,
    'startTreasure':startTreasure,
    'finishTreasure':finishTreasure,
    'getTreasure':getTreasure,
    'getBoxInfo':getBoxInfo,
    'openBox':openBox,
    'visitFriendRewards':visitFriend,
    'doDailyTask':doDailyTask,
    'updateDailyTask':updateDailyTask,
    'startProduce':startProduce,
    'cancelProduce':cancelProduce,
    'finishProduce':finishProduce,
    'acceptSystemReward':acceptSystemReward,
    'startExchange':startExchange,
    'updateLevelTaskInfo':updateLevelTaskInfo,
    'finishLevelTask':finishLevelTask,
    'decorateInBag':decorateInBag,
    'decorateInShop':decorateInShop,
    'decorateGroupInShop':decorateGroupInShop,
    'expandBagCapacity':expandBagCapacity,
    'refining':refining,
    'getAlchemyInfo':getAlchemyInfo,
    'startAlchemy':startAlchemy,
    'finishAlchemy':finishAlchemy,
    'cancelAlchemy':cancelAlchemy,
    'helpAlchemy':helpAlchemy,
    'speedupAlchemy':speedupAlchemy,
    'speedupSearch':speedupSearch,
    'speedupProduce':speedupProduce,
    'helpProduce':helpProduce,
    'getDigItemReward':getDigItemReward,
    'getTeamUpInfo':getTeamUpInfo,
    'launchTeamUp':launchTeamUp,
    'joinTeamUp':joinTeamUp,
    'kickTeamUp':kickTeamUp,
    'quitTeamUp':quitTeamUp,
    'getStepReward':getStepReward,
    'presentFestivalGift':presentFestivalGift,
    'startLittleGame':startLittleGame,
    'finishLittleGame':finishLittleGame,
    'startExchangeTask':startExchangeTask,
    'addLotteryReward':addLotteryReward,
    'lifeTreeLevelUp':lifeTreeLevelUp,
    'launchPurchase':launchPurchase,
    'cancelPurchase':cancelPurchase,
    'purchaseResponse':purchaseResponse,
    'getIntervalBoxReward':getIntervalBoxReward,
    'getMapsInfo':getMapsInfo,
    'sendSearchTeam':sendSearchTeam,
    'getSearchTeamInfo':getSearchTeamInfo,
    'startGrowth':startGrowth,
    'stealSearchTeam':stealSearchTeam,
    'helpHarvest':helpHarvest,
}

# Place the namespace mapping into a TwistedGateway
logger = logging.getLogger(__file__)
gateway = TwistedGateway(services, logger=logger, expose_request=False,
                         debug=True)

# A base root resource for the twisted.web server
root = resource.Resource()

# Publish the PyAMF gateway at the root URL
root.putChild('', gateway)

print 'Running AMF gateway on http://localhost:%s' % (SERVER_PORT)
print 'PLATFORM:',PLATFORM
print 'DATABASE_TYPE:',DATABASE_TYPE,'-',dbhost
print 'MEMCACHE_SERVER:',MEMCACHE_SERVER

application = service.Application('kakaZoo Server')
#description type:port like 'tcp:80','udp:80','ssl:80'
description = 'tcp:%s' % (SERVER_PORT)
server = strports.service(description, server.Site(root))
server.setServiceParent(application)

