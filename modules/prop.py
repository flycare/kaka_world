#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.item_config import *
from config.sell_config import *
from config.bag_config import *
from config.box_config import *

import time
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.player as player_module
import modules.random_tool as random_tool

def usePropInBag(playerId,prop_id):
    propDict = db_tool.getAllProp(playerId)
    prop_id=str(prop_id)
    
    if propDict.has_key(prop_id) and propDict[prop_id] >0 :
        player = db_tool.__getPlayerById(playerId)
        player = player_module.__updateEnergy(player)
        
        boxItem = {}
        
        #能量道具
        if prop_id == '2010' or prop_id == '2011' or prop_id == '2012':
            player['energy'] += PROP_CONFIG[int(prop_id)]['num']
            db_tool.__updatePlayer(player['id'],{'energy':player['energy'],'last_energy_time':player['last_energy_time']})
        #VIP道具
        elif prop_id == '2001' or prop_id == '2002' or prop_id == '2003':
            time_now = int(time.time())
            if player['vip'] > time_now:
                player['vip'] += PROP_CONFIG[int(prop_id)]['period']
            else:
                player['vip'] = time_now + PROP_CONFIG[int(prop_id)]['period']
            db_tool.__updatePlayer(player['id'],{'vip':player['vip']})
        #材料包
        elif prop_id == '3001' or prop_id == '3002' or prop_id == '3003':
            props = PROP_CONFIG[int(prop_id)]['items']
            for item in props:
                db_tool.__addPropItem(propDict,item['type'],item['num'])
        #神秘箱子
        elif prop_id == '4000' or prop_id == '4010':
            random_table_key = 'magic_box_random_table_'+prop_id
            boxItem = random_tool.getRandomItem(random_table_key,MAGIC_BOX[int(prop_id)])
            db_tool.__addPropItem(propDict,boxItem['type'],boxItem['num'])
        else:
            return {'status':0,'msg':'未配置效果物品 ['+str(prop_id)+'].'}
            
            
        propDict[prop_id]-=1
        db_tool.saveAllProp(player['id'],propDict)
        
        #有箱子信息
        if boxItem:
            return {'status':1,'player':player,'bag':propDict,'time_now':int(time.time()),'prop_id':prop_id,'box_item_type':boxItem['type'],'box_item_num':boxItem['num']}
        else:
            return {'status':1,'player':player,'bag':propDict,'time_now':int(time.time()),'prop_id':prop_id}
    else:
        return {'status':0,'msg':'Can not find ['+str(prop_id)+'] in bag.'}


#将合成物从背包放入界面
def decorateInBag(playerId,param):
    habitatId = param['map_index']
    definitionId = str(param['definitionId'])
    propDict= db_tool.getAllProp(playerId)
    if propDict.has_key(definitionId) and propDict[definitionId]>0:
        propDict[definitionId]=propDict[definitionId]-1
        addItems = db_tool.addMapItem(playerId,habitatId,param)
        db_tool.saveAllProp(playerId,propDict)
        return {'status':1,'add':addItems}
    else:
        return {'status':0,'msg':'no definitionId in bag'}


#将装饰物从商店放入界面
def decorateInShop(playerId,param):
    habitatId = param['map_index']
    #买装饰物需要花费的钱
    cost_money=__getCostMoney(param)
    player = db_tool.__getPlayerById(playerId)
    #比较
    if (player['kb']<cost_money['kb']):
        return {'status':0,'msg':'not enough KB'}
    elif (player['gb']<cost_money['gb']):
        return {'status':0,'msg':'not enough GB'}
    #扣除
    player['gb'] -=cost_money['gb']
    player['kb'] -=cost_money['kb']
    player['exp'] += cost_money['exp']
    #添加
    addItems = db_tool.addMapItem(playerId,habitatId,param)
    db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'kb':player['kb'],'exp':player['exp']})
    
    #add cost log
    if cost_money['kb']>0:
        player_module.addCostLog(player['id'],cost_money['kb'],'decorateInShop')
            
    return {'status':1,'buy':addItems,'player':player}


