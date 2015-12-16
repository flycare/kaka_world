#-*- coding=utf8 -*-
from settings import *
from config.explore_config import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.random_tool as random_tool
#a circular dependency
#a import b,and b import a
import player as player_module
import random
import hashlib

#获取挖的奖励
def getDigItemReward(playerId):
    #奖励
    rewardGb = 0
    rewardEnergy = 0
    rewardDefinitionId = 0
    
    #消耗能量
    costEnergy = 1
    
    player = db_tool.__getPlayerById(playerId)
    #更新能量
    player = player_module.__updateEnergy(player)
    
    if player['energy'] < costEnergy:
        return {'status':0,'msg':'not enough energy.'}
    
    #扣除能量
    player['energy'] -= costEnergy
    
    #获取背包信息
    propDict = db_tool.getAllProp(playerId)
    
    oddsInfo = EXPLORE_DIG_REWARD_CONFIG[1]
    
    random_table_key = 'explore_dig_random_table_1'
    rewardItems = random_tool.getRandomItemList(random_table_key,oddsInfo)

    for odds in rewardItems:
        rewardType = odds['type']
        rewardNum = odds['num']

        #金币
        if rewardType == 2:
            rewardGb = rewardNum
            player['gb'] += rewardNum
        #能量
        elif rewardType == 4:
            rewardEnergy = rewardNum
            player['energy'] += rewardNum
        #钥匙
        else:
            rewardDefinitionId = rewardType
            db_tool.__addPropItem(propDict,rewardType,rewardNum)
            db_tool.saveAllProp(playerId,propDict)
    
    #更新player
    db_tool.__updatePlayer(playerId,{'gb':player['gb'],'energy':player['energy'],'last_energy_time':player['last_energy_time']})
    
    returnVal = {
        'status':1,
        'gb':rewardGb,
        'energy':rewardEnergy,
        'definitionId':rewardDefinitionId,
        'player':player,
        'bag':propDict
    }
    return returnVal

#是否开始组队
def isExploreStart(playerId):
    personInfo = getExploreInfo(playerId)
    if personInfo:
        return True
    else:
        return False

#得到组队信息
def getTeamUpInfo(playerId):
    personInfo = getExploreInfo(playerId)
    exploreInfo = {}
    if personInfo:
        leader = personInfo['leader']
        teamInfo,membersInfo = getExploreMembers(playerId)
        
        exploreInfo['floor'] = teamInfo['floor']
        exploreInfo['step'] = teamInfo['step']
        exploreInfo['totalScore'] = teamInfo['total_score']
        exploreInfo['reward'] = personInfo['reward']
        exploreInfo['member'] = membersInfo
        exploreInfo['leader'] = leader
        
    return {'status':1,'teamInfo':exploreInfo}


#得到好友的组队信息
def getFriendTeamUpInfo(playerId,friendId):
    personInfo = getExploreInfo(playerId)
    
    #自己是否已经加入组队
    if personInfo:
        joined = True
    else:
        joined = False
    
    returnVal = getTeamUpInfo(friendId)
    returnVal['joined'] = joined
    
    #只能在自己的队伍中看到奖励
    if personInfo and returnVal['teamInfo']:
        
        if returnVal['teamInfo']['leader'] == personInfo['leader']:
            returnVal['teamInfo']['reward'] = personInfo['reward']
        else:
            returnVal['teamInfo']['reward'] = ''
        
    return returnVal


