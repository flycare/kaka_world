#-*- coding=utf8 -*-
from twisted.web import resource, server , static, http 
from twisted.application import service, strports
from pyamf.remoting.gateway.twisted import TwistedGateway
from pyamf.remoting.gateway import expose_request

import sys
import os
C_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(C_PATH)

from settings import *
from config.item_config import *
from config.prop_config import *
from config.expand_config import *
from config.drawing_config import *
from config.energy_config import *

import modules.auction as auction
import modules.collection as collection
import modules.db_tool as db_tool
import modules.friend as friend
import modules.item as item
import modules.player as player
import modules.prop as prop
import modules.search_team as search_team
import modules.session as session
import modules.user_box as user_box
import modules.daily_reward as daily_reward
import modules.daily_task as daily_task
import modules.level_task as level_task
import modules.produce as produce
import modules.system_reward as system_reward
import modules.exchange as exchange
import modules.alchemy as alchemy
import modules.invite as invite

import time

def getPlayerSession(func):
    def wapper(*args):

        serverInfo = args[0]
        
        #print('serverInfo ==== ',serverInfo)
        #initPlayer(serverInfo['sns_id'])
        
        skey = serverInfo['session_id']
        player_id,sns_id = session.getSession(skey)
        
        #验证playerId是否存在
        if not player_id:
            return {'status':500,'msg':'getPlayerSession '+sns_id}
        
        serverInfo['playerId'] = player_id
        #print '--------------------------',serverInfo['playerId']
        #session_key = serverInfo['sessionkey']
        #serverInfo['sns_id'] = serverInfo['snsid']
        #serverInfo['session_key'] = session_key
        #del serverInfo['snsid']
        del serverInfo['session_id']
        #del serverInfo['sessionkey']
        if len(args)>1:
            return func(serverInfo,args[1])
        else:
            return func(serverInfo)
        '''
        try:
            param = args[1]
            return func(serverInfo,param)
        except:
            return func(serverInfo)
        '''
    return wapper

def hstoreToDict(hstore):
    return eval("{"+hstore+"}")

def init(serverInfo,is_fan):
    playerId = serverInfo['playerId']
    sig = serverInfo['sig']
    session_key = serverInfo['session_key']
    sns_id = serverInfo['sns_id']

    #add daily reward
    dailyReward = daily_reward.getDailyReward(playerId,is_fan);
    
    #get player info
    player = db_tool.__getPlayerById(playerId)
    if not player:
        db_tool.__insertNewPlayer(sns_id)
        player = db_tool.__getPlayer(sns_id)
    
    time_now = int(time.time())

    db_tool.__updateEnergy(player)
    #snsObj = getSnsObj(sig,session_key,sns_id)
    #snsInfo = snsObj.getUserInfo()
    #player['name']=snsInfo['name']
    #player['tinyurl']=snsInfo['tinyurl']
    
    returnVal = {'status':1}
    
    returnVal['player'] = player
    #friends = db_tool.__getFriends(snsObj)
    #returnVal['friends'] = friends
    returnVal['map'] = db_tool.getMapsbyPlayerId(playerId)
    returnVal['searcher'] = search_team.getSearchTeamInfo(playerId)
    returnVal['bag'] = db_tool.getAllProp(playerId)
    returnVal['bagMax'] = prop.getBagCapacity(playerId)
    returnVal['collection'] = collection.getCollection(playerId)
    returnVal['time_now']=time_now
    returnVal['box_status']=user_box.getUserBoxStatus(sns_id)
    returnVal['daily_reward']=dailyReward
    returnVal['daily_task']=daily_task.getTaskInfo(playerId)
    returnVal['level_task']=level_task.getLevelTaskInfo(playerId)
    returnVal['produce']=produce.getProduceList(playerId)
    returnVal['invite_info']=invite.getInviteInfo(sns_id)
    returnVal['system_reward']=system_reward.getSystemRewardInfo(playerId)
    returnVal['alchemy']=alchemy.getAlchemyInfo(playerId)
    return returnVal


#gateway函数

@getPlayerSession
def initGame(serverInfo,is_fan):
    return init(serverInfo,is_fan)     

@getPlayerSession
def getPlayerBag(serverInfo,param=0):
    #return player.getPlayerBag(serverInfo['playerId'])
    pass

@getPlayerSession
def decorativeScene(serverInfo,param):
    return item.decorativeScene(serverInfo,param)
    

def getUserInfo(serverInfo,param):
    return player.getUserInfo(param)

