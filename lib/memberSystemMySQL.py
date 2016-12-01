import sys
import re
import string
import csv
import datetime
from calendar import monthrange
import smtplib
import hashlib
import random
from email.mime.text import  MIMEText
import tvcogCfg as tvcog
import seltzerCfg as seltzer
import MySQLdb as mdb

DBCOL_MEMBER_NUMBER=0
DBCOL_PARENT_MEMBER_NUMBER=1
DBCOL_RFID=2
DBCOL_FIRST_NAME=3
DBCOL_LAST_NAME=4
DBCOL_PLAN=5
DBCOL_STATUS=6
DBCOL_JOINED=9
DBCOL_PAID_THRU=10
DBCOL_ADDR_1=13
DBCOL_ADDR_2=14
DBCOL_CITY=15
DBCOL_STATE=16
DBCOL_ZIP=17
DBCOL_EMAIL=18
DBCOL_PHONE=19
DBCOL_CID=20

DISCOUNT_MEMBER_NUMBER=0
DISCOUNT_MEMBER_NAME=1
DISCOUNT_DATE=2
DISCOUNT_AMOUNT=3
DISCOUNT_DESCRIPTION=4

RATES_FULL=60
RATES_FULL_STUDENT=30
RATES_SUPER=100
RATES_SUPER_STUDENT=70
RATES_FULL_FAMILY=80
RATES_SUPER_FAMILY=120
RATES_SUPER_STUDENT_FAMILY=90
RATES_COWORKING=50

NUM_DAYS_BEFORE_PRORATE=11

MYSQL_HOST=seltzer.MYSQL_HOST
MYSQL_DB=seltzer.MYSQL_DB
MYSQL_CARDSYSTEM_DB="cardsystem"
MYSQL_WORKSPACES_TABLE="workspaces"
MYSQL_USER=seltzer.MYSQL_USER
MYSQL_PASS=seltzer.MYSQL_PASS
MYSQL_CONTACT_TABLE=seltzer.MYSQL_CONTACT_TABLE
MYSQL_DAYPASS_TABLE=seltzer.MYSQL_DAYPASS_TABLE
MYSQL_PLAN_TABLE=seltzer.MYSQL_PLAN_TABLE
MYSQL_MEMBERSHIP_TABLE=seltzer.MYSQL_MEMBERSHIP_TABLE
MYSQL_KEY_TABLE=seltzer.MYSQL_KEY_TABLE
MYSQL_SIGNIN_TABLE="signin"

def getUsername(memberRecord):
   memberNumString="%s" % memberRecord[DBCOL_MEMBER_NUMBER];
   username=memberRecord[DBCOL_FIRST_NAME][0:1]
   username=username+memberRecord[DBCOL_LAST_NAME]+memberNumString;
   pattern = re.compile('[\W_]+')
   username=pattern.sub('', username)
   pattern = re.compile('[\-]+')
   username=pattern.sub('', username)
   username=username.lower()
   return username

def getPlanIdFromPlanName(plan_name):
   if (plan_name == "Associate"):
        rate=0
   outText="associate"
   if (plan_name =="Full"):
       outText='full_membership'
   elif (plan_name =="Full (Student)"):
       outText='full_student_membership'
   elif (plan_name =="Super"):
       outText='super_user_membership'
   elif (plan_name =="Super (Student)"):
       outText='super_student_membership'
   elif (plan_name =="Full (Family)"):
       outText='full_family_membership'
   elif (plan_name =="Super (Family)"):
       outText='super_family_membership'
   elif (plan_name =="coworking"):
       outText='coworking'
   elif (plan_name =="organization_1"):
       outText='organization_1'
   elif (plan_name =="organization_2"):
       outText='organization_2'
   elif (plan_name =="organization_3"):
       outText='organization_3'
   elif (plan_name =="organization_4"):
       outText='organization_4'
   elif (plan_name =="organization_5"):
       outText='organization_5'
   elif (plan_name =="spectrvm_standard"):
       outText='spectrvm_standard'
   elif (plan_name == "spectrvm_colo"):
       outText='spectrvm_colo'
   elif (plan_name == "spectrvm_onsite"):
       outText='spectrvm_onsite'
   return outText