#发起组队
def launchTeamUp(launchInfo):
    snsName = launchInfo['name']
    snsPic = launchInfo['imageUrl']
    floor = launchInfo['floor']
    playerId = launchInfo['id']
    
    propDict = db_tool.getAllProp(playerId)
    
    if not propDict.has_key(EXPLORE_NEED_PROPID) or propDict[EXPLORE_NEED_PROPID] < 1:
        return {'status':0,'msg':'need more definitionId '+str(EXPLORE_NEED_PROPID)}
    
    exploreInfo = {}
    exploreInfo['player_id'] = playerId
    exploreInfo['leader'] = playerId
    exploreInfo['score'] = 0
    exploreInfo['reward'] = ''
    exploreInfo['sns_name'] = snsName
    exploreInfo['sns_pic'] = snsPic
    
    personInfo = getExploreInfo(playerId)
    if personInfo:
        return {'status':0,'msg':'can not launchTeamUp'}
    else:
        addExploreInfo(exploreInfo)
    
    teamInfo = {}
    teamInfo['leader_id'] = playerId
    teamInfo['total_score'] = 0
    teamInfo['floor'] = floor
    teamInfo['step'] = 1
    addExploreTeamInfo(teamInfo)
    
    db_tool.__subtractPropItem(propDict,EXPLORE_NEED_PROPID,1)
    db_tool.saveAllProp(playerId,propDict)
    
    #add eventlog
    eventInfo = {'snsName':snsName}
    addExploreEventLog(playerId,1,eventInfo)
    
    returnVal = getTeamUpInfo(playerId)
    returnVal['bag'] = propDict
    return returnVal


#加入队伍
def joinTeamUp(launchInfo):
    playerId = launchInfo['id']
    snsName = launchInfo['name']
    snsPic = launchInfo['imageUrl']
    leader = launchInfo['leader']
    
    propDict = db_tool.getAllProp(playerId)
    
    if not propDict.has_key(EXPLORE_NEED_PROPID) or propDict[EXPLORE_NEED_PROPID] < 1:
        return {'status':0,'msg':'need more definitionId '+str(EXPLORE_NEED_PROPID)}
        
    exploreInfo = {}
    exploreInfo['player_id'] = playerId
    exploreInfo['leader'] = leader
    exploreInfo['score'] = 0
    exploreInfo['reward'] = ''
    exploreInfo['sns_name'] = snsName
    exploreInfo['sns_pic'] = snsPic
    
    personInfo = getExploreInfo(playerId)
    if personInfo:
        return {'status':0,'msg':'can not joinTeamUp'}
    else:
        #判断成员个数
        memberCounts = getMemberCounts(leader)
        if memberCounts >= 5:
            return {'status':0,'msg':'can not joinTeamUp ... has full member'}
        
        addExploreInfo(exploreInfo)
        
    db_tool.__subtractPropItem(propDict,EXPLORE_NEED_PROPID,1)
    db_tool.saveAllProp(playerId,propDict)
    
    #add eventlog
    leaderInfo = getExploreInfo(leader)
    eventInfo = {'snsName':snsName}
    eventInfo['leaderName'] = leaderInfo['sns_name']
    addExploreEventLog(leader,2,eventInfo)
    
    returnVal = getTeamUpInfo(playerId)
    returnVal['bag'] = propDict
    return returnVal


#踢出队伍
def kickTeamUp(kickedId):
    personInfo = getExploreInfo(kickedId)
    
    if not personInfo:
        return {'status':0,'msg':'kickTeamUp: has quited or not exist'}
        
    leader = personInfo['leader']
    teamInfo = getExploreTeamInfo(leader)
    
    if kickedId == leader:
        return {'status':0,'msg':'kickTeamUp: leader == kickedId'}
    
    exploreInfo = {}
    exploreInfo['leader'] = kickedId
    updateExploreInfo(kickedId,exploreInfo)
    
    #扣除被踢出玩家分数
    updateExploreTeamScore(leader,-personInfo['score'])
    
    newTeamInfo = teamInfo
    newTeamInfo['leader_id'] = kickedId
    newTeamInfo['total_score'] = personInfo['score']
    addExploreTeamInfo(newTeamInfo)
    
    #add eventlog
    leaderInfo = getExploreInfo(leader)
    eventInfo = {'snsName':personInfo['sns_name']}
    eventInfo['leaderName'] = leaderInfo['sns_name']
    addExploreEventLog(leader,4,eventInfo)
    addExploreEventLog(kickedId,4,eventInfo)
    
    return getTeamUpInfo(leader)
    