@getPlayerSession
def getFriendsInfo(serverInfo,param):
    returnVal = {}
    returnVal = db_tool.getFriendsInfo(param)
    returnVal['visit_info'] = friend.getVisitFriends(serverInfo['playerId'])
    return returnVal
        
@getPlayerSession
def buyPropInShop(serverInfo,param):
    return prop.buyPropInShop(serverInfo['playerId'],param)
        
@getPlayerSession
def sellPropInBag(serverInfo,param):
    return prop.sellPropInBag(serverInfo['playerId'],param)

@getPlayerSession        
def becomeVIP(serverInfo,param):
    return prop.becomeVIP(serverInfo['playerId'],param)   

@getPlayerSession
def getSearchTeam(serverInfo):
    return search_team.getSearchTeam(serverInfo['playerId'])
        
@getPlayerSession
def Auction(serverInfo,param):
    return auction.Auction(serverInfo['playerId'],param)
    
@getPlayerSession    
def getAuction(serverInfo,playerId):
    return auction.getAuction(playerId)
        
@getPlayerSession
def buyAuction(serverInfo,info):
    return auction.buyAuction(serverInfo['playerId'],info['auctionId'],info['name'])
        
@getPlayerSession
def cancelAuction(serverInfo,id):
    return auction.cancelAuction(serverInfo['playerId'],id)
        
@getPlayerSession
def expandMap(serverInfo,type):
    #snsObj = getSnsObj()
    snsObj = []
    return player.expandMap(serverInfo['playerId'],type,snsObj)
        
@getPlayerSession
def getAuctionEvent(serverInfo,playerId):
    return auction.getAuctionEvent(serverInfo['playerId'])
        
@getPlayerSession
def mix(serverInfo,definitionId):
    return collection.mix(serverInfo['playerId'],definitionId)
        
@getPlayerSession
def harvest(serverInfo,param):
    return player.harvest(serverInfo['playerId'],param)
        
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
    return player.levelUp(serverInfo['playerId'])

@getPlayerSession        
def buildingLevelUp(serverInfo,array):
    return item.buildingLevelUp(serverInfo['playerId'],array)

@getPlayerSession
def finishCollection(serverInfo,definitionId):
    return collection.finishCollection(serverInfo['playerId'],definitionId)
    
@getPlayerSession
def updateItemDetail(serverInfo,info):
    #print id,'---------',item_detail
    return item.updateDetail(serverInfo['playerId'],info['id'],info['detail'])    


@getPlayerSession
def updateUserTitle(serverInfo,title_id):
    return player.updateTitle(serverInfo['playerId'],title_id)  


@getPlayerSession
def updateGuide(serverInfo,guide_id):
    return player.updateGuide(serverInfo['playerId'],guide_id) 


@getPlayerSession
def startTreasure(serverInfo,info):
    return player.startTreasure(serverInfo['playerId'],info)  

@getPlayerSession
def finishTreasure(serverInfo,info):
    return player.finishTreasure(serverInfo['playerId'],info) 


@getPlayerSession
def getTreasure(serverInfo,info):
    return player.getTreasure(serverInfo['playerId'],info) 

@getPlayerSession
def setSearchArea(serverInfo,area):
    return search_team.setSearchArea(serverInfo['playerId'],area)

@getPlayerSession
def getBoxInfo(serverInfo):
    return user_box.getBoxInfo(serverInfo['sns_id'])

@getPlayerSession
def openBox(serverInfo):
    return user_box.openBox(serverInfo['sns_id'])

@getPlayerSession
def updateDailyTask(serverInfo,info):
    return daily_task.updateDailyTask(serverInfo['playerId'],info['task_id'],info['status']);

#初次访问好友或每日访问好友 领取奖励
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
def startExchange(serverInfo,exchangeId):
    return exchange.startExchange(serverInfo['playerId'],exchangeId)

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
def expandBagCapacity(serverInfo,parms):
    return prop.expandBagCapacity(serverInfo['playerId'],parms)

@getPlayerSession
def refining(serverInfo,param):
    definitionId = param['definitionId']
    definitionNum = param['number']
    return collection.refining(serverInfo['playerId'],definitionId,definitionNum)

@getPlayerSession
def getAlchemyInfo(serverInfo):
    #return alchemy.getAlchemyInfo(serverInfo['playerId'])
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
    return produce.speedupProduce(serverInfo['playerId'],param['machineId'],param['num'])

@getPlayerSession
def helpProduce(serverInfo,param):
    return produce.helpProduce(serverInfo['playerId'],param['snsName'],param['snsPic'],param['friendId'],param['machineId'])

