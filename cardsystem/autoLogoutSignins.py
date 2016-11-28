#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
import datetime
import re
import os
import mailchimp

# Number of hours to wait before expiring an entry. This is the mad amount of
# time we're willing to say someone is in the space without them coming and 
# and going.

expirationHours = 8

def expireSignins():
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()

   # The following query looks for active sign-in entries in the database
   # that are more than *expirationHours* old and it logs them out, setting a
   # flag (auto_logout) to 1 to indicate it was an automatic action. The end
   # time is set to be *expirationHours* later than the start time.
   query="UPDATE %s SET end_datetime = DATE_ADD(start_datetime,INTERVAL %s HOUR), auto_logout=1 WHERE end_datetime IS NULL AND start_datetime < DATE_SUB(CONVERT_TZ(NOW(),'+0:00','-5:00'), INTERVAL %s HOUR)" % (memberSystem.MYSQL_SIGNIN_TABLE,expirationHours,expirationHours)
   cur.execute(query)


expireSignins()
