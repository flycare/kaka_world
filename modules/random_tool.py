#-*- coding=utf8 -*-
from settings import *
import random

cacheRandom = {}

#根据概率组合一个序列
def getRandomTable(key,items):
    if(cacheRandom.has_key(key)):
        table = cacheRandom[key]
    else:
        sequence = []
        relative_odds = []
        
        for i in range(len(items)):
                sequence.append(i)
                relative_odds.append(items[i]['relative_odds'])
    
        #根据概率组合新的value list
        table = [ z for x, y in zip(sequence, relative_odds) for z in [x]*y ]
        '''
        table = []
        for x,y in zip(sequence, relative_odds) :
            #y个x
            for z in [x]*y :
                table.append(z)
        '''
        cacheRandom[key] = table
    
    return table


#随机获取一个item
#items:随机获取概率配置
#key:用于缓存的关键字
def getRandomItem(key,items):
    
    table = getRandomTable(key,items)
    #root_logger.debug(cacheRandom)
    id = random.choice(table)
    item = items[id]
    
    returnVal = {}
    returnVal['type']=random.choice(item['value'])
    returnVal['num']=item['num']
    return returnVal


#随机获取多个item
def getRandomItemList(key,items):
    
    table = getRandomTable(key,items)
    #root_logger.debug(cacheRandom)
    ids = random.sample(table,3)
    #去除重复id
    ids = list(set(ids))
    
    itemList = []
    for id in ids:
        item = items[id]
        
        if item['value']:
            returnVal = {}
            returnVal['type']=random.choice(item['value'])
            returnVal['num']=item['num']
            
            itemList.append(returnVal)
    return itemList