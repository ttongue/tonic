#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
import datetime
import re
import os

logFile="/var/log/cardsystem.log"

def getKeyAccessList(year,month,day):
    	global logFile
	inFile = open(logFile,"r")
	dpattern=re.compile("^%s-%s"%(month,day))
        output=""
	for line in inFile:
		myResult=dpattern.search(line)
		if (myResult):
			output=output+line+"<br>"

        if (output != ""):
		output="<p></p><p>Below is the list of RFID entries:</p>"+output
   	return output
		

def getSignedInList(year,month,day):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select transaction_id,member_id,name,start_datetime,end_datetime from %s"%(memberSystem.MYSQL_SIGNIN_TABLE)
   cur.execute(query)
   rows = cur.fetchall()
   lines=""
   output=""
   dpattern=re.compile("%s\-%s\-%s"%(year,month,day))
   for row in rows:
        member_id=row[1]
        datestr="%s"%row[3]
	myResult=dpattern.search(datestr)
        if (myResult):
	 	if (member_id == -1):
			member_id="Guest"
	 	lines=lines+"<tr><td>%s</td><td>%s</td><td>%s</td><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td>%s</td></tr>\n"%(member_id,row[2],row[3],row[4])
	else:
		continue
   if (lines != ""):
	output="<table bgcolor=#404040><tr><th>Member #</th><th>Name</th><th>Sign-In Time</th><th></th><th>Sign-Out Time</th></tr>"+lines+"</table>"
   return output

def generateDateForm(year, month, day):
    months={'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
    formOut="<form action=/cardsystem/listSignins.py method=POST> <p>Month: <select name=month>"
    for m in range(1,13):
        m="%02d"%m
	if (m == month):
		formOut=formOut+"<option value='%s' selected>%s"%(m,months[m])
	else:
		formOut=formOut+"<option value='%s'>%s"%(m,months[m])
    formOut=formOut+"</select>&nbsp;&nbsp;&nbsp;&nbsp;Day:<select name=day>"
    for d in range(1,32):
	if ("%02d"%d == day):
		formOut=formOut+"<option value='%s' selected>%s"%("%02d"%d,d)
	else:
		formOut=formOut+"<option value='%s'>%s"%("%02d"%d,d)
    formOut=formOut+"</select> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<select name=year> "
    for y in range(2014,2017):
	if ("%s"%y == year):
		formOut=formOut+"<option value='%s' selected>%s"%(y,y)
	else:
		formOut=formOut+"<option value='%s'>%s"%(y,y)
    formOut=formOut+"</select> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=submit value='Submit'> </p> "
    return formOut

def stepOne(importantMessage,importantMessageGuest,year,month,day):
    body=memberSystem.loadTemplate("templates/listsignin.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Sign-In List")
    outText=tmpheader+body+footer
    signedIn=getSignedInList(year,month,day)
    keyList=getKeyAccessList(year,month,day)
    formOut=generateDateForm(year,month,day)
    outText=outText.replace("#FORMOUT#",formOut)
    outText=outText.replace("#SIGNED_IN_LIST#",signedIn+keyList)
    print outText;

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")
try:
  form = cgi.FieldStorage()
  month=cgi.escape(form.getfirst("month",datetime.datetime.now().strftime("%02m")))
  day=cgi.escape(form.getfirst("day",datetime.datetime.now().strftime("%02d")))
  year=cgi.escape(form.getfirst("year",datetime.datetime.now().strftime("%Y")))
  
  stepOne("","",year,month,day)
  print "<!--"
  sys.exit(0)
  
except:
  cgi.print_exception()
