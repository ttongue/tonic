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

logFile="/var/log/cardsystem.log"

def getKeyAccessList(year,month,day):
    	global logFile
	inFile = open(logFile,"r")
	dpattern=re.compile("^%s-%s"%(month,day))
        output=""
	for line in inFile:
		myResult=dpattern.search(line)
		if (myResult):
			output=output+line+"<br>"

        if (output != ""):
		output="<p></p><p>Below is the list of RFID entries:</p>"+output
   	return output
		

def getSignedInList(year,month):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select transaction_id,member_id,name,start_datetime,end_datetime from %s"%(memberSystem.MYSQL_SIGNIN_TABLE)
   cur.execute(query)
   rows = cur.fetchall()
   lines=""
   output=""
   dpattern=re.compile("%s\-%s"%(year,month))
   for row in rows:
        member_id=row[1]
        datestr="%s"%row[3]
	myResult=dpattern.search(datestr)
        if (myResult):
	 	if (member_id == -1):
			member_id="Guest"
	 	lines=lines+"%s\t%s\t%s\t%s\n"%(member_id,row[2],row[3],row[4])
	else:
		continue
   if (lines != ""):
	output="Member #\tName\tSign-In Time\tSign-Out Time\n"+lines
   return output

month="07"
year="2016"
output=getSignedInList(year,month)
print output
sys.exit(0)
  
