#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.daily_config import *
from config.explore_config import *

import time
import random
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.festival_gift as festival_gift
import modules.explore_reward as explore_reward
import modules.time_tool as time_tool

#每日奖励
def getDailyReward(playerId,isfan):
    #get player
    player = db_tool.__getPlayerById(playerId)
    #if(not player):
    #    return {'status':0,'msg':'player not exist'}
    #compare login time
    todayTime = int(time.time())
    lastLoginTime = player['last_login_time']
    
    #get login times
    login_times = player['login_times']
    lottery_num = player['lottery_num']
    
    #计算连续登录天数
    
    if(time_tool.isToday(lastLoginTime)):
        return {'lottery_num':lottery_num,'login_times':login_times}
    elif(time_tool.isYesterday(lastLoginTime)):
        login_times+=1
    else:
        login_times = 1

    #根据登录天数赠送金币+抽奖次数
    rewardDays = login_times
    if rewardDays>5:
        rewardDays = 5
    rewardGg = DAILY_CONFIG[rewardDays]['gb']
    rewardLotteryNum = DAILY_CONFIG[rewardDays]['lotteryNum']
    
    player['gb'] += rewardGg
    player['lottery_num'] = rewardLotteryNum
    
    #vip多一次抽奖机会
    #if player['vip']>todayTime:
    #    player['lottery_num'] += 1
    
    #赠送免费挖宝次数
    if(isfan):
        free_treasure_times = 4
    else:
        free_treasure_times = 3
    free_times = player['free_times']+free_treasure_times
    
    #每日送免费能量
    player['help_energy'] = 50
    
    db_tool.__updatePlayer(player['id'],{'free_times':free_times,
                                         'gb':player['gb'],
                                         'lottery_num':player['lottery_num'],
                                         'last_login_time':todayTime,
                                         'login_times':login_times,
                                         'help_energy':player['help_energy']})
    
    return {'lottery_num':player['lottery_num'],'login_times':login_times}


#添加每日奖励
def addLotteryReward(playerId):
    
    player = db_tool.__getPlayerById(playerId)
    lottery_num = player['lottery_num']
    
    if lottery_num == 0:
        return {'status':0,'msg':'lottery_num == 0'}
    else:
        lottery_num -= 1
    
    db_tool.__updatePlayer(player['id'],{'lottery_num':lottery_num})
    
    rewardList = DAILY_REWARD_CONF['common']
    todayTime = int(time.time())
    if player['vip']>todayTime:
        rewardList = rewardList + DAILY_REWARD_CONF['vip']
    
    rewardInfo = random.choice(rewardList)
    rewardType = rewardInfo['definitionID']
    rewardNum = rewardInfo['num']
    
    prop = db_tool.getAllProp(playerId)
    db_tool.__addPropItem(prop,rewardType,rewardNum)
    db_tool.saveAllProp(playerId,prop)

    return {'status':1,'bag':prop,'definitionID':rewardType,'num':rewardNum}
    

#节日期间的每日奖励
def getFestivalDailyReward(playerId):
    todayTime = int(time.time())
    startTime = time_tool.str2sec('2011-09-08 00:00:00')
    endTime = time_tool.str2sec('2011-10-16 00:00:00')
    
    #不再节日期间
    if todayTime<startTime or todayTime>endTime:
        return {}
    
    #小红旗10个
    giftId = 10100
    giftNum = 10
    receivedInfo = festival_gift.receiveGift(playerId,giftId,giftNum)
    retVal = {}
    retVal['definitionId'] = int(receivedInfo['giftId'])
    retVal['number'] = receivedInfo['giftNum']
    retVal['friends'] = receivedInfo['friends']
    return retVal


#领取虎符
#每周赠送两个（每人最多两个）
def getWeeklyReward(playerId):
    todayTime = int(time.time())
    addReward = False
    
    rewardInfo = explore_reward.getExploreRewardInfo(playerId)

    if not rewardInfo:
        rewardInfo = {}
        rewardInfo['player_id'] = playerId
        rewardInfo['create_time'] = todayTime
        explore_reward.saveExploreRewardInfo(rewardInfo)
        
        addReward = True
    else:
        #if time_tool.getIntervalDays(rewardInfo['create_time']) >= 3:
        if time_tool.getWeekNum(rewardInfo['create_time']) != time_tool.getWeekNum(todayTime):
            
            updRewardInfo = {}
            updRewardInfo['create_time'] = todayTime
            explore_reward.updateExploreRewardInfo(playerId,updRewardInfo)
            
            addReward = True
    
    #每周赠送两个（每人最多两个）
    if addReward:
        propDict = db_tool.getAllProp(playerId)
        #db_tool.__addPropItem(propDict,EXPLORE_NEED_PROPID,2)
        propDict[EXPLORE_NEED_PROPID] = 2
        db_tool.saveAllProp(playerId,propDict)