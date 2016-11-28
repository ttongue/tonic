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
import subprocess


memberDatabase=memberSystem.loadMemberDatabase();
print("Content-type: text/html\n\n")
try:
  form = cgi.FieldStorage()
  rfid=cgi.escape(form.getfirst("rfid",""))
  if (rfid == ""): 
    print "No rfid provided."
    print "<!--"
    sys.exit(0)
  memberRecord = memberSystem.emptyMemberRecord();
  for line in memberDatabase:
	if (rfid == line[memberSystem.DBCOL_RFID]):
		memberRecord = line
  if (memberRecord[memberSystem.DBCOL_MEMBER_NUMBER] < 0):
    print "Invalid RFID - membership is either expired or incorrect!"
    print "<!--"
    sys.exit(0)
  member_id=memberRecord[memberSystem.DBCOL_MEMBER_NUMBER]
  name=memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
  email=memberRecord[memberSystem.DBCOL_EMAIL]
  zip=memberRecord[memberSystem.DBCOL_ZIP]
  if (cardsystem.alreadySignedIn(member_id)):
        cardsystem.recordSignOut(member_id)
        print "Member %s was already signed in with rfid %s, signing them out first." % (name,rfid)
  cardsystem.recordSignIn(member_id,name,zip,email,"")
  print "Welcome %s! You have been automatically signed in with rfid %s!" % (name,rfid)
  

except:
  cgi.print_exception()
