from pyamf.remoting.client import RemotingService

gw = RemotingService('http://192.168.3.111:8081')
service = gw.getService('getAuction')

#print service({'sns_id': u'1', 'session_key': u'1', 'sig': u'1', 'session_id': u'1'},13000100)
print service({'sns_id': u'3', 'session_key': u'3', 'sig': u'1', 'session_id': u'3'}, 3)



