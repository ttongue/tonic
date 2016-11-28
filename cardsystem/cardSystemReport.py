#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cardsystem
import memberSystemMySQL as memberSystem
import re
import datetime

logFile="/var/log/cardsystem.raw.log"


bufChars=0
bufAsc=""
bufHex=""
dumpDir=""
logList=[]
lastDateTime=""

dateTimeParse=re.compile(">\s+(\d\d)\-(\d\d)\s+(\w\w)\s+(\d\d)\:(\d\d)")
cardEntryParse=re.compile(">\s+\*?\s*RD\#0\d\s+([\w\_]+)\s([X\s])\s([\w\-]+)\s(\d+)\s+(\w?\w?)")


def addToLogList():
	global bufChars, bufAsc,bufHex,dumpDir,lastDateTime,memberNumbersFromRFID,memberDatabase
	if (bufChars == 0):
		return
	appendString="%s %-70s" % (dumpDir,bufAsc)
	#print appendString
	logList.append(appendString)
	dateMatch=dateTimeParse.search(appendString)
	if (dateMatch):
		dateString="%s-%s %s %s:%s" % (dateMatch.group(1),dateMatch.group(2),dateMatch.group(3),dateMatch.group(4),dateMatch.group(5))
		# print dateString
		lastDateTime = dateString
	cardMatch=cardEntryParse.search(appendString)
	if (cardMatch):
		cardNum=int(cardMatch.group(4))
		reportString="%s\tRFID: %s" % (lastDateTime, cardNum)
		if (memberNumbersFromRFID.has_key("%s" % cardNum)):
			memberNum=memberNumbersFromRFID["%s" % cardNum]
			memberRecord=memberSystem.findMemberRecord(memberDatabase,memberNum)
			reportString=reportString+"\tMember Number: %s" % memberNum
			reportString=reportString+"\tName: %s %s" % (memberRecord[memberSystem.DBCOL_FIRST_NAME], memberRecord[memberSystem.DBCOL_LAST_NAME])
			reportString=reportString+"\tPlan: %s" % memberRecord[memberSystem.DBCOL_PLAN]
		else:
			reportString=reportString+"\tMember Number: -1\tName: Not Found\tPlan: Not Found"
		if (cardMatch.group(5)):
			reportString=reportString+"\tFlag: %s" % cardMatch.group(5)
		else:
			reportString=reportString+"\tFlag: OK"
		print reportString
	bufChars=0;
	bufAsc=""
	bufHex=""
	return()


def buildRFIDLookupTable():
	global memberDatabase
	memberNumber={'-1':'Hodor'}
	for memberLine in memberDatabase:
		number=memberLine[memberSystem.DBCOL_MEMBER_NUMBER]
		rfid = memberLine[memberSystem.DBCOL_RFID]
		if (rfid != ""):
			memberNumber[rfid]=number
	return memberNumber
			




memberDatabase=memberSystem.loadMemberDatabase()
memberNumbersFromRFID=buildRFIDLookupTable()
infile = open(logFile,"r")
p=re.compile('^(.)\s+0x(..)')
#p2=re.compile('^..(..)')
p3=re.compile('\((.)\)')
for line in infile:
	line.rstrip('\r\n')
	myResult=p.match(line)
	if (myResult):
		myDir=myResult.group(1)
		# print myDir
		#line=re.sub('^(.)\s+','',line)
		# myDir=myResult.group(0)
		#print line
		if (myDir == "<"):
			#print myDir
			if (dumpDir == ">"):
				addToLogList()
			dumpDir=myDir;
		else:
			if (myDir == ">"):
				#print myDir
				if (dumpDir == "<"):
					addToLogList()
				dumpDir=myDir
	#myHexResult=p2.match(line)
		hexchar=myResult.group(2)
	
		bufHex = bufHex+" "+hexchar
		#print "---"+hexchar
	#print line
	myAscResult=re.search(r"\(+(.)\)+",line)
	if (myAscResult):
		bufAsc=bufAsc+myAscResult.group(1)
	else:
		bufAsc=bufAsc+" "
	bufChars=bufChars+1
	if (hexchar=="0a"):
		addToLogList()
	if (bufChars>70):
		addToLogList()

# addToLogList()




