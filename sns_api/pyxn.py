import logging
import hashlib
import sys
import time
import urllib
import urllib2
import httplib
import urlparse
import mimetypes
import modules.db_tool as db_tool
from settings import *

class XnApi():
    def __init__(self,sig,session_key,sns_id):
        self.sns_id = str(sns_id)
        self.url = "http://api.renren.com/restserver.do"
        self.config = {
            'api_key':"826073379185423c8afd217cb44ab169",
            'call_id':0,
            'v':"1.0",
            'sig':sig,
            'format':'json',
            'session_key':session_key,
        }
    
    def getUserInfo(self):
        self.config['call_id'] = self.__getTime()
        self.config['method'] = "users.getInfo"
        self.config['uids'] = self.sns_id
        res = self.__callRenren(self.config)
	logging.debug(res)
        return res[0]
        
    def getFriends(self):
        self.config['call_id'] = self.__getTime()
        self.config['method'] = "friends.getAppFriends"
        self.config['fields'] = "name,tinyurl"
        res = self.__callRenren(self.config)
        return res
    
    def __getTime(self):
        return time.time()
        
    def __callRenren(self,dict):
        data = urllib.urlencode(dict)
        res = urllib2.urlopen(self.url, data=data)
        return eval(res.read())
'''   
time_now = time.time()
url = "http://api.renren.com/restserver.do"
dict = {
    'api_key':"826073379185423c8afd217cb44ab169",
    'method':"users.getInfo",
    'call_id':time_now,
    'v':"1.0",
    'sig':'343ef1bb8e24897dd1c908a736ac24fe',
    'uids':'278296567',
    'format':'json',
    'session_key':'2.fc246d86f5078dbc4e4a357491827632.3600.1302174000-278296567',
    }
data = urllib.urlencode(dict)
res = urllib2.urlopen(url, data=data)
ret = eval(res.read())
print ret[0]['name']
'''