def getInvoiceHTML(memberRecord):
   slash=re.compile(r'\/')
   amountDue=0;
   paidThru=slash.split(memberRecord[DBCOL_PAID_THRU])
   if (balanceDue(memberRecord) !=True) :
        return """<table><tr><th>No Balance Due for this Account.</th></tr></table>"""
   pTN=int("{0:s}{1:02d}{2:02d}".format(paidThru[2],int(paidThru[0]),int(paidThru[1])))
   numMonths=howManyMonthsDue(memberRecord)
   outText=loadTemplate("templates/invoiceTable.html")
   fees=calcAmountDue(memberRecord)
   rate=getMembershipRate(memberRecord)
   proratedFee=getProratedRate(rate,int(paidThru[2]),int(paidThru[0]),int(paidThru[1]))
   fees=fees+proratedFee
   periodStart=calcBillingPeriodStart(memberRecord)
   periodEnd=calcBillingPeriodEnd(memberRecord)
   outText=outText.replace("#FEES#","$%d"%fees)
   outText=outText.replace("#MEMBERSHIP_RATE#","$%d"%rate)
   outText=outText.replace("#BILLING_PERIOD#",periodStart+" - "+periodEnd)
   adjustments=0
   # todaysDiscountFile = "/var/www/html/cardsystem/MemberDiscounts.txt"
   # discounts=loadDiscountDatabase(todaysDiscountFile)
   # memberDiscounts=getDiscountsForMember(discounts,memberRecord[DBCOL_MEMBER_NUMBER],memberRecord[DBCOL_PAID_THRU])
   for line in memberDiscounts:
       thisDiscountAmount=int(line[DISCOUNT_AMOUNT])
       adjustments=adjustments+thisDiscountAmount
       thisDiscountDescription=line[DISCOUNT_DESCRIPTION]
       replacementString="#DISCOUNTS#<br>\n                      $%d" % thisDiscountAmount
       replacementString=replacementString+"    %s" % thisDiscountDescription
       outText=outText.replace("#DISCOUNTS#",replacementString)
   amtDue="$%d" % (fees+adjustments)
   if (adjustments == 0):
        outText=outText.replace("#DISCOUNTS#","N/A")
   else:
        outText=outText.replace("#DISCOUNTS#","")
   outText=outText.replace("#CURRENTLY_DUE#",amtDue)
   return outText



def setMembershipExpirationDate(memberId,endDate):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   with con:
        cur=con.cursor()
        cur.execute("UPDATE %s AS c INNER JOIN %s AS m ON c.cid=m.cid SET m.end='%s' WHERE c.MemberNumber=%s" % (MYSQL_CONTACT_TABLE,MYSQL_MEMBERSHIP_TABLE,endDate,memberId))


def markDayPassAsUsed(qrcode):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   with con:
        cur=con.cursor()
        thisDate=datetime.datetime.now().strftime("%Y-%02m-%02d")
        cur.execute("UPDATE %s set used='%s' where guid='%s'" % (MYSQL_DAYPASS_TABLE,thisDate,qrcode))


def isDayPassUnused(qrcode):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   with con:
        cur=con.cursor()
        cur.execute("SELECT cid,guid,used from %s where guid='%s' AND used IS NULL" % (MYSQL_DAYPASS_TABLE,qrcode))
        if (cur.rowcount > 0):
            return 1
        else:
            return 0


def getPassNumMonths(qrcode):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   with con:
        cur=con.cursor()
        thisDate=datetime.datetime.now().strftime("%Y-%02m-%02d")
        cur.execute("SELECT cid,guid,used,num_months from %s where guid='%s' AND used IS NULL" % (MYSQL_DAYPASS_TABLE,qrcode))
        if (cur.rowcount > 0):
                rows = cur.fetchall()
                for row in rows:
                        cid=row[0]
                        num_months=row[3]
                        return num_months
        return 0


def getMemberRecordFromDayPass(qrcode):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   memberDatabase=loadMemberDatabase()
   with con:
        cur=con.cursor()
        thisDate=datetime.datetime.now().strftime("%Y-%02m-%02d")
        cur.execute("SELECT cid,guid,used from %s where guid='%s' AND used IS NOT NULL" % (MYSQL_DAYPASS_TABLE,qrcode))
        if (cur.rowcount > 0):
                rows = cur.fetchall()
                for row in rows:
                        cid=row[0]
                        if (("%s"%row[2]) == thisDate):
                                memberRecord=findMemberRecordFromCID(memberDatabase,cid)
                                return memberRecord
        cur.execute("SELECT cid,guid,used from %s where guid='%s' AND used IS NULL" % (MYSQL_DAYPASS_TABLE,qrcode))
        if (cur.rowcount > 0):
                rows = cur.fetchall()
                for row in rows:
                        cid=row[0]
                        memberRecord=findMemberRecordFromCID(memberDatabase,cid)
                        return memberRecord
        else:
                return emptyMemberRecord()


