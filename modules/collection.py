#-*- coding=utf8 -*-
from settings import *
from config.drawing_config import *
from config.collection_config import *
import modules.db_tool as db_tool
import modules.item as item_module
import random


def getCollection(playerId):
    collection=db_tool.__getPlayerCollection(playerId)
    if not collection['status']:
        return []
    returnVal = collection['status'].split('|')
    return returnVal

#残片炼化
def refining(playerId,definitionId,definitionNum):
    definitionId = str(definitionId)
    itemStar = definitionId[-1]
    #根据星级获得不同的炼化石
    if itemStar == '0':
    	refining_stone = 10060
    elif itemStar == '1':
    	refining_stone = 10061
    elif itemStar == '2':
    	refining_stone = 10062
    
    propDict = db_tool.getAllProp(playerId)
    
    if not propDict.has_key(definitionId) or propDict[definitionId] < definitionNum:
    	return {'status':0,'msg':'refining failed... no (or not enough) definitionId '+definitionId}
    
    db_tool.__subtractPropItem(propDict,definitionId,definitionNum)
    db_tool.__addPropItem(propDict,refining_stone,definitionNum)
    db_tool.saveAllProp(playerId,propDict)
    
    return {'status':1,'bag':propDict,'definitionId':refining_stone,'number':definitionNum}
    
#残片合成
def mix(playerId,definitionId):
    
    player = db_tool.__getPlayerById(playerId)
    propDict = db_tool.getAllProp(playerId)
    
    if not propDict.has_key(str(definitionId)):
    	return {'status':0,'msg':'no definitionId'+str(definitionId)}
    
    drawing = propDict[str(definitionId)]
    if not drawing or drawing <= 0:
        return {'status':0,'type_error':13,'msg':' '}
    mix_prop = DRAWING_CONFIG[definitionId]['mix']
    
    item_id = item_module.getMixIdByDrawId(definitionId)
    
    #合成新物种加经验
    collectionStr = db_tool.__getPlayerCollection(player['id'])['status']
    collection = __collectionToList(collectionStr)
    if str(item_id) in collection:
        exp = 0
    else:
        exp = DRAWING_CONFIG[definitionId]['exp']
    player['exp'] += exp
    
    #验证合成需要的材料
    if not __checkNum(player,mix_prop,propDict):
        return {'status':0,'type_error':23,'msg':'材料数量不够'}
    
    for each in mix_prop:
    	if each['type'] == 2:
    	    player['gb']-=each['value']
    	else:
    	    db_tool.__subtractPropItem(propDict,each['type'],each['value'])

    db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'exp':player['exp']})
    db_tool.__addPropItem(propDict,str(item_id),1)
    db_tool.__subtractPropItem(propDict,str(definitionId),1)
    db_tool.saveAllProp(player['id'],propDict)#update db
    __updateCollection(player,item_id)
    #num =  db_tool.getGlobalDefinitionNum(item_id)        
    #num=1
    return {'status':1,'bag':propDict,"item_id":item_id,'add_exp':exp,'player_exp':player['exp'],'player_gb':player['gb']}

#残片分解
def resolve(playerId,definitionId,definitionNum):
    returnVal = {}
    returnVal['items'] = []
    #drawing = db_tool.__selectProp(definitionId,playerId)
    propDict = db_tool.getAllProp(playerId)
    drawing = propDict[str(definitionId)]
    if not drawing or drawing < definitionNum:
        return {'status':0,'msg':'can not find prop id: ['+str(definitionId)+'].'}
        
    resolve_prop = DRAWING_CONFIG[definitionId]['resolve']
    for each in resolve_prop:
        prop_id,number,per = each['type'],each['value'],each['per']
        randNum = random.randint(1,100)
        #有几率获得双倍材料
        if 1 <= randNum <= per:
            number *= 2
        totalNumber = number*definitionNum
        db_tool.__addPropItem(propDict,str(prop_id),totalNumber)
        returnVal['items'].append({'number':totalNumber,'definitionId':prop_id})
    
    db_tool.__subtractPropItem(propDict,str(definitionId),definitionNum)
    db_tool.saveAllProp(playerId,propDict)#update prop db
    returnVal['status'] = 1
    returnVal['bag'] = propDict
    returnVal['definitionId'] = definitionId
    returnVal['number'] = definitionNum
    return returnVal


def __collectionToList(collection):
    collectionList = collection.split('|') 
    return collectionList


def __listToCollection(collectionList):
    collection = "|".join(collectionList)
    return collection

def __collectionListToDict(collection):
    collectionDict = dict()
    collectionList = collection.split('|')
    for each in collectionList:
        theCollection = each.split(':')
        collectionDict[int(theCollection[0])] = int(theCollection[1])
    return collectionDict

def __dictToCollectionList(dict):
    theList = list()
    for key in dict:
        theList.append(str(key)+":"+str(dict[key]))
    collection = '|'.join(theList)
    return collection


def finishCollection(playerId,definitionId):
    player = db_tool.__getPlayerById(playerId)
    
    #
    collectionListStr = db_tool.__getPlayerCollectionList(player['id'])['status']
    if not collectionListStr:
        collectionListList = []
    else:
        collectionListList = __collectionToList(collectionListStr)
    if str(definitionId) in collectionListList:
        return {'status':0,'msg':''}

    collectionStr = db_tool.__getPlayerCollection(player['id'])['status']
    #
    if not collectionStr:
        collectionList = []
    else:
        collectionList = __collectionToList(collectionStr)
    
    content = COLLECTION_CONFIG[definitionId]['content']
    for each in content:
        if str(each) not in collectionList:
            return {'status':0}
            
    award = COLLECTION_CONFIG[definitionId]['award']
    if award['gb']:
        player['gb'] += award['gb']
    if award['exp']:
        player['exp'] += award['exp']
    db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'exp':player['exp']})

    collectionListList.append(str(definitionId))
    strCollection = __listToCollection(collectionListList)
    db_tool.updateCollectionList(strCollection,player['id'])
    
    prop = db_tool.getAllProp(playerId)
    if award['definitionId']:
       db_tool.__addPropItem(prop,award['definitionId'],1)
    db_tool.saveAllProp(playerId,prop)
    return {'status':1,'bag':prop,'player':player}


def __checkNum(player,mix_prop,propDict):
    for each in mix_prop:
        if each['type'] == 2:
            #gb不足
            if player['gb'] - each['value'] < 0:
                return False
        else:
            prop_id=each['type']
            #材料不足
            if not propDict.has_key(str(prop_id)):
                return False
            #材料数不足
            if propDict[str(prop_id)] - each['value'] < 0:
                return False
    return True


def __updateCollection(player,definitionId):
    collection = db_tool.__getPlayerCollection(player['id'])
    status = collection['status']
    
    definitionId = str(definitionId)
    statusList = []
    if status:
        statusList = status.split("|")
    
    if definitionId not in statusList:
        statusList.append(str(definitionId))
        status = '|'.join(statusList)
        db_tool.updateCollection(status,player['id'])
    