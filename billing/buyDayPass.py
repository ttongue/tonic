#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import MySQLdb as mdb
import seltzerCfg as seltzer
import memberSystemMySQL as memberSystem
# import cardsystem as cardsystem
import datetime
import re
import os
import smtplib
import braintree
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

reload(sys)  
sys.setdefaultencoding('utf8')

DEBUG=False

if (DEBUG):
  braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="mvb2qkcvbb6fnr85",
                                  public_key="g7yn7kqsf6vxt64s",
                                  private_key="5375b0a83ea61ecd3d807e4373e70519")
else:
  braintree.Configuration.configure(braintree.Environment.Production,
                                  merchant_id="998p6ptnd7ppkg7m",
                                  public_key="v8f4hptfchw97dtk",
                                  private_key="afc4b695d4e02ec9a5f84c6ad7379d31")


def stepOne(importantMessage,importantMessageGuest):
    body=memberSystem.loadTemplate("templates/buyDayPass1.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Day Pass Order Form")
    outText=tmpheader+body+footer
    clientToken=braintree.ClientToken.generate()
    outText=outText.replace("<!--CLIENT_TOKEN-->",clientToken)
    outText=outText.replace("<!--ERROR_MESSAGE-->",importantMessage)
    outText=outText.replace("<!--ERROR_MESSAGE2-->",importantMessageGuest)
    print outText;


def handleSale(nonce,amtDue):
     result = braintree.Transaction.sale({
    		"amount": amtDue,
    		"payment_method_nonce": nonce
              })
     if result.is_success:
	return "Transaction Success!"
     return "Error: Transaction DECLINED"


print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")
try:
  form = cgi.FieldStorage()
  id=cgi.escape(form.getfirst("id",""))
  zip=cgi.escape(form.getfirst("zip",""))
  option=cgi.escape(form.getfirst("bundle",""))
  nonce=cgi.escape(form.getfirst("payment_method_nonce",""))
  step=cgi.escape(form.getfirst("step",""))
  if (step==""):
    stepOne("","")
    print "<!--"
    sys.exit(0)
  if ((id == "") | (zip =="") | (option=="") | (nonce =="")):
    stepOne("Blank Fields! Please complete all of the fields!","")
    print "<!--"
    sys.exit(0)
  members=memberSystem.loadMemberDatabase() 
  member_id=int(id)      
  name=""
  email=""
  memberRecord=memberSystem.findMemberRecord(members,member_id)
  if (memberRecord[memberSystem.DBCOL_ZIP]!=zip):
   		stepOne("No member record exists with that id and Zip code!","")
    		print "<!--"
    		sys.exit(0)
  name=memberRecord[memberSystem.DBCOL_FIRST_NAME]+" "+memberRecord[memberSystem.DBCOL_LAST_NAME]
  email=memberRecord[memberSystem.DBCOL_EMAIL]
  cid=memberRecord[memberSystem.DBCOL_CID] 
  result="Error: Option selected is NOT SUPPORTED!"
  purchase=""
  if (option=="1"):
     result = handleSale(nonce,25)
     purchase="Single Day Pass - $25"
  if (option=="3"):
     result = handleSale(nonce,50)
     purchase="Three Day Passes - $50"
  if (option=="7"):
     result = handleSale(nonce,100)
     purchase="Seven Day Pass - $100"
  if (result.find("Error:") == -1):
     num=int(option)
     for i in range(0,num):
	memberSystem.addDayPassToCID(cid)
  # cardsystem.sendQRCodeEmail(qrcode,email) 
     body=memberSystem.loadTemplate("templates/buyDayPassComplete.html")
     body=body.replace("#MEMBER_NUMBER#","%s" % member_id)
     body=body.replace("#MEMBER_NAME#",name)
     body=body.replace("#MEMBER_EMAIL#",email)
     body=body.replace("#PURCHASE#",purchase)
     tmpheader=header
     tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Day Pass Purchase Complete!")
     tmpheader=tmpheader.replace("<!--METAREFRESH-->","<META http-equiv='refresh' content='10;http://systems.techvalleycenterofgravity.com/cardsystem/buyDayPass.py'>")
     print tmpheader+body+footer
  else:
    stepOne("Day Pass Purchase Failed: %s, please try again." % result,"")
    print "<!--"
    sys.exit(0)
     
  
except:
  cgi.print_exception()