def getFirstAvailableDayPass(memberRecord):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   memberDatabase=loadMemberDatabase()
   plan=memberRecord[DBCOL_PLAN]
   cid=memberRecord[DBCOL_CID]
   with con:
        cur=con.cursor()
        thisDate=datetime.datetime.now().strftime("%Y-%02m-%02d")
        cur.execute("SELECT guid,used from %s where cid=%s AND used ='%s'" % (MYSQL_DAYPASS_TABLE,cid,thisDate))
        if (cur.rowcount > 0):
                rows = cur.fetchall()
                for row in rows:
                        qrcode=row[0]
                        return qrcode
        else:
                cur.execute("SELECT guid,used from %s where cid=%s AND used IS NULL" % (MYSQL_DAYPASS_TABLE,cid))
                if (cur.rowcount > 0):
                        rows = cur.fetchall()
                        for row in rows:
                            qrcode=row[0]
                            return qrcode
                else:
                        if ((plan == "Super") | (plan == "Super (Family)") | (plan == "Super (Student)")):
                            return addDayPassToCID(cid)
                        else:
                            return ''

def addDayPassToCID(cid,num_months=0):
    con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
    cur=con.cursor()
    guid=generateDayPassGUID()
    thisDate=datetime.datetime.now().strftime("%Y-%02m-%02d")
    cur.execute("INSERT INTO %s SET cid=%s, guid='%s', purchased='%s', num_months=%s" % (MYSQL_DAYPASS_TABLE,cid,guid,thisDate,num_months))
    return guid

def generateDayPassGUID():
    m=hashlib.md5()
    m.update("%f" % random.SystemRandom().random())
    hexdump=m.hexdigest().upper()
    guid = hexdump[0:8]+"-"+hexdump[8:12]+"-"+hexdump[12:16]+"-"+hexdump[16:20]+"-"+hexdump[20:32]
    return guid



def alreadyHasReservation(memberID):
   start_datetime=datetime.datetime.now().strftime("%Y-%02m-%02d %H:%02m:%S")
   end_datetime=(datetime.datetime.now()+datetime.timedelta(hours=24)).strftime("%Y-%02m-%02d %H:%02m:%S")
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="select * from %s where end_datetime>'%s' AND member_id=%s"%(MYSQL_WORKSPACES_TABLE,start_datetime,memberID)
   cur.execute(query)
   if (cur.rowcount > 0):
       return True
   else:
        return False

def reserveWorkspace(memberID):
   start_datetime=datetime.datetime.now().strftime("%Y-%02m-%02d %H:%02m:%S")
   end_datetime=(datetime.datetime.now()+datetime.timedelta(hours=24)).strftime("%Y-%02m-%02d %H:%02m:%S")
   reserveWorkspaceWithDates(memberID,start_datetime,end_datetime)

def reserveWorkspaceWithDates(memberID,start_datetime,end_datetime):
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_CARDSYSTEM_DB)
   cur=con.cursor()
   query="insert into %s SET member_id=%s, start_datetime='%s', end_datetime='%s'" % (MYSQL_WORKSPACES_TABLE,memberID,start_datetime,end_datetime)
   cur.execute(query)

def getNextMemberNumber():
    con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
    lastNumber=0;
    nextNumber=0;
    with con:
        cur=con.cursor()
        query="select memberNumber FROM %s WHERE memberNumber IS NOT NULL ORDER BY ABS(memberNumber)" % MYSQL_CONTACT_TABLE
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            if (("%s"%row[0])=="None"):
                continue
            memberNumber=int(row[0]);
            if (memberNumber == lastNumber+1):
                nextNumber=memberNumber;
                lastNumber=memberNumber;
    return nextNumber+1;


