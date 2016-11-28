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
print "Content-type: text/plain\n\n"
for line in sorted_members:
  memberNumString="%s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  username=memberSystem.getUsername(line)
  neo4jString="CREATE ("+username+":Member {"
  neo4jString+="memberNumber:"+memberNumString+", "
  neo4jString+="firstName:\""+line[memberSystem.DBCOL_FIRST_NAME]+"\", "
  neo4jString+="lastName:\""+line[memberSystem.DBCOL_LAST_NAME]+"\", "
  neo4jString+="email:'"+line[memberSystem.DBCOL_EMAIL]+"', "
  neo4jString+="phone:'"+line[memberSystem.DBCOL_PHONE]+"', "
  neo4jString+="plan:'"+line[memberSystem.DBCOL_PLAN]+"'})"
  print neo4jString

