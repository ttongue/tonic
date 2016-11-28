#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
# import cardsystem as cardsystem
import datetime
import re
import os
import traceback
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

reload(sys)  
sys.setdefaultencoding('utf8')


NUMBER_TO_CREATE=50
NUMBER_OF_MONTHS=1
DEBUG=False

try:
  members=memberSystem.loadMemberDatabase() 
  member_id=1     
  memberRecord=memberSystem.findMemberRecord(members,member_id)
  cid=memberRecord[memberSystem.DBCOL_CID] 
  for i in range(0,NUMBER_TO_CREATE):
	guid=memberSystem.addDayPassToCID(cid,NUMBER_OF_MONTHS)
        filename="cert%s.svg" % i
        pngfilename="cert%s.png" % i
        os.system("cp templates/MembershipCreditCertificateTemplate.svg output/%s" % filename)
        os.system("perl -p -i -e 's/AAAAAAAA-BBBB-CCCC-DDDD-EEEEEE/%s/g' output/%s" % (guid,filename))
        os.system("svgexport output/%s output/%s png 2000:" % (filename,pngfilename))

except:
   traceback.print_exc()