def createSeltzerContactRecords(firstName,lastName,address,city,state,zip,email,phone,over18,emergencyName,emergencyRelation,emergencyPhone,emergencyEmail, plan,organization=""):
   memberNumber="%s" % getNextMemberNumber()
   today=datetime.date.today()
   joined=today.strftime('%Y-%m-%d')
   con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   with con:
      cur=con.cursor()
      query="INSERT INTO %s (memberNumber,firstName,lastName,joined,address1,address2,city,state,zip,email,phone,over18,emergencyName,emergencyRelation,emergencyPhone,emergencyEmail,company) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%d,'%s','%s','%s','%s','%s')" % (MYSQL_CONTACT_TABLE,memberNumber,firstName,lastName,joined,address,"",city,state,zip,email,phone,over18,emergencyName,emergencyRelation,emergencyPhone,emergencyEmail,organization)
      cur.execute(query)
      cur=con.cursor()
      query="SELECT cid,memberNumber FROM %s where memberNumber='%s'" % (MYSQL_CONTACT_TABLE,memberNumber)
      cur.execute(query)
      rows = cur.fetchall()
      for row in rows:
          if (("%s"%row[0])=="None"):
              continue
          cid=int(row[0]);
      query="INSERT INTO member (cid) VALUES (%d)"%cid
      cur=con.cursor()
      cur.execute(query)
  
      pid = getPIDFromPlan(plan)
      today=datetime.date.today()
      start_date=today.strftime('%Y-%m-%d')
      query="INSERT INTO membership (cid,pid,start) VALUES (%d,%d,'%s')" % (cid,pid,start_date)
      cur=con.cursor()
      cur.execute(query)
 
      username=lastName.lower()+"%s"%memberNumber
      pattern=re.compile(r'\W+')
      username=re.sub(pattern,'',username)
      query="INSERT INTO user (cid,username) VALUES (%d,'%s')" % (cid,username)
      cur=con.cursor()
      cur.execute(query)

      query="INSERT INTO user_role (cid,rid) VALUES (%d,%d)" % (cid,2)
      cur=con.cursor()
      cur.execute(query)
      


def loadMemberDatabase():
    con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
    outList=[]
    with con:
        cur=con.cursor()
        cur.execute("SELECT memberNumber,parentNumber,firstName,lastName,joined,company,school,studentID,address1,address2,city,state,zip,email,phone,cid from %s" % MYSQL_CONTACT_TABLE)
        
        rows = cur.fetchall()
    for row in rows:
        if (("%s"%row[0])=="None"):
            continue
        memberNumber=int(row[0]);
        parentNumber=row[1];
        firstName=row[2];
        lastName=row[3];
        joined=row[4];
        company=row[5];
        school=row[6];
        studentId=row[7];
        address1=row[8];
        address2=row[9];
        city=row[10];
        state=row[11];
        zip=row[12];
        email=row[13];
        phone=row[14];
        cid=row[15];
        query="SELECT serial from %s where cid=%d" % (MYSQL_KEY_TABLE,cid)
        cur.execute(query)
        rfid=""
        if (cur.rowcount > 0):
            thisKeyRow=cur.fetchone()
            if (len(thisKeyRow) > 0):
                    rfid=thisKeyRow[0]
        cur.execute("SELECT pid,end from %s where cid=%d order by end desc" % (MYSQL_MEMBERSHIP_TABLE,cid))
        pid=1
        endDate="N/A"
        if (cur.rowcount > 0):
            thisPlanRow=cur.fetchone()
            pid=thisPlanRow[0]
            slash=re.compile(r'\-')
            endDate=thisPlanRow[1]
        else:
            print "WTF, no plan entry for cid %s / memberNumber %s\n" % (cid,memberNumber)
        endDateSplit=slash.split("%s"%endDate)
        paidThru="N/A"
        if (len(endDateSplit) == 3):
            paidThru="%s/%s/%s" % (endDateSplit[1],endDateSplit[2],endDateSplit[0])
        cur.execute("SELECT name from %s where pid=%d" % (MYSQL_PLAN_TABLE,pid))
        thisPlanRow=cur.fetchone()
        plan=thisPlanRow[0]
        status="N/A"
        if (plan != "Associate"):
            if (balanceDueFromDateAndPlan(paidThru,plan)):
                status="BALANCE DUE"
            else:
                status="PAID"
    
        outList.append(tuple([memberNumber,parentNumber,rfid,firstName,lastName,plan,status,"","",joined,paidThru,"","",address1,address2,city,state,zip,email,phone,cid]))

    return outList


