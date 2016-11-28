#!/usr/bin/python
import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import datetime
import memberSystemMySQL as memberSystem

today=datetime.date.today()
datestr=today.strftime('%Y-%02m-%02d')
todayNum=int(today.strftime('%Y%02m%02d'))


form=cgi.FieldStorage()
members=memberSystem.loadMemberDatabase()
idNumStr=form.getfirst('id','')
idNumStr=cgi.escape(idNumStr)
idNum=int(idNumStr)

memberName='';

print "Content-type: text/html\n"

memberRecord=memberSystem.findMemberRecord(members,idNum)
if (memberRecord[memberSystem.DBCOL_MEMBER_NUMBER] == idNum):
  print memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
else:
  print "NULL"