#退出组队
def quitTeamUp(playerId):
    personInfo = getExploreInfo(playerId)
    leader = personInfo['leader']
            
    #add eventlog (before del)
    leaderInfo = getExploreInfo(leader)
    eventInfo = {'snsName':personInfo['sns_name']}
    eventInfo['leaderName'] = leaderInfo['sns_name']
    addExploreEventLog(leader,3,eventInfo)
    
    #团队及成员信息
    teamInfo,membersInfo = getExploreMembers(leader)
    
    #是否删除团队所有信息
    delTeamInfo = False
    
    #队长退出
    if playerId == leader:
        #是否有新队长
        hasNewLeader = False
        
        for member in membersInfo:
            if(playerId != member['player_id']):
                nextLeader = member
                hasNewLeader = True
                break
        
        if(hasNewLeader):
            oldLeader = leader
            newLeader = nextLeader['player_id']
            updateExploreLeader(oldLeader,newLeader)
            leader = newLeader
        else:
            delTeamInfo = True
            
    else:
        pass
    
    #删除探索信息
    if delTeamInfo:
        delExploreAndTeamInfo(leader)
    else:
        delExploreInfo(playerId)
        if teamInfo['step'] != 4:
            updateExploreTeamScore(leader,-personInfo['score'])
    
    return getTeamUpInfo(leader)


#开始小游戏
def startLittleGame(playerId):
    propDict = db_tool.getAllProp(playerId)
    
    if not propDict.has_key(LITTLEGAME_NEED_PROPID) or propDict[LITTLEGAME_NEED_PROPID] < 1:
        return {'status':0,'msg':'need more definitionId '+str(LITTLEGAME_NEED_PROPID)}
        
    db_tool.__subtractPropItem(propDict,LITTLEGAME_NEED_PROPID,1)
    db_tool.saveAllProp(playerId,propDict)
    
    return {'status':1,'bag':propDict}
    
    
#完成小游戏
def finishLittleGame(playerId,gameName,score,securityCode):
    
    #验证分数是否合法
    securityStr = str(score)+'无敌咔咔'
    verifyCode = hashlib.md5(securityStr).hexdigest()
    if verifyCode != securityCode:
        return {'status':0,'msg':'finishLittleGame:security code error'}
    
    personInfo = getExploreInfo(playerId)
    leader = personInfo['leader']

    #需要修改的个人信息
    exploreInfo = {}
    exploreInfo['score'] = personInfo['score']+score
    updateExploreInfo(playerId,exploreInfo)
    
    #需要修改的团队信息
    enterNextStep,teamInfo = updateExploreTeamScore(leader,score)
    
    if enterNextStep:
        #领取上一阶段奖励
        floor = teamInfo['floor']
        step = teamInfo['step']-1
        
        if not EXPLORE_CONFIG[floor].has_key(step):
            return {'status':0,'msg':'EXPLORE_CONFIG has no step '+str(step)}
        
        addStepReward(leader,floor,step)
    
    #add eventlog
    eventInfo = {'snsName':personInfo['sns_name']}
    eventInfo['score'] = score
    eventInfo['gameName'] = gameName
    addExploreEventLog(leader,7,eventInfo)
    
    returnVal = getTeamUpInfo(leader)
    returnVal['score'] = score
    return returnVal
    

#添加阶段奖励
def addStepReward(leaderId,floor,step):
    teamInfo,membersInfo = getExploreMembers(leaderId)

    if EXPLORE_CONFIG[floor].has_key(step):
        reward = EXPLORE_CONFIG[floor][step]['reward']
        reward = str(reward)
        for member in membersInfo:
            personRewardList = rewardstr2list(member['reward'])
            personRewardList.append(reward)
            personRewardStr = list2rewardstr(personRewardList)
            updateExploreInfo(member['player_id'],{'reward':personRewardStr})
    

