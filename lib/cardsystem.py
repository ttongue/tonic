#!/usr/bin/python
import sys
sys.path.append("../lib")
sys.path.append("../config")

import re
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
import time
import datetime
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from subprocess import call

def sendQRCodeEmail(qrstring,toEmail):
	execstring="/usr/local/bin/qrencode -l Q -s 8 -o /tmp/qrcode.png '%s\'"%qrstring
	call(execstring, shell=True)
	# Create the container (outer) email message.
	msg = MIMEMultipart()
	msg['Subject'] = 'TVCOG Day Pass QR Code'
        me='president@techvalleycenterofgravity.com'
	msg['From'] = me
	msg['To'] = toEmail
	msg.preamble = 'TVCOG Day Pass QR Code'

    	# Open the files in binary mode.  Let the MIMEImage class automatically
    	# guess the specific image type.
    	fp = open("/tmp/qrcode.png", 'rb')
    	img = MIMEImage(fp.read())
    	fp.close()
    	msg.attach(img)

		# Send the email via our own SMTP server.
	s = smtplib.SMTP('localhost')
	s.sendmail(me, toEmail, msg.as_string())
	s.quit()
	execstring="rm -f /tmp/qrcode.png"
	call(execstring, shell=True)
	

def readSerialResponse(ser):
	out=''
        while (ser.inWaiting() > 0):
                out+=ser.read(1)
        return out

def waitForSerialEvent(ser):
	while (ser.inWaiting()== 0):
		time.sleep(0.2)
	return readSerialResponse(ser)

def sendSerialAndGetResponse(ser,outString):
	leadIn=readSerialResponse(ser)
        ser.write(outString+"\r\n")
        time.sleep(0.2)
        response=readSerialResponse(ser)
        response=response.replace('\r','')
        response=response.replace('\n','')
        return response

def openSerialToCardpanel():
	#ser = serial.Serial()
        ## ser.port='/dev/ttyS0'
        #ser.port='/tmp/interceptty'
        #ser.baudrate=9600
        #ser.parity=serial.PARITY_NONE
        #ser.stopbits=serial.STOPBITS_ONE
        #ser.bytesize=serial.EIGHTBITS
        #ser.open()
        #return ser
        return ""

def clearCards(ser,cardList):
        out=readSerialResponse(ser)
        #while (ser.inWaiting() > 0):
        #        out+=ser.read(1)
        for card in cardList:
     		#ser.write(" C=1 %s\r\n" % card)
		cardCommand=" C=1 %s" % card
     		print sendSerialAndGetResponse(ser,cardCommand)

def clearCard(ser,cardnum):
	out=readSerialResponse(ser)
	cardCommand=" C=1 %s" % cardnum
	print sendSerialAndGetResponse(ser,cardCommand)


def setTime(ser):
	cardCommand=" T=0 "+time.strftime("%H:%M")
        print sendSerialAndGetResponse(ser,cardCommand)

def getCardList(ser):
	out=''
	while (ser.inWaiting() > 0):
		out+=ser.read(1)

	outList=[]
	ser.write(" R=1 C\r\n")
	skipcount=0
	line=''
	m=re.compile(r'\d\d\d\d\d TZ1=\d\d\d TZ2=\d\d\d')
	while skipcount<10000:
		while (ser.inWaiting() > 0):
			chr=ser.read(1)
			line+=chr
			if (chr =="\n"):
				if (m.search(line)!=None):
					outList.append(line)
				line=''
			skipcount=0
		skipcount=skipcount+1
	return outList

def activateCard(ser,cardnum):
	commandString=" C=1 %s 1 1 1 2" % cardnum
	print sendSerialAndGetResponse(ser,commandString)
	
def openDoor(ser):
	commandString=" O=1 3 P" 
	print sendSerialAndGetResponse(ser,commandString)
	

def compileAndInstallCards(ser,memberDatabase):
	weekdaynum=datetime.datetime.today().weekday()
	today=datetime.date.today()
	todayNum=int(today.strftime('%Y%02m%02d'))
	for line in memberDatabase:
        	memNumString="%d" % line[memberSystem.DBCOL_MEMBER_NUMBER]
		# print memNumString
		rfid=line[memberSystem.DBCOL_RFID]
        	if (rfid!=""):
			if (line[memberSystem.DBCOL_PLAN] == "Associate") : continue
			daySpan=int(memberSystem.howManyDaysDue(line))
                        plan=line[memberSystem.DBCOL_PLAN]
                	if ((daySpan > 37) & (plan != "Inst (Floating Ext)")):
				print "%s  -- days due %d" % (memNumString,daySpan)
				continue
			if ((plan == "Super") | (plan == "Super (Student)") | (plan=="Inst (Fixed)") | (plan == "Super (Family)") | (plan == "Super (Student Family)") | (plan == "Super (Family Ext)") | (plan=="Comped") | (plan=="Inst (Floating)") | (plan == "Inst (Floating Ext)")):
                		commandString=" C=1 "+rfid+" 1 1 1 2"
				print sendSerialAndGetResponse(ser,commandString)
                		commandString=" C=1 "+rfid+" 1 1 1 2"
				print sendSerialAndGetResponse(ser,commandString)
                	else :
                        	commandString=" C=1 "+rfid+" 3 3 1 2"
				if (weekdaynum < 5):
                        		commandString=" C=1 "+rfid+" 2 2 1 2"
				print sendSerialAndGetResponse(ser,commandString)
                        	commandString=" C=1 "+rfid+" 3 3 1 2"
				if (weekdaynum < 5):
                        		commandString=" C=1 "+rfid+" 2 2 1 2"
				print sendSerialAndGetResponse(ser,commandString)

