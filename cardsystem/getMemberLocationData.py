#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import memberSystemMySQL as memberSystem
import datetime


members=memberSystem.loadMemberDatabase()
sorted_members=sorted(members, key=lambda members: members[memberSystem.DBCOL_MEMBER_NUMBER])
for line in sorted_members:
  memberNumString="%s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  memberName="%s %s" % (line[memberSystem.DBCOL_FIRST_NAME],line[memberSystem.DBCOL_LAST_NAME])
  memberAddr="%s" % line[memberSystem.DBCOL_ADDR_1]
  memberCity="%s" % line[memberSystem.DBCOL_CITY]
  memberState="%s" % line[memberSystem.DBCOL_STATE]
  memberZIP="%s" % line[memberSystem.DBCOL_ZIP]
  print memberNumString+"|"+memberAddr+"|"+memberCity+"|"+memberState+"|"+memberZIP
