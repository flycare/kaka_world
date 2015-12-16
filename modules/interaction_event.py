#-*- coding=utf8 -*-
from settings import *

from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool
import modules.explore_team as explore_team
import modules.festival_gift as festival_gift

#获取交互信息
def getEventLogs(playerId):
    
    #礼物信息
    giftlogs = festival_gift.getGiftEventLog(playerId)
    festival_gift.updateGiftEventStatus(playerId)
    
    #组队信息
    exploreInfo = explore_team.getExploreInfo(playerId)
    teamlogs = []
    if exploreInfo:
        leaderId = exploreInfo['leader']
        teamlogs = explore_team.getExploreEventLog(leaderId)
        explore_team.updateExploreEventStatus(playerId)
    
    #交互日志
    otherlogs = getInteractionEventLog(playerId)
    updateInteractionEventStatus(playerId)
    
    return {'status':1,'festivalEvents':giftlogs,'teamEvents':teamlogs,'interactionEvents':otherlogs}


#未读的消息数
def getEventCount(playerId):
    festivalNum = festival_gift.getGiftEventCounts(playerId)
    exploreNum = explore_team.getExploreEventCounts(playerId)
    interactionNum = getInteractionEventCounts(playerId)
    return festivalNum+exploreNum+interactionNum

    
#交互日志
'''
偷搜索队：1
帮好友炼化：2
帮好友研究所提速：3
帮助收获：4
'''
@getOneDBConn
def writeInteractionEventLog(db,conn,log_info,playerId,type):
    time_now = int(time.time())
    log_str = db_tool.__dictToString(log_info)
    db.execute("INSERT INTO interaction_event_log(player_id,info,create_time,type) VALUES(%s,%s,%s,%s)",(playerId,log_str,time_now,type))
    conn.commit()


@getOneDBConn
def getInteractionEventLog(db,conn,playerId):
    db.execute("SELECT * FROM interaction_event_log WHERE player_id = %s order by create_time desc limit 30",(playerId,))
    info = []
    
    try:
        logs = db.fetchall()
    except:
        return info
    
    for log in logs:
        temp = db_tool.__auctionStringToDict(log['info'])
        temp['time'] = log['create_time']
        temp['type'] = log['type']
        temp['status'] = log['status']
        info.append(temp)
    
    return info


@getOneDBConn
def updateInteractionEventStatus(db,conn,playerId):
    db.execute("UPDATE interaction_event_log SET status=1 WHERE player_id=%s",(playerId,))
    conn.commit()

@getOneDBConn
def getInteractionEventCounts(db,conn,playerId):
    db.execute("select count(id) from interaction_event_log WHERE player_id=%s and status=0",(playerId,))
    num = db.fetchone()
    #return num[0]
    return num.values()[0]