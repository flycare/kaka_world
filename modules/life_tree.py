#-*- coding=utf8 -*-
from settings import *

from config.visit_config import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.time_tool as time_tool
import modules.random_tool as random_tool

#获取生命之树信息
def getLifeTreeInfo(playerId):
    lifeTreeInfo = getLifeTreeInfoById(playerId)
    returnVal = {}
    returnVal['info'] = str2dict(lifeTreeInfo['info'])
    returnVal['level'] = lifeTreeInfo['level']
    return returnVal


#生命之树升级
def lifeTreeLevelUp(playerId,mapId):
    lifeTreeInfo = getLifeTreeInfoById(playerId)
    infoDict = str2dict(lifeTreeInfo['info'])
    infoDict[str(mapId)] = 1
    
    updateInfo = {}
    updateInfo['info'] = dict2str(infoDict)
    updateInfo['level'] = lifeTreeInfo['level']+1
    updateLifeTreeInfo(playerId,updateInfo)
    
    #为flash封装成dict
    updateInfo['info'] = infoDict
    return {'status':1,'life_tree':updateInfo}
    

def str2dict(astr):
    adict = dict()
    if len(astr)>0:
        list = astr.split('|')
        for each in list:
            obj = each.split(':')
            adict[str(obj[0])] = int(obj[1])
    return adict

def dict2str(adict):
    alist = list()
    for key in adict:
        alist.append(str(key)+":"+str(adict[key]))
    astr = '|'.join(alist)
    return astr

@getOneDBConn
def getLifeTreeInfoById(db,conn,playerId):
    db.execute("SELECT * FROM life_tree WHERE player_id = %s",(playerId,))
    lifeTreeInfo = db.fetchone()
    if not lifeTreeInfo:
        info = {}
        info['1'] = 0
        info['2'] = 0
        info['3'] = 0
        info['4'] = 0
        info['5'] = 0
        
        lifeTreeInfo = {}
        lifeTreeInfo['player_id'] = playerId
        lifeTreeInfo['info'] = dict2str(info)
        lifeTreeInfo['level'] = 1
        
        saveLifeTreeInfo(lifeTreeInfo)
        
    return lifeTreeInfo

#添加生命之树信息
@getOneDBConn
def saveLifeTreeInfo(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into life_tree (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()


#修改生命之树信息
@getOneDBConn
def updateLifeTreeInfo(db,conn,playerId,info):
    fields = info.keys()
    values = info.values()
    values.append(playerId)
    setValue = ""
    setField = ""
    sql = ""
    for field in fields:
        setField += field+"=%s,"
    setField = setField[:-1]
    setValue = tuple(values)
    sql = "UPDATE life_tree SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()