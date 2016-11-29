#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
import tvcogCfg as tvcog
import datetime
import re
import os
import mailchimp


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
   if (subscribe == "1"):
      try:
      	api=mailchimp.Mailchimp(tvcog.MAILCHIMP_API_KEY)
      	api.lists.subscribe(tvcog.MAILCHIMP_LIST_ID, {'email': email})
      except mailchimp.ListAlreadySubscribedError:
	subscribe="0"
   cur.execute(query)


def stepOne(importantMessage,importantMessageGuest):
    body=memberSystem.loadTemplate("templates/signin.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Sign-In")
    outText=tmpheader+body+footer
    outText=outText.replace("<!--ERROR_MESSAGE-->",importantMessage)
    outText=outText.replace("<!--ERROR_MESSAGE2-->",importantMessageGuest)
    signedIn=getSignedInList()
    outText=outText.replace("#SIGNED_IN_LIST#",signedIn)
    print outText;

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")
try:
  form = cgi.FieldStorage()
  if (cgi.escape(form.getfirst("action","")) == "logout"):
	trans_id=int(cgi.escape(form.getfirst("transaction_id","")))
        logoutTransaction(trans_id)
        stepOne("","")
        print "<!--"
        sys.exit(0)
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
  if (member_id == -1):
	name=cgi.escape(form.getfirst("name",""))
	email=cgi.escape(form.getfirst("email",""))
        acceptLiability=cgi.escape(form.getfirst("liabilityAgreed",""))
        subscribe=cgi.escape(form.getfirst("subscribe",""))
        if (name==""):
		stepOne("","You must provide your name!")
    		print "<!--"
    		sys.exit(0)
        if (zip==""):
		stepOne("","You must provide your zip code!")
    		print "<!--"
    		sys.exit(0)
        if (email==""):
		stepOne("","You must provide your e-mail!")
    		print "<!--"
    		sys.exit(0)
	if not re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email):
                stepOne("","You must provide a VALID e-mail!")
                print "<!--"
                sys.exit(0)
        if (acceptLiability ==""):
		stepOne("","You must accept the liability agreement!")
    		print "<!--"
    		sys.exit(0)
  else:
  	memberRecord=memberSystem.findMemberRecord(members,member_id)
  	if (memberRecord[memberSystem.DBCOL_ZIP]!=zip):
    		stepOne("No member record exists with that id and Zip code!","")
    		print "<!--"
    		sys.exit(0)
	name=memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
        email=memberRecord[memberSystem.DBCOL_EMAIL]
	if (alreadySignedIn(member_id)):
		transaction_id=getTransactionId(member_id)
		stepOne("%s is already signed in. <a href=signin.py?action=logout&transaction_id=%s>Logout first</a> and then try again."%(name,transaction_id),"")
                print "<!--"
                sys.exit(0)

  
  body=memberSystem.loadTemplate("templates/signinComplete.html")
  recordSignIn(member_id,name,zip,email,subscribe)
  body=body.replace("#NAME#",name)
  body=body.replace("#EMAIL#",email)
  tmpheader=header
  tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Sign-In Complete!")
  tmpheader=tmpheader.replace("<!--METAREFRESH-->","<META http-equiv='refresh' content='5;http://systems.techvalleycenterofgravity.com/cardsystem/signin.py'>")
  print tmpheader+body+footer
  
except:
  cgi.print_exception()
