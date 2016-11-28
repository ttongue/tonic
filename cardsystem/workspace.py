#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import memberSystemMySQL as memberSystem
import datetime
import re
import os

def stepTwoGatherInfo(memberRecord):
   template=" "
   membershipLine=" "
   if (memberRecord[memberSystem.DBCOL_PLAN]=="Associate"):
     template=memberSystem.loadTemplate("templates/stepTwoAssociate.html")
     membershipLine=buildSelectionBoxForMemberships(memberRecord)
   else:
     template=memberSystem.loadTemplate("templates/stepTwo.html")
     membershipLine=buildMembershipLine(memberRecord)
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Membership Subscription Setup - Step 2")
   outText=memberSystem.processMemberRecordIntoTemplate(memberRecord,template)
   outText=outText.replace("#MEMBERSHIP_LEVEL#",membershipLine)
   invoiceHTML=getInvoiceHTML(memberRecord)

def stepTwoNotFound():
   template=memberSystem.loadTemplate("templates/idNotFound.html")
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG RFID Cardsystem member record not found.")
   outText=tmpheader+template+footer
   print outText

def stepOne():
    body=memberSystem.loadTemplate("templates/workspace.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Workspace Signout")
    outText=tmpheader+body+footer
    print outText;

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")
try:
  form = cgi.FieldStorage()
  id=cgi.escape(form.getfirst("id",""))
  zip=cgi.escape(form.getfirst("zip",""))
  if ((id == "") | (zip =="")):
    stepOne()
    print "<!--"
    sys.exit(0)
  members=memberSystem.loadMemberDatabase() 
  member_id=int(id)      
  memberRecord=memberSystem.findMemberRecord(members,member_id)
  if (memberRecord[memberSystem.DBCOL_ZIP]!=zip):
    stepTwoNotFound()
    print "<!--"
    sys.exit(0)
  if (member_id == -1):
    stepOne()
    print "<!--"
    sys.exit(0)
  if (memberSystem.alreadyHasReservation(member_id)):
    body=memberSystem.loadTemplate("templates/reservationExists.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","Workspace Reservation Already Active!")
    print tmpheader+body+footer
    print "<!--"
    sys.exit(0)
  memberSystem.reserveWorkspace(member_id)
  body=memberSystem.loadTemplate("templates/workspaceSlip.html")
  exptime = datetime.datetime.now()+datetime.timedelta(days=1)
  exptimestr = exptime.strftime("%A, %B %d, %Y  %r")
  body=body.replace("#FIRST_NAME#",memberRecord[memberSystem.DBCOL_FIRST_NAME])
  body=body.replace("#LAST_NAME#",memberRecord[memberSystem.DBCOL_LAST_NAME])
  body=body.replace("#EMAIL#",memberRecord[memberSystem.DBCOL_EMAIL])
  body=body.replace("#PHONE#",memberRecord[memberSystem.DBCOL_PHONE])
  body=body.replace("#EXPIRE_DATETIME#",exptimestr)
  tmpheader=header
  tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Workspace Signout")
  print tmpheader+body+footer
  
except:
  cgi.print_exception()