#将一组装饰物从商店放入界面
def decorateGroupInShop(playerId,param):
    habitatId = param['map_index']
    groupId = param['groupId']
    groupItems = param['group']
    
    item = {'definitionId':groupId}
    
    #买装饰物需要花费的钱
    cost_money=__getCostMoney(item)
    player = db_tool.__getPlayerById(playerId)
    #比较
    if (player['kb']<cost_money['kb']):
        return {'status':0,'msg':'not enough KB'}
    elif (player['gb']<cost_money['gb']):
        return {'status':0,'msg':'not enough GB'}
    #扣除
    player['gb'] -=cost_money['gb']
    player['kb'] -=cost_money['kb']
    player['exp'] += cost_money['exp']
    #添加
    addItems = db_tool.addMapItemList(playerId,habitatId,groupItems)
    db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'kb':player['kb'],'exp':player['exp']})
    
    #add cost log
    if cost_money['kb']>0:
        player_module.addCostLog(player['id'],cost_money['kb'],'decorateGroupInShop')
    
    return {'status':1,'group':addItems,'player':player}


#买东西花费的钱及奖励的经验
def __getCostMoney(item):
    returnVal={}
    returnVal['kb']=0
    returnVal['gb']=0
    returnVal['exp']=0
    definition = ITEM_CONFIG[item['definitionId']]
    if definition.has_key('KB') and definition['KB'] >0:
        returnVal['kb']+=definition['KB']
    elif definition.has_key('GB') and definition['GB'] >0:
        returnVal['gb']+=definition['GB']
    returnVal['exp'] += definition['exp']
    return returnVal


#从背包卖出(残片)
def sellProps(playerId,param):
    player = db_tool.__getPlayerById(playerId)
    prop_id = str(param['definitionId'])
    prop_num= param['number']
    
    propDict = db_tool.getAllProp(playerId)
    
    if propDict.has_key(prop_id) and propDict[prop_id] >= prop_num:
        propDict[prop_id]-=prop_num
        
        itemType = prop_id[0]
        itemStar = prop_id[-1]
        #是否是残片
        if (itemType != '1'):
            return {'status':0,'msg':'err definitionIds'}
        #卖出的金额
        gold = SELL_UNMIX_CONFIG[int(itemStar)+1]*prop_num
        
        player['gb'] += gold
        db_tool.__updatePlayer(player['id'],{'gb':player['gb']})
        db_tool.saveAllProp(player['id'],propDict)
        
        return {'status':1,'player':player,'sell_info':param}
    else:
        return {'status':0,'msg':'not enough definitionIds'}


#从背包卖出(合成物)
def sellPropInBag(playerId,param):
    player = db_tool.__getPlayerById(playerId)
    prop_id = str(param['definitionId'])
    prop_num= param['number']
    
    propDict = db_tool.getAllProp(playerId)
    
    if propDict.has_key(prop_id) and propDict[prop_id] >= prop_num:
        propDict[prop_id]-=prop_num
        
        itemType = prop_id[0]
        itemStar = prop_id[-1]
        if(itemType == '2'):
            gold = ITEM_CONFIG[int(prop_id)]['GB']/10*prop_num
        elif(itemType == '3' or itemType == '4' or itemType == '5'):
            gold = SELL_CONFIG[int(itemType)][int(itemStar)+1]*prop_num
        
        player['gb'] += gold
        db_tool.__updatePlayer(player['id'],{'gb':player['gb']})
        db_tool.saveAllProp(player['id'],propDict)
        
        return {'status':1,'player':player,'sell_info':param}
    else:
        return {'status':0,'msg':'not enough definitionIds'}