def loadDiscountDatabase(filestr):
    outList=[]
    try:
        text=csv.reader(open(filestr,"r"),delimiter=',',quotechar='"')

        for args in text:
            args.reverse()
            memNumString=args.pop()
            memNumString=re.sub('\D+','',memNumString)
            if (memNumString!=""):
                args.append(int(memNumString))
                args.reverse()
                outList.append(tuple(args))
            else:
                args.append(memNumString)
                args.reverse()
      #print "skipped %s"%memNumString +args[3] + " "+ args[4] + "   "+args[DBCOL_PLAN]

        return outList
    except IOError:
        print "ERROR: Unable to load the discount database %s!!" % filestr



def processMemberRecordIntoTemplate(memberRecord,template):
    outTempl=template
    outTempl=outTempl.replace('#FIRST_NAME#',memberRecord[DBCOL_FIRST_NAME])
    outTempl=outTempl.replace('#LAST_NAME#',memberRecord[DBCOL_LAST_NAME])
    outTempl=outTempl.replace('#MEMBERSHIP_ID#','%d' % memberRecord[DBCOL_MEMBER_NUMBER])
    outTempl=outTempl.replace('#PAID_THRU#',memberRecord[DBCOL_PAID_THRU])
    outTempl=outTempl.replace('#MEMBERSHIP_STATUS#',memberRecord[DBCOL_STATUS])
    outTempl=outTempl.replace('#MEMBERSHIP_PLAN#',memberRecord[DBCOL_PLAN])
    outTempl=outTempl.replace('#STREET_ADDR1#',memberRecord[DBCOL_ADDR_1])
    outTempl=outTempl.replace('#STREET_ADDR2#',memberRecord[DBCOL_ADDR_2])
    outTempl=outTempl.replace('#CITY#',memberRecord[DBCOL_CITY])
    outTempl=outTempl.replace('#STATE#',memberRecord[DBCOL_STATE])
    outTempl=outTempl.replace('#ZIP#',memberRecord[DBCOL_ZIP])
    outTempl=outTempl.replace('#PHONE#',memberRecord[DBCOL_PHONE])
    outTempl=outTempl.replace('#EMAIL#',memberRecord[DBCOL_EMAIL])
    return outTempl



def loadTemplate(templateFileName):
    inFile=open(templateFileName,"r")
    lines=inFile.readlines()
    outTemplate=''
    for thisLine in lines:
        outTemplate+=thisLine
    return outTemplate


def getDiscountsForMember(discountDatabase,memberID,paidThru):
    discounts=[]
    slash=re.compile(r'\/')
    paidThruSplit=slash.split(paidThru)
    if (len(paidThruSplit) < 3):
        return discounts
    pTN=int("{0:s}{1:02d}{2:02d}".format(paidThruSplit[2],int(paidThruSplit[0]),int(paidThruSplit[1])))
    for line in discountDatabase:
        discDate=slash.split(line[DISCOUNT_DATE])
        ddN=int("{0:s}{1:02d}{2:02d}".format(discDate[2],int(discDate[0]),int(discDate[1])))
    if ((line[DISCOUNT_MEMBER_NUMBER]==memberID) & (ddN > pTN)):
        discounts.append(line)
    return discounts

def balanceDue(memberRecord):
    return balanceDueFromDateAndPlan("%s"%memberRecord[DBCOL_PAID_THRU],memberRecord[DBCOL_PLAN])

def balanceDueFromDateAndPlan(paidThru,plan):
    today=datetime.date.today()
    datestr=today.strftime('%Y-%02m-%02d')
    todayNum=int(today.strftime('%Y%02m%02d'))
    slash=re.compile(r'\/')
    paidThruSplit=slash.split(paidThru)
    if (plan == "Associate") :
        return False
    if ((paidThru==None) | (len(paidThruSplit)<3)):
        return False
    pTN=int("{0:s}{1:02d}{2:02d}".format(paidThruSplit[2],int(paidThruSplit[0]),int(paidThruSplit[1])))
    if (todayNum < pTN) :
        return False
    return True

def getAmountDue(memberRecord,memberDiscounts,DEBUG=False):
    numMonths=howManyMonthsDue(memberRecord)
    fees=calcAmountDue(memberRecord)
    rate=getMembershipRate(memberRecord)
    periodStart=calcBillingPeriodStart(memberRecord)
    periodEnd=calcBillingPeriodEnd(memberRecord)
    adjustments=0
    for line in memberDiscounts:
        thisDiscountAmount=int(line[DISCOUNT_AMOUNT])
        adjustments=adjustments+thisDiscountAmount

    amtDue=(fees+adjustments)
    return amtDue

