#-*- coding=utf8 -*-
from settings import *
import datetime


#是否是今天
def isToday(optime):
    todayTime = int(time.time())
    todayTimeStr = time.strftime("%Y%m%d",time.localtime(todayTime))
    opTimeStr = time.strftime("%Y%m%d",time.localtime(optime))
    return (todayTimeStr == opTimeStr)

#是否是昨天
def isYesterday(optime):
    todayTime = int(time.time())
    yesterdayTimeStr = time.strftime("%Y%m%d",time.localtime(todayTime-24*60*60))
    opTimeStr = time.strftime("%Y%m%d",time.localtime(optime))
    return (yesterdayTimeStr == opTimeStr)
    
#与当前时间间隔天数
def getIntervalDays(optime):
    d1 =  time.strftime("%j", time.localtime())
    d2 =  time.strftime("%j", time.localtime(optime))
    days = int(d1)- int(d2)
    return days


#获取当前时间是星期几
#1、2、3、4、5、6、0
def getWeekDay():
    return time.strftime('%w',time.localtime())


#获取当前时间是当年的第几周，
#把星期一做为第一天（值从0到53）,如1月1日非星期一，返回0
def getWeekNum(optime):
    d = time.localtime(optime)
    return time.strftime('%W',d)
    
    
#second to string
def sec2str(second):
    return time.strftime("%Y-%m-%d %H:%M:%s",time.localtime(second))

#string to second
def str2sec(timestr):
    struct_time = time.strptime(timestr, '%Y-%m-%d %H:%M:%S')
    return int(time.mktime(struct_time))