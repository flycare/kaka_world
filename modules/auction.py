#-*- coding=utf8 -*-
from settings import *
import time
import sys
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import purchase as purchase
import modules.player as player_module

#获得交易行信息
def getAuction(playerId):
    time_now = int(time.time())
    player = db_tool.__getPlayerById(playerId)
    if not player:
        return {'status':0,'msg':'用户不存在'}
    
    returnVal = {}
    returnVal['status'] = 1
    returnVal['vip'] = 1 if time_now < player['vip'] else 0
    returnVal['uid'] = playerId
    returnVal['transaction'] = __getTransactionList(playerId)
    returnVal['player'] = player
    returnVal['events'] = getAuctionEvent(playerId)
    
    returnVal['purchase_transaction'] = purchase.getPurchaseList(playerId)
    returnVal['purchase_events'] = purchase.getPurchaseEvent(playerId)
    
    return returnVal

#拍卖物品
def Auction(playerId,param):
    player = db_tool.__getPlayerById(playerId)
    returnVal = {}
    time_now = int(time.time())
    
    num = __countTransaction(playerId)
    if player['vip'] > time_now:
        if num >= 5:
            return {'status':0,'error_type':11,'msg':'拍卖行5格已满,'}
    else:
        if num >= 3:
            return {'status':0,'error_type':10,'msg':'拍卖行3格已满'}
            
    prop_id = param['definitionId']
    price = param['price']
    number = param['number']
    propDict=db_tool.getAllProp(playerId)
    prop_count=propDict[str(prop_id)]
    if prop_count >= number:
        __addTransactionItem(playerId,prop_id,number,price)
        db_tool.__subtractPropItem(propDict,prop_id,number)
        db_tool.saveAllProp(playerId,propDict)
        
        returnVal['status'] = 1
        returnVal['bag'] = propDict
        returnVal['transaction'] = __getTransactionList(playerId)
        returnVal['item'] = param
        return returnVal
    else :
        return {'status':0,'msg':'data error'}
    
#取消拍卖
@getOneDBConn
def cancelAuction(db,conn,playerId,transaction_id):
    returnVal = {}
    transaction=__lockTransactionById(db,conn,transaction_id)
    if transaction:
        number = transaction['number']
        prop_id = transaction['prop_id']
        
        #放回背包
        propDict=db_tool.getAllProp(playerId)
        db_tool.__addPropItem(propDict,prop_id,number)
        db_tool.saveAllProp(playerId,propDict)
        #删除记录
        __delLockTransactionItem(db,conn,transaction_id)
        
        returnVal['status'] = 1
        returnVal['transaction'] = __getTransactionList(playerId)
        returnVal['bag'] = propDict
        returnVal['auctionId'] = transaction_id
        return returnVal
    else:
        return {'status':0,'error_type':13,'msg':'Can not find the Transaction by id '+str(transaction_id) }

 
#购买拍卖物品
@getOneDBConn
def buyAuction(db,conn,playerId,transaction_id,buyer_name):
    
    player = db_tool.__getPlayerById(playerId)
    playerId = player['id']
    returnVal = {}
    
    transaction= __lockTransactionById(db,conn,transaction_id)
    if transaction:
        number = transaction['number']
        price = transaction['price']
        seller_id = transaction['user_id']
        
        seller = db_tool.__getPlayerById(seller_id)

        player['gb']-=price
        if(player['gb']>=0):
            tax_rate=1/0.05
            tax=int((price+tax_rate-1)/tax_rate)
            seller_income=price-tax;
            
            #修改卖家gb
            db_tool.__updatePlayer(seller_id,{'gb':seller['gb']+seller_income})
            #修改买家gb及背包
            db_tool.__updatePlayer(playerId,{'gb':player['gb']})
            props = db_tool.getAllProp(playerId)
            db_tool.__addPropItem(props,transaction['prop_id'],number)
            db_tool.saveAllProp(playerId,props)
            #删除记录
            __delLockTransactionItem(db,conn,transaction_id)
            
            log_info = {}
            log_info['player_id'] = playerId
            log_info['price'] = price
            log_info['buyer'] = buyer_name
            log_info['number'] = number
            log_info['prop_id'] = transaction['prop_id']
            auctionEvent(log_info,seller_id)
            
            returnVal['status'] = 1
            returnVal['bag'] = db_tool.getAllProp(playerId)
            returnVal['player'] = player
            returnVal['cost']=price
            returnVal['auctionId'] = transaction_id
            returnVal['auctionStatus'] = player_module.getAuctionStatus(seller_id)
            return returnVal
        else:
            return {'status':0,'error_type':100,'msg':'Not enough money'}
    else:
        return {'status':0,'error_type':1,'auctionId':transaction_id,'msg':'Can not find the Transaction by id '+str(transaction_id)}


def auctionEvent(log_info,playerId):
    db_tool.writeEventLog(log_info,playerId)
    
    
def getAuctionEvent(playerId):
    e_type = 1
    info = db_tool.getEventLog(e_type,playerId)
    return info


@getOneDBConn
def __countTransaction(db,conn,playerId):
    db.execute("select count(*) from transaction where user_id=%s",(playerId,))
    num = db.fetchone()
    return num.values()[0]

@getOneDBConn
def __getTransactionById(db,conn,transaction_id):
    db.execute("SELECT * FROM transaction WHERE id = %s",(transaction_id,))
    transaction = db.fetchone()
    return transaction

#lock and get
def __lockTransactionById(db,conn,transaction_id):
    db.execute("SELECT * FROM transaction WHERE id = %s for update",(transaction_id,))
    transaction = db.fetchone()
    return transaction

@getOneDBConn
def __addTransactionItem(db,conn,playerId,prop_id,prop_num,price):
    db.execute("INSERT INTO transaction(price,number,prop_id,user_id) VALUES(%s,%s,%s,%s)",
                   (price,prop_num,prop_id,playerId))
    conn.commit()

@getOneDBConn
def __delTransactionItem(db,conn,transaction_id):
    db.execute("DELETE FROM transaction WHERE id = %s",(transaction_id,))
    conn.commit()

def __delLockTransactionItem(db,conn,transaction_id):
    db.execute("DELETE FROM transaction WHERE id = %s",(transaction_id,))
    conn.commit()
    
@getOneDBConn
def __getTransactionList(db,conn,playerId):
    db.execute("SELECT * FROM transaction WHERE user_id = %s",(playerId,))
    transactions = db.fetchall()
    if transactions:
        returnVal = []
        for item in transactions:
           returnVal.append({'id':item['id'],'price':item['price'],'number':item['number'],'definitionId':item['prop_id']})
        return returnVal
    else:
        return []