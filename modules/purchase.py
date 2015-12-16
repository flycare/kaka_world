#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.memory_cache as memory_cache

#发起求购信息
@getOneDBConn
def launchPurchase(db,conn,playerId,parm):
    prop_id = parm['definitionId']
    price = parm['price']
    number = parm['number']
    
    player = db_tool.__getPlayerById(playerId)
    
    num = getPurchaseCounts(playerId)
    time_now = int(time.time())
    if player['vip'] > time_now:
        if num >= 5:
            return {'status':0,'error_type':1,'msg':'求购5格已满,'}
    else:
        if num >= 3:
            return {'status':0,'error_type':1,'msg':'求购3格已满'}
            
    purchaseInfo = {}
    purchaseInfo['user_id'] = playerId
    purchaseInfo['price'] = price
    purchaseInfo['prop_id'] = prop_id
    purchaseInfo['number'] = number
    savePurchaseInfo(purchaseInfo)
    
    return {'status':1,'purchase':parm}


#取消求购
def cancelPurchase(playerId,purchaseId):
    purchaseItem = getPurchaseItem(purchaseId)
    
    if not purchaseItem or purchaseItem['user_id'] != playerId:
        bag = db_tool.getAllProp(playerId);
        player = db_tool.__getPlayerById(playerId)
        return {'status':0,'bag':bag,'gb':player['gb'],'error_type':1,'purchaseId':purchaseId,'msg':'cancelPurchase error by purchaseId'+str(purchaseId)}
    
    delPurchaseItem(purchaseId)
    
    purchaseList = getPurchaseList(playerId)
    
    return {'status':1,'purchaseId':purchaseId,'purchase_transaction':purchaseList}


#卖给求购者
@getOneDBConn
def purchaseResponse(db,conn,buyer,seller,sellerName,purchaseId):
    sellerBag = db_tool.getAllProp(seller);
    
    buyerPlayer = db_tool.__getPlayerById(buyer)
    sellerPlayer = db_tool.__getPlayerById(seller)

    purchaseItem = lockPurchaseItem(db,conn,purchaseId)
    
    if not purchaseItem:
        return {'status':0,'error_type':1,'purchaseId':purchaseId,'msg':'purchaseResponse: no purchase'}
    
    price = purchaseItem['price']
    number = purchaseItem['number']
    prop_id = str(purchaseItem['prop_id'])
    
    if buyerPlayer['gb'] < price:
        return {'status':0,'error_type':2,'purchaseId':purchaseId,'msg':'purchaseResponse: not enouth gb'}
    
    if not sellerBag.has_key(prop_id) or sellerBag[prop_id] < number:
        return {'status':0,'error_type':3,'purchaseId':purchaseId,'msg':'purchaseResponse: not enouth prop'}
    
    #计算税
    tax_rate=1/0.05
    tax=int((price+tax_rate-1)/tax_rate)
    
    #更新卖方背包及GB
    db_tool.__subtractPropItem(sellerBag,prop_id,number)
    db_tool.saveAllProp(seller,sellerBag)
    
    sellerPlayer['gb'] += price-tax
    db_tool.__updatePlayer(seller,{'gb':sellerPlayer['gb']})
    
    #更新买方背包及GB
    buyerBag = db_tool.getAllProp(buyer);
    db_tool.__addPropItem(buyerBag,prop_id,number)
    db_tool.saveAllProp(buyer,buyerBag)
    
    buyerPlayer['gb'] -= price
    db_tool.__updatePlayer(buyer,{'gb':buyerPlayer['gb']})
    
    #删除求购单数据
    delLockPurchaseItem(db,conn,purchaseId)
    
    #添加交易日志
    time_now = int(time.time())
    
    info = {}
    info['player_id'] = seller
    info['price'] = price
    info['number'] = number
    info['prop_id'] = prop_id
    info['buyer'] = sellerName
    
    eventLog = {}
    eventLog['user_id'] = buyer
    eventLog['type'] = 1
    eventLog['info'] = dict2str(info)
    eventLog['create_time'] = time_now
    savePurchaseEvent(eventLog)
    
    return {'status':1,'purchaseId':purchaseId,'bag':sellerBag,'gb':sellerPlayer['gb']}
    
#获取求购数量
@getOneDBConn
def getPurchaseCounts(db,conn,playerId):
    db.execute("select count(*) from purchase where user_id=%s",(playerId,))
    num = db.fetchone()
    return num.values()[0]


#具体求购信息
@getOneDBConn
def getPurchaseItem(db,conn,purchaseId):
    db.execute("SELECT * FROM purchase WHERE id = %s",(purchaseId,))
    purchaseItem = db.fetchone()
    return purchaseItem

#lock and get
def lockPurchaseItem(db,conn,purchaseId):
    db.execute("SELECT * FROM purchase WHERE id = %s for update",(purchaseId,))
    purchaseItem = db.fetchone()
    return purchaseItem
    
#获取求购信息列表
@getOneDBConn
def getPurchaseList(db,conn,playerId):
    db.execute("SELECT * FROM purchase WHERE user_id = %s",(playerId,))
    purchaseList = db.fetchall()
    if purchaseList:
        returnVal = []
        for item in purchaseList:
           returnVal.append({'id':item['id'],'price':item['price'],'number':item['number'],'definitionId':item['prop_id']})
        return returnVal
    else:
        return []
    
    
#添加求购信息
@getOneDBConn
def savePurchaseInfo(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into purchase (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()

#删除
@getOneDBConn
def delPurchaseItem(db,conn,purchaseId):
    db.execute("DELETE FROM purchase WHERE id = %s",(purchaseId,))
    conn.commit()

def delLockPurchaseItem(db,conn,purchaseId):
    db.execute("DELETE FROM purchase WHERE id = %s",(purchaseId,))
    conn.commit()
    
#添加求购信息日志
@getOneDBConn
def savePurchaseEvent(db,conn,info):
    fields = ','.join(info.keys())
    values = tuple(info.values())
    buildstr = ','.join(['%s']*len(info))
    sql = "insert into purchase_event_log (%s) values (%s)" % (fields,buildstr)
    
    db.execute(sql,values)
    conn.commit()
    
    #clear cache
    playerId = info['user_id']
    memory_cache.setPurchaseEventLogCache(playerId,None)

#获取求购信息日志
@getOneDBConn
def getPurchaseEvent(db,conn,playerId):
    #先从cache中获取
    info = memory_cache.getPurchaseEventLogCache(playerId)
    if info:
        return info
    
    db.execute("SELECT * FROM purchase_event_log WHERE type = 1 AND user_id = %s order by create_time desc limit 16",(playerId,))
    info = []
    try:
        logs = db.fetchall()
    except:
        return info
    for log in logs:
        temp = str2dict(log['info'])
        temp['time'] = log['create_time']
        info.append(temp)
    
    #set cache
    memory_cache.setPurchaseEventLogCache(playerId,info)
    
    return info

def str2dict(astr):
    adict = dict()
    if len(astr)>0:
        list = astr.split('|')
        for each in list:
            obj = each.split(':')
            adict[str(obj[0])] = str(obj[1])
    return adict

def dict2str(adict):
    alist = list()
    for key in adict:
        alist.append(str(key)+":"+str(adict[key]))
    astr = '|'.join(alist)
    return astr