def buildIsPaid(memberDatabase):
  isPaid={}
  slash=re.compile(r'\/')
  dash=re.compile(r'\-')
  for memberRecord in memberDatabase:
    memberId=memberRecord[memberSystem.DBCOL_MEMBER_NUMBER]
    paidThru=slash.split(memberRecord[memberSystem.DBCOL_PAID_THRU])
    parentId=memberRecord[memberSystem.DBCOL_PARENT_MEMBER_NUMBER]
    today=datetime.datetime.now()
    paidThru=slash.split(memberRecord[memberSystem.DBCOL_PAID_THRU])
    if (len(paidThru) < 3):
      tempThru=dash.split("%s" % memberRecord[memberSystem.DBCOL_JOINED])
      if (len(paidThru) < 3):
         # print "Content-type: text/plain\n\nMember Number: %s" % memberId
         # sys.exit(0)
         tempThru=dash.split("2010-01-01")
      paidThru=(tempThru[1],tempThru[2],tempThru[0])
      
    paidThruDateTime=datetime.datetime(int(paidThru[2]),int(paidThru[0]),int(paidThru[1]))
    numDays = (today - paidThruDateTime + datetime.timedelta(-1)).days
    if (numDays < 10):
      isPaid["%s" % memberId] = 1
    else:
      isPaid["%s" % memberId] = 0
  return isPaid  

def compileCardsListForKastellan(memberDatabase):
        output="The format for this file is:\n"
        output+="\n"
        output+="   Column 1 - RFID number from card\n"
        output+="   Column 2 - Facility code from card\n"
        output+="   Column 3 - Reader Group ID \n"
        output+="              (the group id indicates which group of doors this should open)\n"
        output+="   Column 4 - Zone ID (which time zone definition applies for this card #)\n"
        output+="\n"
        output+="\n"
        output+="---begin---\n"
	for line in memberDatabase:
        	memNumString="%d" % line[memberSystem.DBCOL_MEMBER_NUMBER]
		# print memNumString
		rfid=line[memberSystem.DBCOL_RFID]
        	if (rfid!=""):
			rfidnum="%d" % int(rfid)
			if (line[memberSystem.DBCOL_PLAN] == "Associate") : continue
			daySpan=int(memberSystem.howManyDaysDue(line))
                        plan=line[memberSystem.DBCOL_PLAN]
                	if ((daySpan > 37) & (plan != "Inst (Floating Ext)")):
				# print "%s  -- days due %d" % (memNumString,daySpan)
				continue
			if ((plan == "Super") | (plan == "Super (Student)") | (plan == "Super (Student Family)") | (plan=="Inst (Fixed)") | (plan == "Super (Family)") | (plan == "Super (Family Ext)") | (plan=="Comped") | (plan=="Inst (Floating)") | (plan == "Inst (Floating Ext)") | (plan == "coworking") | (plan == "organization_1") | (plan == "organization_2") | (plan == "organization_3") | (plan == "organization_4") | (plan == "organization_5") | (plan == "spectrvm_onsite") | (plan == "spectrvm_colo") | (plan == "spectrvm_standard")):
                		commandString=rfidnum+" 88 1 1\n"
                                output=output+commandString
                	else :
				commandString=rfidnum+" 88 1 2\n"
                                output=output+commandString
				commandString=rfidnum+" 88 1 3\n"
                                output=output+commandString
				commandString=rfidnum+" 88 1 4\n"
                                output=output+commandString
	return output



def alreadySignedIn(member_id):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select * from %s where end_datetime IS NULL AND member_id=%s"%(memberSystem.MYSQL_SIGNIN_TABLE,member_id)
   cur.execute(query)
   if (cur.rowcount > 0):
	return True
   else:
	return False

def recordSignOut(member_id):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select transaction_id from %s where end_datetime IS NULL AND member_id=%s"%(memberSystem.MYSQL_SIGNIN_TABLE,member_id)
   cur.execute(query)
   rows = cur.fetchall()
   trans_id=""
   for row in rows:
        trans_id=row[0]
   end_datetime=datetime.datetime.now().strftime("%Y-%02m-%02d %H:%02m:%S")
   cur=con.cursor()
   query="update %s SET end_datetime='%s' where transaction_id=%s"%(memberSystem.MYSQL_SIGNIN_TABLE,end_datetime,trans_id)
   cur.execute(query)   

def recordSignIn(member_id,name,zip,email,subscribe):
   con=mdb.connect(memberSystem.MYSQL_HOST,memberSystem.MYSQL_USER,memberSystem.MYSQL_PASS,memberSystem.MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   if (subscribe == ""):
	subscribe="0"
   start_datetime=datetime.datetime.now().strftime("%Y-%02m-%02d %H:%02M:%S")
   query="insert into %s SET member_id=%s, name='%s', email='%s', zip='%s', start_datetime='%s', mailing_list=%s "%(memberSystem.MYSQL_SIGNIN_TABLE,member_id,name,email,zip,start_datetime,subscribe)
   cur.execute(query)