#领取阶段奖励
def getStepReward(playerId,step):
    personInfo = getExploreInfo(playerId)
    
    teamInfo,membersInfo = getExploreMembers(playerId)
    floor = teamInfo['floor']
    rewardId = (floor-1)*3+step
    
    rewardList = rewardstr2list(personInfo['reward'])
    rewardId = str(rewardId)
    if rewardId not in rewardList:
        return {'status':0,'msg':'has no step reward '+rewardId}
    
    rewardList.remove(rewardId)
    
    exploreInfo = {}
    exploreInfo['reward'] = list2rewardstr(rewardList)
    updateExploreInfo(playerId,exploreInfo)
    
    #随机获得奖励
    rewardProp = random.choice(EXPLORE_REWARD_CONFIG[int(rewardId)])
    
    propDict = db_tool.getAllProp(playerId)
    db_tool.__addPropItem(propDict,rewardProp,1)
    db_tool.saveAllProp(playerId,propDict)
    
    returnVal = getTeamUpInfo(playerId)
    #前台展现使用
    returnVal['definitionId'] = rewardProp
    returnVal['num'] = 1
    returnVal['bag'] = propDict
    #任务判断使用
    returnVal['floor'] = returnVal['teamInfo']['floor']
    returnVal['reward_step'] = step
    
    #add eventlog
    eventInfo = {'snsName':personInfo['sns_name']}
    eventInfo['definitionId'] = rewardProp
    eventInfo['num'] = 1
    eventInfo['step'] = step
    addExploreEventLog(personInfo['leader'],5,eventInfo)
    
    #完成所有阶段游戏并领取奖励后，退出游戏
    if not rewardList and returnVal['teamInfo']['step'] == 4:
        quitTeamUp(playerId)
        returnVal['teamInfo'] = None
        
        #add eventlog
        eventInfo = {'snsName':personInfo['sns_name']}
        addExploreEventLog(personInfo['leader'],6,eventInfo)
    
    
    return returnVal


def rewardstr2list(rewardStr):
    rewardslist = []
    if len(rewardStr)>0:
        rewardslist = rewardStr.split('|')
    return rewardslist

def list2rewardstr(rewardslist):
    if(not rewardslist):
        rewardslist = list()
    return '|'.join(rewardslist)
    

#添加探索信息
@getOneDBConn
def addExploreInfo(db,conn,exploreInfo):
    fields = ','.join(exploreInfo.keys())
    values = tuple(exploreInfo.values())
    buildstr = ','.join(['%s']*len(exploreInfo))
    sql = "insert into explore (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()

#添加团队信息
@getOneDBConn
def addExploreTeamInfo(db,conn,teamInfo):
    fields = ','.join(teamInfo.keys())
    values = tuple(teamInfo.values())
    buildstr = ','.join(['%s']*len(teamInfo))
    sql = "insert into explore_team (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()


#更新玩家探险信息
@getOneDBConn
def updateExploreInfo(db,conn,playerId,exploreInfo):
    fields = exploreInfo.keys()
    values = exploreInfo.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE explore SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()


#悲观锁解决并发修改团队信息问题
@getOneDBConn
def updateExploreTeamScore(db,conn,leaderId,score):
    teamInfo = lockExploreTeamInfo(db,conn,leaderId)
    
    totalScore = teamInfo['total_score'] + score
    floor = teamInfo['floor']
    step = teamInfo['step']
    
    enterNextStep = False
    
    if EXPLORE_CONFIG[floor].has_key(step) and totalScore >= EXPLORE_CONFIG[floor][step]['score']:
        step += 1
        enterNextStep = True
        
        teamInfo['total_score'] = totalScore
        teamInfo['step'] = step
        
    db.execute("UPDATE explore_team SET total_score=%s,step=%s WHERE leader_id=%s",(totalScore,step,leaderId))
    conn.commit()
    
    return enterNextStep,teamInfo

    
#获取玩家探险个人信息
@getOneDBConn
def getExploreInfo(db,conn,playerId):
    db.execute("SELECT * FROM explore WHERE player_id = %s",(playerId,))
    teamInfo = db.fetchone()
    if teamInfo:
        teamInfo = dict(teamInfo)
    return teamInfo


#获取玩家探险团队信息
@getOneDBConn
def getExploreTeamInfo(db,conn,leaderId):
    db.execute("SELECT * FROM explore_team WHERE leader_id = %s",(leaderId,))
    teamInfo = db.fetchone()
    if teamInfo:
        teamInfo = dict(teamInfo)
    return teamInfo

#lock and get
def lockExploreTeamInfo(db,conn,leaderId):
    db.execute("SELECT * FROM explore_team WHERE leader_id = %s for update",(leaderId,))
    teamInfo = db.fetchone()
    if teamInfo:
        teamInfo = dict(teamInfo)
    return teamInfo


