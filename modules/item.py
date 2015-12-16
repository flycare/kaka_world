#-*- coding=utf8 -*-
from settings import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
from config.item_config import *
from config.sell_config import *
from config.building_config import *
import player as player_module
import modules.life_tree as life_tree
import modules.produce as produce_module

#根据栖息地ID获取地图信息
def getMapsInfo(playerId,habitatId):
    maps = db_tool.getMapsbyPlayerId(playerId,habitatId)
    return {'status':1,'map_index':habitatId,'map':maps}
    
#更新界面Item信息
def decorativeScene(serverInfo,param):
    playerId = serverInfo['playerId']
    habitatId = param['map_index']
    
    player = db_tool.__getPlayerById(playerId)
    maps=db_tool.getMapsbyPlayerId(playerId,habitatId)
    propDict= db_tool.getAllProp(playerId)
    
    if not __checkItems(param['sell'],maps):
        return {'status':0,'msg':'sell item is not in map'}
    if not __checkItems(param['move'],maps):
        return {'status':0,'msg':'move item is not in map'}
    if not __checkItems(param['back'],maps):
        return {'status':0,'msg':'back item is not in map'}
    
    moveItems,sellItems,backItems,propDict=updateMapItems(playerId,habitatId,param,propDict)
    #卖出获得的钱
    income_money = __getSellMoney(param['sell'])
    player['gb']=income_money+player['gb']
    db_tool.__updatePlayer(playerId,{'gb':player['gb']})
    
    returnVal = {'status':1}
    returnVal['move']=moveItems
    returnVal['back']=backItems
    returnVal['sell']=sellItems
    returnVal['playerBag'] = propDict
    returnVal['player']=player
    return returnVal


#更新地图信息
def updateMapItems(playerId,habitatId,param,propDict):
    #删除界面上的Item
    moveItems = db_tool.updateMapItemsXY(playerId,habitatId,param['move'])
    sellItems = db_tool.delMapItems(playerId,habitatId,param['sell'])
    backItems = db_tool.delMapItems(playerId,habitatId,param['back'])
    
    #更新背包
    for item in backItems:
        db_tool.__addPropItem(propDict,item['definitionId'],1)
    db_tool.saveAllProp(playerId,propDict)
        
    return moveItems,sellItems,backItems,propDict

def __checkItems(itmes,maps):
    for item in itmes:
        if not (__checkItemInMaps(item,maps)):
            return False
    return True


def __checkItemInMaps(target,maps):
    for item in maps:
        if(item['id']==target['id']):
            return True
    return False


def __checkItemsInBags(items,bags):
    for target in items:
        prop_id=target['definitionId']
        prop_num=1
        if target.has_key('number'):
            prop_num=target['number']
        
        if bags.has_key(str(prop_id)):
            bags[str(prop_id)]-=prop_num
            if bags[str(prop_id)]<0:
                return False
            
    return True

#卖东西获得的钱
def __getSellMoney(items):
    gb=0
    for item in items:
        #gold = 10*(item['definitionId']%100+1)
        definitionId = str(item['definitionId'])
        number = 1
        if (item.has_key('number')):
            number = item['number']
        
        #根据definitionid判断类型和星级
        itemType = definitionId[0]
        itemStar = definitionId[-1]
        #装饰物
        if(itemType == '2'):
            definition = ITEM_CONFIG[int(definitionId)]
            if definition.has_key('KB') and definition['KB']>0:
                gold = definition['KB']*10*number
            elif definition.has_key('GB') and definition['GB'] >0:
                gold = definition['GB']/10*number
        #动物、植物、建筑
        elif(itemType == '3' or itemType == '4' or itemType == '5'):
            gold = SELL_CONFIG[int(itemType)][int(itemStar)+1]*number
        gb+=gold
    return gb


