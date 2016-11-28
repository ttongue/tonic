#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import memberSystemMySQL as memberSystem
import datetime

today=datetime.date.today()
datestr=today.strftime('%Y-%02m-%02d')

members=memberSystem.loadMemberDatabase()
sorted_members=sorted(members, key=lambda members: members[memberSystem.DBCOL_MEMBER_NUMBER])
for line in sorted_members:
  memberNumString="%s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  print memberNumString+": "+line[memberSystem.DBCOL_EMAIL]