#获取团队成员信息个数
@getOneDBConn
def getMemberCounts(db,conn,leaderId):
    db.execute("SELECT count(*) FROM explore WHERE leader = %s",(leaderId,))
    members = db.fetchone()
    #return members[0]
    return members.values()[0]
    

#获取团队及成员信息
@getOneDBConn
def getExploreMembers(db,conn,playerId):
    #团队成员信息
    members = []
    #团队信息
    teamInfo = None
    
    exploreInfo = getExploreInfo(playerId)
    leaderId = exploreInfo['leader']
    
    teamInfo = getExploreTeamInfo(leaderId)
    
    db.execute("SELECT * FROM explore WHERE leader = %s",(leaderId,))
    membersInfo = db.fetchall()
    
    if membersInfo:
        for member in membersInfo:
            adict = {}
            adict['sns_name'] = member['sns_name']
            adict['sns_pic'] = member['sns_pic']
            adict['score'] = member['score']
            adict['player_id'] = member['player_id']
            adict['reward'] = member['reward']
            members.append(adict)
    return teamInfo,members
    
@getOneDBConn
def delExploreInfo(db,conn,playerId):
    db.execute("delete from explore WHERE player_id=%s",(playerId,))
    conn.commit()
    
@getOneDBConn
def delExploreTeamInfo(db,conn,leaderId):
    db.execute("delete from explore_team WHERE leader_id=%s",(leaderId,))
    conn.commit()

#为防止出现不一致的情况，放到一个事务中删除
@getOneDBConn
def delExploreAndTeamInfo(db,conn,playerId):
    db.execute("delete from explore WHERE player_id=%s",(playerId,))
    db.execute("delete from explore_team WHERE leader_id=%s",(playerId,))
    db.execute("delete from explore_event_log WHERE leader_id=%s",(playerId,))
    conn.commit()


#换队长
@getOneDBConn
def updateExploreLeader(db,conn,olderLeader,newLeader):

    teamInfo = getExploreTeamInfo(olderLeader)
    
    newTeam = teamInfo
    newTeam['leader_id'] = newLeader
    addExploreTeamInfo(newTeam)
    
    delExploreTeamInfo(olderLeader)

    db.execute("UPDATE explore SET leader=%s WHERE leader=%s",(newLeader,olderLeader))
    db.execute("UPDATE explore_event_log SET leader_id=%s WHERE leader_id=%s",(newLeader,olderLeader))
    conn.commit()


#添加团队日志信息
@getOneDBConn
def saveExploreEventLog(db,conn,eventInfo):
    fields = ','.join(eventInfo.keys())
    values = tuple(eventInfo.values())
    buildstr = ','.join(['%s']*len(eventInfo))
    sql = "insert into explore_event_log (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()


#获得团队日志信息
@getOneDBConn
def getExploreEventLog(db,conn,leaderId):
    db.execute("SELECT * FROM explore_event_log WHERE leader_id = %s order by create_time desc limit 30",(leaderId,))
    eventInfo = []
    try:
        logs = db.fetchall()
    except:
        return eventInfo
    for log in logs:
        info = db_tool.__auctionStringToDict(log['info'])
        temp = {}
        temp['time'] = log['create_time']
        temp['type'] = log['type']
        temp['info'] = info
        temp['status'] = log['status']
        eventInfo.append(temp)
    
    return eventInfo


@getOneDBConn
def updateExploreEventStatus(db,conn,playerId):
    db.execute("UPDATE explore_event_log SET status=1 WHERE leader_id=%s",(playerId,))
    conn.commit()

@getOneDBConn
def getExploreEventCounts(db,conn,playerId):
    db.execute("select count(id) from explore_event_log WHERE leader_id=%s and status=0",(playerId,))
    num = db.fetchone()
    #return num[0]
    return num.values()[0]

#添加组队日志
'''
1.创建
2.加入
3.退出
4.踢出
5.领取阶段奖励
6.完成探索任务
7.完成阶段游戏
'''
def addExploreEventLog(leader,type,info):
    time_now = int(time.time())
    eventInfo = {}
    eventInfo['leader_id'] = leader
    eventInfo['type'] = type
    eventInfo['create_time'] = time_now
    eventInfo['info'] = db_tool.__dictToString(info)
    eventInfo['status'] = 0
    saveExploreEventLog(eventInfo)