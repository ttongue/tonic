#!/usr/bin/python
import sys
sys.path.append("../../lib")
sys.path.append("../../config")

import memberSystemMySQL as memberSystem
import datetime


members=memberSystem.loadMemberDatabase()
sorted_members=sorted(members, key=lambda members: members[memberSystem.DBCOL_MEMBER_NUMBER])
print "Content-type: text/pain\n\n"
print "Member #|Name|E-mail|Plan|Joined|PaidThru|Zip\n";
for line in sorted_members:
  memberNumString="%s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  memberName="%s %s" % (line[memberSystem.DBCOL_FIRST_NAME],line[memberSystem.DBCOL_LAST_NAME])
  memberAddr="%s" % line[memberSystem.DBCOL_ADDR_1]
  memberCity="%s" % line[memberSystem.DBCOL_CITY]
  memberState="%s" % line[memberSystem.DBCOL_STATE]
  memberZIP="%s" % line[memberSystem.DBCOL_ZIP]
  memberJoined="%s" % line[memberSystem.DBCOL_JOINED]
  memberPlan="%s" % line[memberSystem.DBCOL_PLAN]
  memberPaidThru="%s" % line[memberSystem.DBCOL_PAID_THRU]
  memberEmail="%s" % line[memberSystem.DBCOL_EMAIL]
  print memberNumString+"|"+memberName+"|"+memberEmail+"|"+memberPlan+"|"+memberJoined+"|"+memberPaidThru+"|"+memberZIP
