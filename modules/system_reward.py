#-*- coding=utf8 -*-
from settings import *

from config.systemReward_config import *

import time
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool

#获取系统奖励信息
#多个奖励用“|”分割
def getSystemRewardInfo(playerId):
    player = db_tool.__getPlayerById(playerId)
    system_reward = player['system_reward']
    return system_reward

#领取系统奖励
def acceptSystemReward(playerId,sysRewardId):
    
    if not str(sysRewardId):
        return {'status':0,'msg':'no sysRewardId'}
    
    player = db_tool.__getPlayerById(playerId)
    system_reward = player['system_reward']
    system_reward_list = str2list(system_reward)
    if str(sysRewardId) in system_reward_list:
        #更新领取状态
        system_reward_list.remove(str(sysRewardId))
        db_tool.__updatePlayer(playerId,{'system_reward':list2str(system_reward_list)})
        
        #给与奖励
        for systemReward in SYSTEM_REWARD_CONFIG[sysRewardId]:
            system_reward_type = systemReward['type']
            system_reward_num = systemReward['num']
            db_tool.addPropAndMoney(playerId,system_reward_type,system_reward_num)
        
        propDict = db_tool.getAllProp(playerId)
        player = db_tool.__getPlayerById(playerId)
        
        return {'status':1,'sysRewardId':sysRewardId,'player':player,'bag':propDict}
    else:
        return {'status':0,'msg':'no sysRewardId '+str(sysRewardId)}

'''
#获取系统奖励信息
@getOneDBConn
def getSysRewardById(db,conn,playerId):
    db.execute("select * from system_reward where player_id=%s",(playerId,))
    sysReward = db.fetchone()
    if not sysReward:
        time_now = int(time.time())
        sysReward = {}
        sysReward['player_id'] = playerId
        db.execute("insert into system_reward (player_id,create_time,info) values(%s,%s,%s)",(playerId,time_now,''))
    return sysReward
'''

def str2list(astr):
    alist = []
    if len(astr)>0:
        alist = astr.split('|')
    return alist

def list2str(alist):
    if(not alist):
        alist = list()
    return '|'.join(alist)