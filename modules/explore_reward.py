#-*- coding=utf8 -*-
from settings import *
from modules.db_tool import getOneDBConn


#获取奖励信息
@getOneDBConn
def getExploreRewardInfo(db,conn,playerId):
    db.execute("SELECT * FROM explore_reward WHERE player_id = %s",(playerId,))
    rewardInfo = db.fetchone()
    if rewardInfo:
        rewardInfo = dict(rewardInfo)
    return rewardInfo


#添加奖励信息
@getOneDBConn
def saveExploreRewardInfo(db,conn,rewardInfo):
    fields = ','.join(rewardInfo.keys())
    values = tuple(rewardInfo.values())
    buildstr = ','.join(['%s']*len(rewardInfo))
    sql = "insert into explore_reward (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()


#修改奖励信息
@getOneDBConn
def updateExploreRewardInfo(db,conn,playerId,rewardInfo):
    fields = rewardInfo.keys()
    values = rewardInfo.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE explore_reward SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()