def sendDueNotice(memberRecord,memberDiscounts,DEBUG=False):
    numMonths=howManyMonthsDue(memberRecord)
    outEmail=loadTemplate("templates/recentPastDueNotice.txt")
    if (numMonths > 2):
        outEmail=loadTemplate("templates/excessivePastDueNotice.txt")
    outEmail=processMemberRecordIntoTemplate(memberRecord,outEmail)
    fees=calcAmountDue(memberRecord)
    outEmail=outEmail.replace("#FEES#","$%d"%fees)
    rate=getMembershipRate(memberRecord)
    outEmail=outEmail.replace("#MEMBERSHIP_RATE#","$%d"%rate)
    periodStart=calcBillingPeriodStart(memberRecord)
    periodEnd=calcBillingPeriodEnd(memberRecord)
    outEmail=outEmail.replace("#BILLING_PERIOD#",periodStart+" - "+periodEnd) 
    rfid=memberRecord[DBCOL_RFID]
    if (rfid != ""):
        outEmail=outEmail.replace("#RFID_MESSAGE#","Please note that your RFID card\n"+"will no longer grant access to the space, but will still be useful for\n"+"logging in and using equipment.")
    else:
        outEmail=outEmail.replace("#RFID_MESSAGE#","")
    adjustments=0
    for line in memberDiscounts:
        thisDiscountAmount=int(line[DISCOUNT_AMOUNT])
        adjustments=adjustments+thisDiscountAmount
        thisDiscountDescription=line[DISCOUNT_DESCRIPTION]
        replacementString="#DISCOUNTS#\n                      $%d" % thisDiscountAmount 
        replacementString=replacementString+"    %s" % thisDiscountDescription
        outEmail=outEmail.replace("#DISCOUNTS#",replacementString)

    amtDue="$%d" % (fees+adjustments)
    if (adjustments == 0):
        outEmail=outEmail.replace("#DISCOUNTS#","N/A")
    else:
        outEmail=outEmail.replace("#DISCOUNTS#","")
    outEmail=outEmail.replace("#CURRENTLY_DUE#",amtDue)
    print outEmail
    if (DEBUG):
        print "\n\nDEBUG--------------------\n\n"
    else:
        if ((memberRecord[DBCOL_EMAIL]!="") & (memberRecord[DBCOL_MEMBER_NUMBER]>0)):
            msg=MIMEText(outEmail)
            msg['Subject']="Membership renewal for Tech Valley Center of Gravity"
            msg['From']="treasurer@techvalleycenterofgravity.com"
            msg['To']=memberRecord[DBCOL_EMAIL]
            s=smtplib.SMTP('localhost')
            s.sendmail('treasurer@techvalleycenterofgravity.com',memberRecord[DBCOL_EMAIL],msg.as_string())
            s.quit()
        else:
            print "FAIL TRAIN!!! TOOT TOOT! THIS EMAIL "+memberRecord[DBCOL_EMAIL]+" WAS REFUSED!"
        print "\n\n-------------------------\n\n"


def findMemberRecord(memberDatabase,idNum):
    for line in memberDatabase:
        if (idNum ==line[DBCOL_MEMBER_NUMBER]):
            return line
    return emptyMemberRecord()


def findMemberRecordFromCID(memberDatabase,cid):
    for line in memberDatabase:
        if (cid ==line[DBCOL_CID]):
            return line
    return emptyMemberRecord()


def emptyMemberRecord():
    line=[-1,-1,-1,'','','','','','','','','','','','','','','','','','',-1]
    return line

def calcAmountDue(memberRecord):
   # today=datetime.date.today()
   # todayNum=int(today.strftime('%Y%02m%02d'))
   # slash=re.compile(r'\/')
   # paidThru=slash.split(memberRecord[DBCOL_PAID_THRU]) 
   # pTN=int("{0:s}{1:02d}{2:02d}".format(paidThru[2],int(paidThru[0]),int(paidThru[1])))
   # dayDiff=todayNum - pTN
   rate=getMembershipRate(memberRecord)
   amountDue=0
   multiplyer=howManyMonthsDue(memberRecord)
   if (multiplyer > 3):
     multiplyer=3
   amountDue=rate*multiplyer
   return amountDue


def howManyMonthsDue(memberRecord):
   start=calcBillingPeriodStartDateTime(memberRecord)
   end=calcBillingPeriodEndDateTime(memberRecord)
   daySpan=end-start
   numMonths=(daySpan.days-(daySpan.days % 28))/28
   return numMonths

