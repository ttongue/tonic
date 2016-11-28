#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import memberSystemMySQL as memberSystem
import datetime
import re

today=datetime.date.today()
datestr=today.strftime('%Y-%02m-%02d')
todayNum=int(today.strftime('%Y%02m%02d'))

members=memberSystem.loadMemberDatabase()
sorted_members=sorted(members, key=lambda members: members[memberSystem.DBCOL_MEMBER_NUMBER])
slash=re.compile(r'\/')
outline=""
for line in sorted_members:
  memberNumString="%s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  outline=outline+line[memberSystem.DBCOL_FIRST_NAME]+"\t"+line[memberSystem.DBCOL_LAST_NAME]+"\t"+line[memberSystem.DBCOL_EMAIL]+"\n"
  # if (line[memberSystem.DBCOL_PLAN] == "coworking"):
  #     paidThru=slash.split(line[memberSystem.DBCOL_PAID_THRU])
  #     if (paidThru==None): continue
  #     if (len(paidThru) < 3): continue
  #     pTN=int("{0:s}{1:02d}{2:02d}".format(paidThru[2],int(paidThru[0]),int(paidThru[1]))) 
  #     if ((todayNum - pTN) < 80):  
  #       # print memberNumString+(": %d : " % (todayNum-pTN))+"   : "+line[memberSystem.DBCOL_FIRST_NAME]+" "+line[memberSystem.DBCOL_LAST_NAME]+" : "+line[memberSystem.DBCOL_EMAIL]
  #       outline=outline+line[memberSystem.DBCOL_EMAIL]+","

print outline
