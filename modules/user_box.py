#-*- coding=utf8 -*-
from settings import *

from config.prop_config import *
from config.box_config import *
from config.drawing_config import *
import time
import random
from modules.db_tool import getOneDBConn
import modules.db_tool as db_tool
import modules.collection as collection
import modules.time_tool as time_tool

#获得箱子信息
def getBoxInfo(snsid):
    helperIds = getUserBoxHelpUsers(snsid)
    return {'status':1,'helper_ids':helperIds,'box_config':BOX_CONFIG}


#开箱子
def openBox(snsid):
    user_box = getUserBox(snsid);
    if(user_box):
        if(user_box['is_open'] == 1):
            return {'status':0,'msg':'box is opened.'}
        else:
            pass
    else:
        return {'status':0,'msg':'box is null.'}
    
    helperIds = helpStr2List(userbox['helper_ids'])
    
    if(helperIds):
        if len(helperIds) >= BOX_CONFIG['need_users']:
            reward,addexp = getRewardAndExp(snsid,BOX_CONFIG)
            '''
            retval = []
            for item in reward:
                retval.append(item)
            '''
            player = db_tool.__getPlayer(snsid)
            return {'status':1,'add_exp':addexp,'reward':reward,'bag':db_tool.getAllProp(player['id'])}
        else:
            return {'status':0,'msg':'Less users.'}
    else:
        return {'status':0,'msg':'openbox --> No helperIds.'}

#箱子是否已经打开
def getUserBoxStatus(snsId):
    retval = checkbox(snsId)
    return {'isopen':retval['is_open']}
    
#检查箱子信息
def checkbox(snsId):
    #get config
    box_start = time_tool.str2sec(BOX_CONFIG['start_time'])
    box_end = time_tool.str2sec(BOX_CONFIG['end_time'])
    #get user box
    user_box = getUserBox(snsId);
    
    retstr = {}
    if(not user_box):
        retstr = insertUserBox(snsId)
    else:
        time_now = int(time.time())
        if(time_now < box_start or time_now > box_end):
            retstr = {'is_open':1}
        else:
            start_time = user_box['start_time']
            if(start_time < box_start):
                retstr = resetUserBox(snsId,0)
            elif(start_time > box_end):
                retstr = resetUserBox(snsId,1)
            else:
                retstr = {'is_open':user_box['is_open']}
    return retstr

#{key:val}中，是否有key in collectList
def hasSameItem(item, collectList):
    hasVal = False;
    for key in collectList:
        if item.has_key(key):
            hasVal = True
            break
        else:
            pass
    return hasVal

#从items中找出未收集的item列表
def getUnCollectItem(collectList,items):
    uncollectList = []
    for item in items:
        if not hasSameItem(item,collectList):
            uncollectList.append(item);
    return uncollectList


@getOneDBConn
def insertUserBox(db,conn,snsId):
    time_now = int(time.time())
    db.execute("INSERT INTO user_box(owner_id,helper_ids,is_open,start_time) VALUES(%s,%s,%s,%s)",(snsId,'',0,time_now))
    conn.commit()
    return {'is_open':0}
    
@getOneDBConn
def resetUserBox(db,conn,snsId,is_open):
    time_now = int(time.time())
    db.execute("UPDATE user_box set is_open = %s,helper_ids=%s,start_time=%s where owner_id = %s",(is_open,'',time_now,snsId))
    conn.commit()
    return {'is_open':is_open}
    
@getOneDBConn    
def getUserBox(db,conn,snsId):
    db.execute("SELECT * FROM user_box WHERE owner_id = %s",(snsId,))
    userbox = db.fetchone()
    return userbox

#获取帮助的好友列表
def getUserBoxHelpUsers(snsId):
    info = []
    userbox = getUserBox(snsId)
    if userbox:
        info = helpStr2List(userbox['helper_ids'])
    return info

def helpStr2List(helpStr):
    alist = []
    if len(helpStr)>0:
        alist = helpStr.split(':')
    return alist

@getOneDBConn
def getRewardAndExp(db,conn,snsId,config):
    db.execute("UPDATE user_box set is_open = 1 where owner_id = %s",(snsId,))

    #第一次添加经验
    exp = 0
    player = db_tool.__getPlayer(snsId)
    #get collection
    collectionStr = db_tool.__getPlayerCollection(player['id'])['status']
    collectionList = collection.__collectionToList(collectionStr)
    
    #随机获取一个未收集到的图鉴奖励
    rewards = config.get('reward')
    uncollectItem = getUnCollectItem(collectionList,rewards)
    #如果都收集过了
    if(not uncollectItem):
        uncollectItem = rewards

    reward = random.choice(uncollectItem)
    
    prop = db_tool.getAllProp(player['id'])
    for propId in reward.keys():
        #add collection
        if str(propId) in collectionList:
            exp += 0
        else:
            exp += DRAWING_CONFIG[int('1'+propId)]['exp']
            player['exp'] += exp
            db_tool.__updatePlayer(player['id'],{'exp':player['exp']})
            collection.__updateCollection(player,propId)
        #add prop
        db_tool.__addPropItem(prop,propId,reward[propId])
    db_tool.saveAllProp(player['id'],prop)
    conn.commit()
    return reward,exp