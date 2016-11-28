#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
import datetime
import cardsystem
import re
import os



def stepOne(importantMessage,importantMessageGuest):
    body=memberSystem.loadTemplate("templates/accountStatus1.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Account Status")
    outText=tmpheader+body+footer
    outText=outText.replace("<!--ERROR_MESSAGE-->",importantMessage)
    outText=outText.replace("<!--ERROR_MESSAGE2-->",importantMessageGuest)
    print outText;

def stepTwo(memberRecord,memberDatabase):
   
   template=" "
   membershipLine=" "
   template=memberSystem.loadTemplate("templates/accountStatus2.html")
   tmpheader=header
   name=memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
   memberId=memberRecord[memberSystem.DBCOL_MEMBER_NUMBER];
   daySpan=int(memberSystem.howManyDaysDue(memberRecord))
   slash=re.compile(r'\/')
   dash=re.compile(r'\-')
   isPaid = cardsystem.buildIsPaid(memberDatabase)
   today=datetime.datetime.now()
   paidThru=slash.split(memberRecord[memberSystem.DBCOL_PAID_THRU])
   if (len(paidThru) < 3):
     tempThru=dash.split("%s" % memberRecord[memberSystem.DBCOL_JOINED])
     paidThru=(tempThru[1],tempThru[2],tempThru[0])
   paidThruDateTime=datetime.datetime(int(paidThru[2]),int(paidThru[0]),int(paidThru[1]))
   numDays = (today - paidThruDateTime + datetime.timedelta(-1)).days
   cardStatus="CARD ACCESS ENABLED"
   plan=memberRecord[memberSystem.DBCOL_PLAN]
   extraInfo=""
   if ((plan[0:4]=="Supe") | (plan[0:4]=="spec") | (plan[0:3]=="org") | (plan[0:3]=="cow")):
     extraInfo="Access available: 24/7/365"
   else:
     extraInfo="Access available: M/T/Th/F 6:30pm - 10:30pm, Sat/Sun 2pm - 10pm"
   if (plan == "Associate"):
     cardStatus="ASSOCIATE ACCOUNT - DAY PASS REQUIRED FOR ACCESS";
     extraInfo=""
   else: 
     if (numDays > 10):
       cardStatus="CARD ACCESS DISABLED - ACCOUNT PAST DUE"
   accountStatus="Account Type: %s<br>Paid Through: %s <br><!--Is Paid: %s<br>-->Access Card Status: %s<br>%s<!--<br>Number of Days Past Due: %s-->" % (plan,memberRecord[memberSystem.DBCOL_PAID_THRU],isPaid["%s" % memberId],cardStatus,extraInfo,daySpan)
   email=memberRecord[memberSystem.DBCOL_EMAIL]
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Account Status")
   outText=memberSystem.processMemberRecordIntoTemplate(memberRecord,template)
   outText=outText.replace("#NAME#",name)
   outText=outText.replace("#ACCOUNT_STATUS#",accountStatus)
   # outText=outText.replace("#MEMBERSHIP_LEVEL#",membershipLine)
   invoiceHTML=memberSystem.getInvoiceHTML(memberRecord)
   if (int(daySpan) > 0):
     invoiceHTML+="<center><form action=https://ssl.techvalleycenterofgravity.com/billing/recurring.py method=POST>"
     invoiceHTML+= "<input type=hidden name=member_id value='%s'>" % memberId
     invoiceHTML+= "<input type=hidden name=zip value='%s'>"% memberRecord[memberSystem.DBCOL_ZIP]
     invoiceHTML+= "<input type=hidden name=next_step value=2>"
     invoiceHTML+= "<input type=submit value='Pay Current Invoice'>"
     invoiceHTML+= "</form></center>"
     invoiceHTML+= "<font size=-2>(Note, this invoice may not include volunteer credits due. "
     invoiceHTML+= "<br>If you feel there is an error, please contact <a href=mailto:treasurer@techvalleycenterofgravity.com>treasurer@techvalleycenterofgravity.com</a>)</font>"
   outText=outText.replace("#CURRENT_INVOICE#",invoiceHTML)
   print tmpheader+outText+footer

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header-new.html")
footer=memberSystem.loadTemplate("templates/footer-new.html")
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
  memberRecord=memberSystem.findMemberRecord(members,member_id)
  if (memberRecord[memberSystem.DBCOL_ZIP]!=zip):
  	stepOne("No member record exists with that id and Zip code!","")
    	print "<!--"
    	sys.exit(0)
  stepTwo(memberRecord, members) 
  
except:
  cgi.print_exception()