@getPlayerSession
def helpSearch(serverInfo,param):
    return search_team.helpSearch(serverInfo['playerId'],param['snsName'],param['snsPic'],param['friendId'])

'''
@getPlayerSession
def getDailyReward(serverInfo):
    return daily_reward.getDailyReward(serverInfo['playerId']);
'''

def initPlayer(sns_id):
    time_now = time.time()
    player = db_tool.__getPlayer(sns_id)
    if not player:
        #初始化玩家信息+搜索队+道具+地图+session对应表
        playerId = db_tool.__insertNewPlayer(sns_id)
        db_tool.__insertPlayerSeacher(playerId)
        db_tool.__insertItem(playerId)
        db_tool.__insertProp(playerId)
        session.setSession(sns_id)
    else:
        return 0

'''
def getSnsObj(sig=0,session_key=0,sns_id=0):
    if SERVER_PLATFORM == 'localhost':
        from sns_api.local import Local
        snsObj = Local()
    elif SERVER_PLATFORM == 'renren':
        from sns_api.pyxn import XnApi
        snsObj = XnApi(sig,session_key,sns_id)
    return snsObj

class StaticHtml(resource.Resource):  
    def render_GET(self, request):  
        global db,conn,logging,db_tool
        request.setResponseCode(200)
        xn_params = request.args
        if xn_params['xn_sig_added'][0] == '0':
            file = open("static/template/welcome.html","r")
            content = file.read()
        else:
            #global sns_id,session_key,sig
            sns_id = str(request.args['xn_sig_user'][0])
            session_key = request.args['xn_sig_session_key'][0]
            sig = request.args['xn_sig'][0]
            initPlayer(sns_id)
            skey = session.setSession(sns_id)
            file = open("static/template/index.html","r")
            content = file.read()
            content = content.replace('[[snsid]]',sns_id)
            content = content.replace('[[sig]]',sig)
            content = content.replace('[[sessionkey]]',session_key)
            print 'skey-----------',skey
            content = content.replace('[[sessionid]]',skey)
            #content = content.replace('[[uids]]',str(sns_id))
            #from testapi.pyxn import *
            #xn = Xiaonei(api_key="826073379185423c8afd217cb44ab169", secret_key="d62a657f3b77409aa508323c016b557f", app_name="kakaworld", callback_path="http://1.85.2.109:8080/index", internal=True)
            #if not xn.check_session(request): #如需使用xn调用api，xn.check_session(request)这步是必须的
            #return xn.redirect(xn.get_login_url())

        return content
'''
# Ideally, just the imports and the code below this comment would be
# in the .tac file; the AMF service would be defined in a module of
# your making

# Create a dictionary mapping the service namespaces to a function
# or class instance
services = { 
    'init': initGame,
    'getPlayerBag':getPlayerBag,
    'decorativeScene':decorativeScene,
    'getUserInfo':getUserInfo,
    'getFriendsInfo':getFriendsInfo,
    'buyPropInShop':buyPropInShop,
    'sellPropInBag':sellPropInBag,
    'getSearchTeam':getSearchTeam,
    'Auction':Auction,
    'getAuction':getAuction,
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
    'finishCollection':finishCollection,
    'updateItemDetail':updateItemDetail,
    'becomeVIP':becomeVIP,
    'updateUserTitle':updateUserTitle,
    'updateGuide':updateGuide,
    'startTreasure':startTreasure,
    'finishTreasure':finishTreasure,
    'getTreasure':getTreasure,
    'setSearchArea':setSearchArea,
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
    'helpSearch':helpSearch,
}

# Place the namespace mapping into a TwistedGateway
logger = logging.getLogger(__file__)
gateway = TwistedGateway(services, logger=logger, expose_request=False,
                         debug=True)

# A base root resource for the twisted.web server
root = resource.Resource()

# Publish the PyAMF gateway at the root URL
root.putChild('', gateway)
''''
if SERVER_PLATFORM == "localhost":
    pass
else:
    root.putChild('index', StaticHtml())
    
root.putChild('swfobject',static.File('static/swfobject'))
root.putChild('flash',static.File('static/flash'))
root.putChild('data',static.File('static/flash/data'))
root.putChild('static',static.File('static/'))
root.putChild('resource',static.File('static/flash/resource'))
root.putChild('xd_receiver.html',static.File('xd_receiver.html'))
'''
root.putChild('crossdomain.xml',static.File('crossdomain.xml'))


print 'Running AMF gateway on http://localhost:8080'

application = service.Application('kakaZoo Server')
server = strports.service('tcp:8081', server.Site(root))
server.setServiceParent(application)