#从商店买
def buyPropInShop(playerId,params):
    player = db_tool.__getPlayerById(playerId)
    bool = True 
    for each in params :
        prop_id = each['definitionId']
        number = each['number']
        #
        if str(prop_id) == '2':
            pass
        elif PROP_CONFIG[prop_id]['KB']>0 :
            #logging.debug(each)
            money=PROP_CONFIG[prop_id]['KB']*number
            player['kb']-=money
            if player['kb'] < 0:
                bool=False
            else:
                #add cost log
                player_module.addCostLog(playerId,money,'buyPropInShop')
                
        elif PROP_CONFIG[prop_id]['GB']>0:
            money=PROP_CONFIG[prop_id]['GB']*number
            player['gb']-=money
            if player['gb'] < 0:
                bool=False
        else:
            return {'status':0,'msg':'There is a error in PROP_CONFIG'}
    
    if bool:
        db_tool.__updatePlayer(player['id'],{'gb':player['gb'],'kb':player['kb']})
        propDict = db_tool.getAllProp(playerId)
        for each in params :
            db_tool.__addPropItem(propDict,each['definitionId'],each['number'])#Not update db
        db_tool.saveAllProp(player['id'],propDict)#update db
        returnVal = {}
        returnVal['status'] = 1
        returnVal['player'] = player
        returnVal['bag'] = propDict
        returnVal['items'] = params
        return returnVal
    else :
        return {'status':0,'msg':'Not enough money.'}


#成为VIP
def becomeVIP(playerId,prop_id):
    player = db_tool.__getPlayerById(playerId)
    bool=1
    time_now = int(time.time())
    if(PROP_CONFIG[prop_id]['KB']>0):
        player['kb'] -= PROP_CONFIG[prop_id]['KB']
        if player['kb'] < 0:
            bool=0
        else:
            #add cost log
            player_module.addCostLog(playerId,PROP_CONFIG[prop_id]['KB'],'becomeVIP')
            
    elif (PROP_CONFIG[prop_id]['GB']>0):
        player['gb'] -= PROP_CONFIG[prop_id]['GB']
        if player['gb'] < 0:
            bool=0
    if(bool):
        if player['vip'] > time_now:
            player['vip'] += PROP_CONFIG[prop_id]['period']
        else:
            player['vip'] = time_now + PROP_CONFIG[prop_id]['period']
            
        db_tool.__updatePlayer(player['id'],{'vip':player['vip'],'kb':player['kb'],'gb':player['gb']})
        return {'status':1,'vip':player['vip'],'kb':player['kb']}
    else:
        return {'status':0,'msg':'Not enough money.'}

#获得背包容量
@getOneDBConn
def getBagCapacity(db,conn,playerId):
    '''
    db.execute("SELECT * FROM prop WHERE user_id = %s",(playerId,))
    propInfo = db.fetchone()
    return propInfo['capacity']
    '''
    db.execute("SELECT capacity FROM prop WHERE user_id = %s",(playerId,))
    propInfo = db.fetchone()
    return propInfo.values()[0]

#扩充背包容量
@getOneDBConn
def expandBagCapacity(db,conn,playerId,expandType):
    
    currentCapacity = getBagCapacity(playerId)
    
    #下次的扩容数
    nextCapacity = currentCapacity+BAG_INCREMENT_CONFIG['increment']

    if BAG_CONFIG.has_key(nextCapacity) and BAG_CONFIG[nextCapacity].has_key(expandType):
        player = db_tool.__getPlayerById(playerId)
        
        #验证扩充需要的gb or kb
        if player[expandType] < BAG_CONFIG[nextCapacity][expandType]:
            return {'status':0,'msg':'not enough '+expandType}
        
        player[expandType] = player[expandType] - BAG_CONFIG[nextCapacity][expandType]
        
        db.execute("UPDATE prop set capacity = %s WHERE user_id = %s",(nextCapacity,playerId))
        db_tool.__updatePlayer(playerId,{expandType:player[expandType]})
        conn.commit()
        
        return {'status':1,'player':player,'bagMax':nextCapacity}
    else:
        return {'status':0,'msg':'BAG_CONFIG error key : '+nextCapacity}