def howManyDaysDue(memberRecord):
   start=calcBillingPeriodStartDateTime(memberRecord)
   end=calcBillingPeriodEndDateTime(memberRecord)
   daySpan=end-start
   return daySpan.days

def calcBillingPeriodStart(memberRecord):
   paidThruDateTime=calcBillingPeriodStartDateTime(memberRecord)
   billStart=paidThruDateTime.strftime('%m/%d/%Y')
   return billStart

def getToday():
   today=datetime.date.today() 
   return today.strftime('%m/%d/%Y')

def getEndOfThisMonth():
   today=datetime.date.today() 
   thisYear=int(today.strftime('%Y'))
   thisMonth=int(today.strftime('%m'))
   thisDay=int(today.strftime('%d'))
   (junk,daysInMonth)=monthrange(thisYear,thisMonth) 
   endOfMonth="%d/%d/%d"%(thisMonth,daysInMonth,thisYear)
   return endOfMonth

def getEndOfThisMonthYYYYMMDD():
   today=datetime.date.today() 
   thisYear=int(today.strftime('%Y'))
   thisMonth=int(today.strftime('%m'))
   thisDay=int(today.strftime('%d'))
   (junk,daysInMonth)=monthrange(thisYear,thisMonth) 
   endOfMonth="{:04d}{:02d}{:02d}".format(thisYear,thisMonth,daysInMonth)
   return endOfMonth

def calcBillingPeriodStartDateTime(memberRecord):
   slash=re.compile(r'\/')
   today=datetime.date.today()
   todayNum=int(today.strftime('%Y%02m%02d'))
   paidThru=slash.split(memberRecord[DBCOL_PAID_THRU]) 
   if (len(paidThru) < 3):
       tempThru=dash.split("%s" % memberRecord[DBCOL_JOINED])
       paidThru=(tempThru[1],tempThru[2],tempThru[0])
   paidThruDateTime=datetime.datetime(int(paidThru[2]),int(paidThru[0]),int(paidThru[1]))
   paidThruDateTime=paidThruDateTime+datetime.timedelta(1)
   return paidThruDateTime



def calcBillingPeriodEnd(memberRecord):
   endMonth=calcBillingPeriodEndDateTime(memberRecord)
   billEnd=endMonth.strftime('%m/%d/%Y')
   return billEnd

def calcBillingPeriodEndDateTime(memberRecord):
   slash=re.compile(r'\/')
   today=datetime.date.today()+datetime.timedelta(3)
   todayNum=today.strftime('%Y/%m/%d')
   todaySplit=slash.split(todayNum)
   beginMonth=datetime.datetime(int(todaySplit[0]),int(todaySplit[1]),1)
   nextMonth=beginMonth+datetime.timedelta(38)
   nextSplit=slash.split(nextMonth.strftime('%Y/%m/%d'))
   nextBeginMonth=datetime.datetime(int(nextSplit[0]),int(nextSplit[1]),1)
   endMonth=nextBeginMonth-datetime.timedelta(1)
   return endMonth



def getMembershipRate(memberRecord):
   plan=memberRecord[DBCOL_PLAN]
   return getMembershipRateFromPlan(plan)



def getPIDFromPlan(plan):
   pid=1
   if ((plan =="Full") | (plan=="full_membership") | (plan=="full")):
       pid=3
   elif ((plan =="Full (Student)") | (plan=="full_student_membership") | (plan=="full_student")):
       pid=4
   elif ((plan =="Super") | (plan=="super_user_membership") | (plan=="super")):
       pid=2
   elif ((plan =="Super (Student)") | (plan=="super_student_membership") | (plan=="super_student")):
       pid=9
   elif ((plan =="Full (Family)") | (plan=="full_family_membership") | (plan=="full_family")):
       pid=6
   elif ((plan =="Super (Family)") | (plan=="super_family_membership") | (plan=="super_family")):
       pid=5
   elif ((plan == "coworking") | (plan == "Coworking")):
       pid=16
   elif ((plan == "spectrvm_standard") | (plan == "SPECTRVM Standard")):
       pid=17
   elif ((plan == "spectrvm_colo") | (plan == "SPECTRVM Colo")):
       pid=18
   elif ((plan == "spectrvm_onsite") | (plan == "SPECTRVM Onsite")):
       pid=19
   elif (plan == "organization_1"):
       pid=20
   elif (plan == "organization_2"):
       pid=21
   elif (plan == "organization_3"):
       pid=22
   elif (plan == "organization_4"):
       pid=23
   elif (plan == "organization_5"):
       pid=24
   else:
       pid=1
   return pid


