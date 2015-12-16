#-*- coding=utf8 -*-
import traceback
from settings import *

#定义key_prefix
AUCTION_EVENTLOG_KEY_PRE = PLATFORM+'_auction_eventlog_'
PURCHASE_EVENTLOG_KEY_PRE = PLATFORM+'_purchase_eventlog_'

#用于处理异常的装饰器
def useCache(func):
    def wrapper(*arg):
        returnVal = None
        try:
            returnVal = func(*arg)
            return returnVal
        except Exception,e:
            exstr = traceback.format_exc()
            root_logger.error(exstr)
            return returnVal
    return wrapper


#拍卖日志
@useCache
def setAuctionEventLogCache(playerId,eventLogs):
    eventlog_key = AUCTION_EVENTLOG_KEY_PRE+str(playerId)
    MEMCACHE_CLIENT.set(eventlog_key,eventLogs)

@useCache
def getAuctionEventLogCache(playerId):
    eventlog_key = AUCTION_EVENTLOG_KEY_PRE+str(playerId)
    return MEMCACHE_CLIENT.get(eventlog_key)
    

#求购日志
@useCache
def setPurchaseEventLogCache(playerId,eventLogs):
    eventlog_key = PURCHASE_EVENTLOG_KEY_PRE+str(playerId)
    MEMCACHE_CLIENT.set(eventlog_key,eventLogs)

@useCache
def getPurchaseEventLogCache(playerId):
    eventlog_key = PURCHASE_EVENTLOG_KEY_PRE+str(playerId)
    return MEMCACHE_CLIENT.get(eventlog_key)