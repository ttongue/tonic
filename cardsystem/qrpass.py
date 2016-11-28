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



print("Content-type: text/html\n\n")
try:
  form = cgi.FieldStorage()
  qrcode=cgi.escape(form.getfirst("qrcode",""))
  if (qrcode == ""): 
    print "No QR Code provided."
    print "<!--"
    sys.exit(0)
  if (len(qrcode) != 36):
    print "Invalid QR Day Pass Code Format. Please try again."
    print "<!--"
    sys.exit(0)
  memberRecord=memberSystem.getMemberRecordFromDayPass(qrcode) 
  if (memberRecord[memberSystem.DBCOL_MEMBER_NUMBER] < 0):
    print "Invalid QR Day Pass Code - QR Code is either expired or incorrect!"
    print "<!--"
    sys.exit(0)
  member_id=memberRecord[memberSystem.DBCOL_MEMBER_NUMBER]
  name=memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
  email=memberRecord[memberSystem.DBCOL_EMAIL]
  zip=memberRecord[memberSystem.DBCOL_ZIP]
  memberSystem.markDayPassAsUsed(qrcode)
  if (cardsystem.alreadySignedIn(member_id)):
	signedIn=1
        print "Welcome Back %s! Your Day Pass with QR Code %s has been validated. The door is unlocked, please come in!" % (name,qrcode)
  else:
	cardsystem.recordSignIn(member_id,name,zip,email,"")
        print "Welcome %s! Your Day Pass with QR Code %s has been validated. You have been automatically signed in and the door is unlocked, please come in!" % (name,qrcode)
  
  c=os.popen("links --source http://192.168.13.22/door1 &> /dev/null",'r');
  c.close()

except:
  cgi.print_exception()