def getMembershipRateFromPlan(plan):
   if ((plan =="Full") | (plan=="full_membership")):
       rate=RATES_FULL
   elif ((plan =="Full (Student)") | (plan=="full_student_membership")):
       rate=RATES_FULL_STUDENT
   elif ((plan =="Super") | (plan=="super_user_membership")):
       rate=RATES_SUPER
   elif ((plan =="Super (Student)") | (plan=="super_student_membership")):
       rate=RATES_SUPER_STUDENT
   elif ((plan =="Full (Family)") | (plan=="full_family_membership")):
       rate=RATES_FULL_FAMILY
   elif ((plan =="Super (Family)") | (plan=="super_family_membership")):
       rate=RATES_SUPER_FAMILY
   elif ((plan =="Super (Student Family)") | (plan=="super_student_family_membership")):
       rate=RATES_SUPER_STUDENT_FAMILY
   elif ((plan =="Coworking") | (plan == "coworking")):
       rate=RATES_COWORKING
   else:
       rate=100
   return rate


def translateEnglishPlanToDataPlan(plan):
   if (plan =="Full"):
    return "full_membership"
   elif (plan =="Full (Student)"): 
    return "full_student_membership"
   elif (plan =="Super"):
    return  "super_user_membership"
   elif (plan =="Super (Student)"):
    return "super_student_membership"
   elif (plan =="Super (Student Family)"):
    return "super_student_family_membership"
   elif (plan =="Full (Family)"):
    return "full_family_membership"
   elif (plan =="Super (Family)"):
    return "super_family_membership"
   elif (plan =="Coworking"):
    return "coworking"
   return plan
 

def getProratedRateFromToday(rate):
   today=datetime.date.today()
   thisDay=int(today.strftime('%d'))
   thisMonth=int(today.strftime('%m'))
   thisYear=int(today.strftime('%Y'))
   if (thisDay < NUM_DAYS_BEFORE_PRORATE):
        return 1*rate
   (junk,daysInMonth)=monthrange(thisYear,thisMonth)
   # Updated 11/10/16 - At Dan Falkenstrom's request (Treasurer), the signup
   # system no longer bills for the next month + the prorated amount
   # so this will only report the prorated amount, and the automated system
   # will be relied upon to bill for all future months.
   #
   # Previously we used this:
   # return rate*(1.0+((1.0*(daysInMonth-thisDay))/(1.0*daysInMonth)))
   # Now we do this:
   prorated=rate*((1.0*(daysInMonth-thisDay))/(1.0*daysInMonth))
   # It is a pain to collect less than $2, so there is a minimum charge.
   if (prorated < 2):
       prorated=2
   return prorated

 

def getProratedRate(rate, fromYear, fromMonth, fromDay):
   today=datetime.date(fromYear,fromMonth,fromDay)
   thisDay=int(today.strftime('%d'))
   thisMonth=int(today.strftime('%m'))
   thisYear=int(today.strftime('%Y'))
   if (thisDay < NUM_DAYS_BEFORE_PRORATE):
        return 1*rate
   (junk,daysInMonth)=monthrange(thisYear,thisMonth)
   #return (((daysInMonth-thisDay)/daysInMonth))*rate
   # Updated 11/10/16 - At Dan Falkenstrom's request (Treasurer), the signup
   # system no longer bills for the next month + the prorated amount
   # so this will only report the prorated amount, and the automated system
   # will be relied upon to bill for all future months.
   #
   # Previously we used this:
   # return rate*(1.0+((1.0*(daysInMonth-thisDay))/(1.0*daysInMonth)))
   # Now we do this:
   return rate*((1.0*(daysInMonth-thisDay))/(1.0*daysInMonth))


def getProratedMonthlyFeeFromToday(rate):
   today=datetime.date.today()
   thisYear=int(today.strftime('%Y'))
   thisMonth=int(today.strftime('%m'))
   thisDay=int(today.strftime('%d'))
   datestr=today.strftime('%Y-%02m-%02d')
   (junk,daysInMonth)=monthrange(thisYear,thisMonth) 
   nDays=daysInMonth-thisDay+1
   prorated=rate*nDays/daysInMonth
   return prorated
   
