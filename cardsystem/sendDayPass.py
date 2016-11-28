#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
import cardsystem as cardsystem
import datetime
import re
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def logoutTransaction(trans_id):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   end_datetime=datetime.datetime.now().strftime("%Y-%02m-%02d %H:%02m:%S")
   cur=con.cursor()
   query="update %s SET end_datetime='%s' where transaction_id=%s"%(memberSystem.MYSQL_SIGNIN_TABLE,end_datetime,trans_id)
   cur.execute(query)

def alreadySignedIn(member_id):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select * from %s where end_datetime IS NULL AND member_id=%s"%(memberSystem.MYSQL_SIGNIN_TABLE,member_id)
   cur.execute(query)
   if (cur.rowcount > 0):
	return True
   else:
	return False

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


def recordSignIn(member_id,name,zip,email,subscribe):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   if (subscribe == ""):
	subscribe="0"
   start_datetime=datetime.datetime.now().strftime("%Y-%02m-%02d %H:%02M:%S")
   query="insert into %s SET member_id=%s, name='%s', email='%s', zip='%s', start_datetime='%s', mailing_list=%s "%(memberSystem.MYSQL_SIGNIN_TABLE,member_id,name,email,zip,start_datetime,subscribe)
   cur.execute(query)


def stepOne(importantMessage,importantMessageGuest):
    body=memberSystem.loadTemplate("templates/QRgetUserInfo.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Day Pass Retriever")
    outText=tmpheader+body+footer
    outText=outText.replace("<!--ERROR_MESSAGE-->",importantMessage)
    outText=outText.replace("<!--ERROR_MESSAGE2-->",importantMessageGuest)
    print outText;

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")
try:
  form = cgi.FieldStorage()
  id=cgi.escape(form.getfirst("id",""))
  zip=cgi.escape(form.getfirst("zip",""))
  if ((id == "") | (zip =="")):
    stepOne("","")
    print "<!--"
    sys.exit(0)
  members=memberSystem.loadMemberDatabase() 
  member_id=int(id)      
  name=""
  email=""
  subscribe="0"
  memberRecord=memberSystem.findMemberRecord(members,member_id)
  if (memberRecord[memberSystem.DBCOL_ZIP]!=zip):
   		stepOne("No member record exists with that id and Zip code!","")
    		print "<!--"
    		sys.exit(0)
  name=memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
  email=memberRecord[memberSystem.DBCOL_EMAIL]
  cid=memberRecord[memberSystem.DBCOL_CID] 
  plan=memberRecord[memberSystem.DBCOL_PLAN]
  qrcode=memberSystem.getFirstAvailableDayPass(memberRecord)
  if (qrcode == ""):
	stepOne("No Day Passes are available for %s (member number: %s). Please contact the treasurer at treasurer@techvalleycenterofgravity.com to add more day passes to your account and try again!" % (name,member_id),"")
	print "<!--"
        sys.exit(0)
  cardsystem.sendQRCodeEmail(qrcode,email) 
  body=memberSystem.loadTemplate("templates/QRsendComplete.html")
  body=body.replace("#NAME#",name)
  body=body.replace("#EMAIL#",email)
  tmpheader=header
  tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Day Pass Retrieval Complete!")
  tmpheader=tmpheader.replace("<!--METAREFRESH-->","<META http-equiv='refresh' content='10;http://systems.techvalleycenterofgravity.com/cardsystem/sendDayPass.py'>")
  print tmpheader+body+footer
  
except:
  cgi.print_exception()
