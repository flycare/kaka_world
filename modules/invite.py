#-*- coding=utf8 -*-
from settings import *

from config.invite_config import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.system_reward as system_reward_module


#获得邀请信息
@getOneDBConn
def getInviteInfo(db,conn,snsId):
    
    db.execute("SELECT * FROM invite WHERE invite_id = %s",(snsId,))
    invite = db.fetchone()
    
    #好友增长个数
    inviteIncrement = INVITE_INCREMENT_CONFIG['increment']
    
    if(not invite):
        #系统奖励
        system_reward_id = INVITE_CONFIG[inviteIncrement]['id']
        system_reward_num = INVITE_CONFIG[inviteIncrement]['num']
        #总邀请数
        total_invites_num = 0
        #邀请的好友
        invites = []
    else:
        inviteFriends = invite['accepter_ids']
        sysRewardTimes = invite['sys_reward_times']
        
        #总邀请数
        total_invites_num = len(friendstr2list(inviteFriends))
        
        #本次系统应该奖励次数
        if sysRewardTimes == 0:
            cur_sys_reward_times = total_invites_num/inviteIncrement
        else:
            remainSysRewardTimes = total_invites_num-sysRewardTimes*inviteIncrement
            cur_sys_reward_times = remainSysRewardTimes/inviteIncrement
        
        #添加本次系统奖励
        if cur_sys_reward_times > 0:
            sysRewardTimes = updateInviteReward(snsId,sysRewardTimes,cur_sys_reward_times)
            
        #本次邀请的好友
        invites = currentInviteFriends(inviteFriends,sysRewardTimes)
        
        #下次获得的系统奖励
        nextReward = (sysRewardTimes+1)*inviteIncrement
        
        #大于20个后配置相同
        if nextReward > 20:
            nextReward = 20
        system_reward_num = INVITE_CONFIG[nextReward]['num']
        
    return {'invites':invites,'total_invite_num':total_invites_num,'sys_reward_num':system_reward_num}
    

#本次邀请的好友
def currentInviteFriends(friendstr,sysRewardTimes):
    friendList = friendstr2list(friendstr)
    inviteIncrement = INVITE_INCREMENT_CONFIG['increment']
    
    totalCounts = len(friendList)
    #当前邀请数
    curCounts = totalCounts%inviteIncrement
    
    start = (sysRewardTimes)*inviteIncrement
    end = (sysRewardTimes+1)*inviteIncrement
    
    curList = friendList[start:end]
    return curList


#更新奖励信息
@getOneDBConn
def updateInviteReward(db,conn,snsId,alreadyRewardTimes,curRewardTimes):
    player = db_tool.__getPlayer(snsId)
    playerId = player['id']
    system_reward = player['system_reward']
    system_reward_list = system_reward_module.str2list(system_reward)

    #更新系统奖励
    all_sys = system_reward_list+getSysRewardBoxs(alreadyRewardTimes,curRewardTimes)
    system_reward = system_reward_module.list2str(all_sys)
    
    db_tool.__updatePlayer(playerId,{'system_reward':system_reward})
    
    totalRewardTimes = alreadyRewardTimes+curRewardTimes
        
    db.execute("update invite set sys_reward_times=%s where invite_id=%s",(totalRewardTimes,snsId))
    conn.commit()
    
    return totalRewardTimes


#获得系统奖励箱子
def getSysRewardBoxs(alreadyRewardTimes,curRewardTimes):
    boxs = []
    
    #好友增长个数
    inviteIncrement = INVITE_INCREMENT_CONFIG['increment']
    
    for index in range(curRewardTimes):
        
        curReward = (alreadyRewardTimes+index+1)*inviteIncrement
        #大于20个后配置相同
        if curReward > 20:
            curReward = 20
        
        system_reward_id = INVITE_CONFIG[curReward]['id']
        system_reward_num = INVITE_CONFIG[curReward]['num']
        
        boxs += [str(system_reward_id)]*system_reward_num
        
    return boxs
    
def friendstr2list(inviteFriends):
    return inviteFriends.split(':')