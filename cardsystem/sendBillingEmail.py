#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import memberSystemMySQL as memberSystem
import datetime
import re

DEBUG=False

today=datetime.date.today()
datestr=today.strftime('%Y-%02m-%02d')
todayNum=int(today.strftime('%Y%02m%02d'))

todaysDiscountFile = "MemberDiscounts-%s.txt" % datestr

members=memberSystem.loadMemberDatabase()
sorted_members=sorted(members, key=lambda members: members[memberSystem.DBCOL_MEMBER_NUMBER])
discounts=memberSystem.loadDiscountDatabase(todaysDiscountFile)
slash=re.compile(r'\/')

for line in sorted_members:
  memberNumString="%s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  amountDue=0;
  paidThru=slash.split(line[memberSystem.DBCOL_PAID_THRU])        
  print "DEBUG: MEM NUMBER: %s" % line[memberSystem.DBCOL_MEMBER_NUMBER];
  if (line[memberSystem.DBCOL_PLAN] == "Associate") : continue
  if ((line[memberSystem.DBCOL_PARENT_MEMBER_NUMBER]!="") | (paidThru==None)): continue
  pTN=int("{0:s}{1:02d}{2:02d}".format(paidThru[2],int(paidThru[0]),int(paidThru[1])))
  if (todayNum < pTN) : continue
  memberDiscounts=memberSystem.getDiscountsForMember(discounts,line[memberSystem.DBCOL_MEMBER_NUMBER],line[memberSystem.DBCOL_PAID_THRU])
  memberSystem.sendDueNotice(line,memberDiscounts,DEBUG)


