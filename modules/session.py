#-*- coding=utf8 -*-
from settings import *

from modules.db_tool import getOneDBConn
import traceback

#验证session
def getPlayerSession(func):
    def wapper(*args):
        #定义函数返回值
        returnVal = None
        try:
            serverInfo = args[0]
            skey = serverInfo['session_id']
            player_id,sns_id = getSession(skey)
            
            #验证playerId是否存在
            if not player_id:
                return {'status':500,'msg':'getPlayerSession '+sns_id}
            
            serverInfo['playerId'] = player_id
            
            if len(args)>1:
                returnVal = func(serverInfo,args[1])
            else:
                returnVal = func(serverInfo)
        except Exception,e:
            exstr = traceback.format_exc()
            root_logger.error(exstr)
        return returnVal
    
    return wapper

#获取session相关的playerId，snsId
def getSession(skey):
    user_session = getUserSession(skey)
    if user_session:
        return user_session['player_id'],user_session['sns_id']
    else:
        return False,"session不存在"


@getOneDBConn
def getUserSession(db,conn,skey):
    db.execute("SELECT * FROM session WHERE skey = %s",(skey,))
    user_session = db.fetchone()
    return user_session