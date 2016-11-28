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


def getTransactionId(member_id):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select transaction_id from %s where end_datetime IS NULL AND member_id=%s"%(memberSystem.MYSQL_SIGNIN_TABLE,member_id)
   cur.execute(query)
   rows = cur.fetchall()
   for row in rows:
	return row[0]
   return ""

def getSignedInList():
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select transaction_id,member_id,name,start_datetime from %s where end_datetime IS NULL"%(memberSystem.MYSQL_SIGNIN_TABLE)
   cur.execute(query)
   rows = cur.fetchall()
   lines=""
   output=""
   
   for row in rows:
         member_id=row[1]
	 if (member_id == -1):
		member_id="Guest"
	 lines=lines+"<tr><td>%s</td><td>%s</td><td>%s</td><td><a href=signin.py?action=logout&transaction_id=%s>Logout</a></td></tr>\n"%(member_id,row[2],row[3],row[0])
   if (lines != ""):
	output="<table bgcolor=#404040><tr><th>Member #</th><th>Name</th><th>Sign-In Time</th><th>Action</th></tr>"+lines+"</table>"
   return output

print("Content-type: text/html\n\n")
try:
  outList=getSignedInList();
  print outList;
except:
  cgi.print_exception()