#升级研究所
def buildingLevelUp(playerId,type):
    
    player = db_tool.__getPlayerById(playerId)
    
    produceInfo = produce_module.getProduceById(playerId)
    nextLevel = produceInfo['level']+1
    produce_module.updateProduceLevel(playerId,nextLevel)
    
    #使用GB升级
    if(type==1):
        price = PRODUCE_COFIG[nextLevel]['GB']
        if player['gb'] < price:
            return {'status':0,'msg':'not enough GB'}
        elif player['level'] < PRODUCE_COFIG[nextLevel]['levelLimit']:
            return {'status':0,'msg':'not enough Level'}
        else :
            player['gb']-=price
            db_tool.__updatePlayer(playerId,{'gb':player['gb']})
    
    #使用KB升级
    else :
        price = PRODUCE_COFIG[nextLevel]['KB']
        if player['kb'] < price:
           return {'status':0,'msg':'not enough KB'}
        else:
            player['kb']-=price
            db_tool.__updatePlayer(playerId,{'kb':player['kb']})
            
            #add cost log
            player_module.addCostLog(player['id'],price,'buildingLevelUp')
        
    returnVal = {}
    returnVal['status'] = 1  
    returnVal['level'] = nextLevel
    returnVal['gb'] = player['gb']
    returnVal['kb'] = player['kb']
    returnVal['player'] = player
    return returnVal


#修改描述
def updateDetail(playerId,id,item_detail):
    item = db_tool.__getItem(playerId,id)
    if item and item['user_id'] == playerId:
        db_tool.__updateItemDetail(playerId,id,item_detail)
        return {'status':1,'id':id,'detail':item_detail}
    else:
        return {'status':0,'msg':'Can not find the item'}


#升级栖息地
def habitatLevelUp(playerId,infos):
    habitatId = infos['habitat_id']
    type = infos['money_type']
    
    habitatInfo = getHabitatInfo(playerId)
    levelInfo = str2dict(habitatInfo['info'])
    
    if not levelInfo.has_key(str(habitatId)):
        return {'status':0,'msg':'err habitatId'}
    
    nextLevel = levelInfo[str(habitatId)]+1
    limitInfo = HABITAT_CONFIG[habitatId][nextLevel]
    player = db_tool.__getPlayerById(playerId)
    
    #使用GB升级
    if(type==1):
        price = limitInfo['GB']
        if player['gb'] < price:
            return {'status':0,'msg':'not enough GB'}
        elif player['level'] < limitInfo['levelLimit']:
            return {'status':0,'msg':'not enough Level'}
        else :
            player['gb']-=price
            db_tool.__updatePlayer(playerId,{'gb':player['gb']})
    
    #使用KB升级
    else :
        price = limitInfo['KB']
        if player['kb'] < price:
           return {'status':0,'msg':'not enough KB'}
        else:
            player['kb']-=price
            db_tool.__updatePlayer(playerId,{'kb':player['kb']})
            
            #add cost log
            player_module.addCostLog(player['id'],price,'habitatLevelUp')
    
    levelInfo[str(habitatId)] = nextLevel
    updateInfo = {'info':dict2str(levelInfo)}
    updateHabitatInfo(playerId,updateInfo)
    
    return {'status':1,'gb':player['gb'],'kb':player['kb'],'id':habitatId,'level':nextLevel,'habitat':levelInfo}


@getOneDBConn
def getHabitatInfo(db,conn,playerId):
    db.execute("SELECT * FROM habitat WHERE player_id = %s",(playerId,))
    habitatInfo = db.fetchone()
    if not habitatInfo:
        level = {}
        level['1'] = 1
        level['2'] = 0
        level['3'] = 0
        level['4'] = 0
        level['5'] = 0
        level['6'] = 0
        level['7'] = 0
        level['8'] = 0
        level['9'] = 0
        level['10'] = 0
        
        habitatInfo = {}
        habitatInfo['player_id'] = playerId
        habitatInfo['info'] = dict2str(level)
        
        saveHabitatInfo(habitatInfo)
    else:
        habitatInfo = dict(habitatInfo)
    
    return habitatInfo


@getOneDBConn
def saveHabitatInfo(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into habitat (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()


@getOneDBConn
def updateHabitatInfo(db,conn,playerId,info):
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
    sql = "UPDATE habitat SET %s WHERE %s"%(setField,"player_id = %s")
    
    db.execute(sql,setValue)
    conn.commit()
    
    
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


#获得残片ID
def getDrawIdByMixId(mixId):
    drawId = 10000000 + int(mixId)
    return drawId

#获得合成物ID
def getMixIdByDrawId(drawId):
    mixId = int(drawId)%10000000
    return mixId