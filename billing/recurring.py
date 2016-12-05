#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import braintree
#import memberSystem
import memberSystemMySQL as memberSystem
import mailsystem
import datetime
import re
import btlib
import os

#braintree.Configuration.configure(
#    braintree.Environment.Sandbox,
#    "mvb2qkcvbb6fnr85",
#    "g7yn7kqsf6vxt64s",
#    "5375b0a83ea61ecd3d807e4373e70519"
#)

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")




def buildMembershipLine(memberRecord):
   plan=memberRecord[memberSystem.DBCOL_PLAN]
   rate=memberSystem.getMembershipRate(memberRecord)
   if (plan == "Associate"):
	rate=0
   outText=plan+" ($%d / month)" % rate
   if (plan =="Full"):
       outText=outText+"<input type=hidden name=membership_level value='full_membership'>"
   elif (plan =="Full (Student)"):
       outText=outText+"<input type=hidden name=membership_level value='full_student_membership'>"
   elif (plan =="Super"):
       outText=outText+"<input type=hidden name=membership_level value='super_user_membership'>"
   elif (plan =="Super (Student)"):
       outText=outText+"<input type=hidden name=membership_level value='super_student_membership'>"
   elif (plan =="Full (Family)"):
       outText=outText+"<input type=hidden name=membership_level value='full_family_membership'>"
   elif (plan =="Super (Family)"):
       outText=outText+"<input type=hidden name=membership_level value='super_family_membership'>"
   elif (plan =="Super (Student Family)"):
       outText=outText+"<input type=hidden name=membership_level value='super_student_family_membership'>"
   elif (plan =="coworking"):
       outText=outText+"<input type=hidden name=membership_level value='coworking'>"
   elif ((plan =="spectrvm_onsite") | (plan =="spectrvm_standard") | (plan =="spectrvm_colo")):
       outText=outText+"<input type=hidden name=membership_level value='"+plan+"'>"
   return outText



def buildSelectionBoxForMemberships(memberRecord):
   # plan=memberRecord[memberSystem.DBCOL_PLAN]
   # rate=memberSystem.getMembershipRate(memberRecord)
   # if (plan == "Associate"):
# 	rate=0
   # outText=plan+" ($%d / month)" % rate
   outText="<select name=membership_level>"
   outText=outText+"<option value='full_membership'> Full Membership ($60/mo)"
   outText=outText+"<option value='full_student_membership'> Full Student Membership ($30/mo)"
   outText=outText+"<option value='super_user_membership'> Super User Membership ($100/mo)"
   outText=outText+"<option value='super_student_membership'> Super Student Membership ($70/mo)"
   outText=outText+"<option value='full_family_membership'> Full Family Membership"
   outText=outText+"<option value='super_family_membership'>Super Family Membership"
   outText=outText+"</select>"
   return outText


def isSupported(memberRecord):
   plan=memberRecord[memberSystem.DBCOL_PLAN]
   if (plan =="Associate"):
	return True 
   if (plan =="Full"):
	return True 
   elif (plan =="Full (Student)"):
	return True
   elif (plan =="Super"):
	return True
   elif (plan =="Super (Student)"):
	return True
   elif (plan =="Full (Family)"):
	return True
   elif (plan =="Super (Family)"):
	return True
   elif (plan =="spectrvm_onsite"):
	return True
   elif (plan =="spectrvm_standard"):
	return True
   elif (plan =="spectrvm_colo"):
	return True
   elif (plan =="coworking"):
	return True
   return False


def stepOneGetMemberNumber():
   outText=memberSystem.loadTemplate("templates/stepOne.html");
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Membership Subscription Setup - Step 1")
   outText=tmpheader+outText+footer
   print outText;

def stepTwoGatherInfo(memberRecord):
   template=" "
   membershipLine=" "
   if (memberRecord[memberSystem.DBCOL_PLAN]=="Associate"):
     template=memberSystem.loadTemplate("templates/stepTwoAssociate.html")
     membershipLine=buildSelectionBoxForMemberships(memberRecord)
   else:
     template=memberSystem.loadTemplate("templates/stepTwo.html")
     membershipLine=buildMembershipLine(memberRecord)
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Membership Subscription Setup - Step 2")
   outText=memberSystem.processMemberRecordIntoTemplate(memberRecord,template)
   outText=outText.replace("#MEMBERSHIP_LEVEL#",membershipLine)
   invoiceHTML=memberSystem.getInvoiceHTML(memberRecord)
   outText=outText.replace("#CURRENT_INVOICE#",invoiceHTML)
   print tmpheader+outText+footer

def stepThreeConfirmation(memberRecord):
   template=memberSystem.loadTemplate("templates/stepThree-Confirmation.html")
   outText=processFormDataIntoTemplate(template)
   inspectionResults=inspectFormInputs()
   outText=outText.replace("#FORM_PARSE_RESULTS#",inspectionResults)
   invoiceHTML=" "
   plan=cgi.escape(form.getfirst("membership_level"))
   currentMemberPlan=memberSystem.translateEnglishPlanToDataPlan(memberRecord[memberSystem.DBCOL_PLAN])
   if (currentMemberPlan!=plan):
      invoiceHTML=getProratedInvoiceHTML(plan)
   else:
      invoiceHTML=memberSystem.getInvoiceHTML(memberRecord)
   outText=outText.replace("#CURRENT_INVOICE#",invoiceHTML)
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Membership Subscription Setup - Step 3 - Confirmation")
   print tmpheader+outText+footer

def inspectFormInputs():
   result=""
   if (cgi.escape(form.getfirst("first_name","")) == ""):
     result=result+"REQUIRED: First Name<br>"
   if (cgi.escape(form.getfirst("last_name","")) == ""):
     result=result+"REQUIRED: Last Name<br>"
   if (cgi.escape(form.getfirst("zip","")) == ""):
     result=result+"REQUIRED: ZIP<br>"
   if (cgi.escape(form.getfirst("email","")) == ""):
     result=result+"REQUIRED: E-mail<br>"
   if (cgi.escape(form.getfirst("ccnum","")) == ""):
     result=result+"REQUIRED: Credit Card Number<br>"
   if (cgi.escape(form.getfirst("mm","")) == ""):
     result=result+"REQUIRED: Credit Card Expiration Month<br>"
   if (cgi.escape(form.getfirst("yyyy","")) == ""):
     result=result+"REQUIRED: Credit Card Expiration Year<br>"
   if (cgi.escape(form.getfirst("cvv","")) == ""):
     result=result+"REQUIRED: Credit Card Security Code (CVV)<br>"
   return result


def stepFourProcess(memberRecord):
   template=memberSystem.loadTemplate("templates/stepFour.html")
   results="<ul> "
   successmessage=" "
   inspectionResults=inspectFormInputs()
   if (inspectionResults!=""):
      results="Billing System purports to die of unnatural causes! Please report this error along with the following items to treasurer@techvalleycenterofgravity.com! Errors: <ul>%s" % inspectionResults
   else:
      member_id=cgi.escape(form.getfirst("member_id",""))
      first_name = cgi.escape(form.getfirst("first_name","")) 
      last_name = cgi.escape(form.getfirst("last_name","")) 
      zip = cgi.escape(form.getfirst("zip","")) 
      email = cgi.escape(form.getfirst("email","")) 
      ccnum = cgi.escape(form.getfirst("ccnum",""))
      mm = cgi.escape(form.getfirst("mm","")) 
      yyyy = cgi.escape(form.getfirst("yyyy","")) 
      cvv = cgi.escape(form.getfirst("cvv","")) 
      plan_id=cgi.escape(form.getfirst("membership_level"))
      currentMemberPlan=memberSystem.translateEnglishPlanToDataPlan(memberRecord[memberSystem.DBCOL_PLAN])
      if (btlib.customerExists(member_id)):
        results=results+"<li>"+btlib.updateCustomer(member_id,first_name, last_name, zip, ccnum, mm,yyyy,cvv)
      else:
        results=results+"<li>"+btlib.createCustomer(member_id,first_name, last_name, zip, ccnum, mm,yyyy,cvv)
        if ((memberSystem.balanceDue(memberRecord)) & (plan_id==currentMemberPlan)):
           amtDue=memberSystem.getAmountDue(memberRecord,memberDiscounts)
           results=results+"<li>"+btlib.chargeCustomer(member_id,amtDue) 
      if (plan_id!=currentMemberPlan):
	rate=memberSystem.getMembershipRateFromPlan(plan_id)
        fees=memberSystem.getProratedMonthlyFeeFromToday(rate)
        if (fees > 2):
           results=results+"<li>"+btlib.chargeCustomer(member_id,fees) 
      results=results+"<li>"+btlib.setRecurring(member_id,plan_id)
      successmessage="<p><b><u>PLEASE NOTE: Do not use the BACK button to go to the previous page! This will result in a second submission and potentially additional transactions being posted.</u></b></p>"
      
   outText=template.replace("#RESULTS#",results+"</ul> "+successmessage)
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Recurring Billing Setup - Results")
   print tmpheader
   print outText
   print footer
   additionalComments=""
   origPlanID=memberSystem.getPlanIdFromPlanName(memberRecord[memberSystem.DBCOL_PLAN])
   if (origPlanID != plan_id):
   	additionalComments="!!NOTE!! User changed their membership level from %s to %s -- Adjust records accordingly!!"% (origPlanID,plan_id)
   adminEmail=memberSystem.loadTemplate("templates/adminStepFourEmail.txt")
   adminEmail=adminEmail.replace("#RESULTS#",results)
   adminEmail=adminEmail.replace("#MEMBER_ID#",member_id)
   adminEmail=adminEmail.replace("#FIRST_NAME#",first_name)
   adminEmail=adminEmail.replace("#LAST_NAME#",last_name)
   adminEmail=adminEmail.replace("#EMAIL#",email)
   adminEmail=adminEmail.replace("#ADDITIONAL_COMMENTS#",additionalComments)
   mailsystem.sendEmail('treasurer@techvalleycenterofgravity.com','ttongue@techvalleycenterofgravity.com,ttongue@thomastongue.com','Billing System Notice - Recurring Billing setup/update',adminEmail)
   userEmail=memberSystem.loadTemplate("templates/userStepFourEmail.txt")
   userEmail=userEmail.replace("#RESULTS#",results)
   userEmail=userEmail.replace("#MEMBER_ID#",member_id)
   userEmail=userEmail.replace("#FIRST_NAME#",first_name)
   userEmail=userEmail.replace("#LAST_NAME#",last_name)
   mailsystem.sendEmail('treasurer@techvalleycenterofgravity.com',email,'TVCOG Billing System Notice - membership subscription update',userEmail)
   #mailsystem.sendEmail('treasurer@techvalleycenterofgravity.com','ttongue@techvalleycenterofgravity.com','TVCOG Billing System Notice - membership subscription update',userEmail)
   
 
def processFormDataIntoTemplate(template):
   outTempl=template
   outTempl=outTempl.replace('#MEMBERSHIP_ID#',cgi.escape(form.getfirst("member_id","")))
   outTempl=outTempl.replace('#MEMBERSHIP_LEVEL#',cgi.escape(form.getfirst("membership_level","")))
   outTempl=outTempl.replace('#FIRST_NAME#',cgi.escape(form.getfirst("first_name",memberRecord[memberSystem.DBCOL_FIRST_NAME])))
   outTempl=outTempl.replace('#LAST_NAME#',cgi.escape(form.getfirst("last_name",memberRecord[memberSystem.DBCOL_LAST_NAME])))
   outTempl=outTempl.replace('#ZIP#',cgi.escape(form.getfirst("zip",memberRecord[memberSystem.DBCOL_ZIP])))
   outTempl=outTempl.replace('#EMAIL#',cgi.escape(form.getfirst("email",memberRecord[memberSystem.DBCOL_EMAIL])))
   outTempl=outTempl.replace('#CC_NUMBER#',cgi.escape(form.getfirst("ccnum","")))
   outTempl=outTempl.replace('#CC_MM#',cgi.escape(form.getfirst("mm","")))
   outTempl=outTempl.replace('#CC_YYYY#',cgi.escape(form.getfirst("yyyy","")))
   outTempl=outTempl.replace('#CC_CVV#',cgi.escape(form.getfirst("cvv","")))
   return outTempl
 
def stepTwoNotSupported(memberRecord):
   template=memberSystem.loadTemplate("templates/stepTwoNotSupported.html")
   outText=memberSystem.processMemberRecordIntoTemplate(memberRecord,template)
   outText=outText.replace("#MEMBERSHIP_LEVEL#",buildMembershipLine(memberRecord))
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Recurring Billing Setup - Account Not Supported")
   print tmpheader+outText+footer

def stepTwoNotFound():
   template=memberSystem.loadTemplate("templates/stepTwoNotFound.html")
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG Recurring Billing Setup - Member record not found.")
   outText=tmpheader+template+footer
   print outText

# def getInvoiceHTML(memberRecord):
#    slash=re.compile(r'\/')
#    amountDue=0;
#    paidThru=slash.split(memberRecord[memberSystem.DBCOL_PAID_THRU])
#    if (memberSystem.balanceDue(memberRecord) !=True) :
# 	return """<table><tr><th>No Balance Due for this Account.</th></tr></table>"""
#    pTN=int("{0:s}{1:02d}{2:02d}".format(paidThru[2],int(paidThru[0]),int(paidThru[1])))
#    numMonths=memberSystem.howManyMonthsDue(memberRecord)
#    outText=memberSystem.loadTemplate("templates/invoiceTable.html")
#    fees=memberSystem.calcAmountDue(memberRecord)
#    rate=memberSystem.getMembershipRate(memberRecord)
#    proratedFee=memberSystem.getProratedRate(rate,int(paidThru[2]),int(paidThru[0]),int(paidThru[1]))
#    fees=fees+proratedFee
#    periodStart=memberSystem.calcBillingPeriodStart(memberRecord)
#    periodEnd=memberSystem.calcBillingPeriodEnd(memberRecord)
#    outText=outText.replace("#FEES#","$%d"%fees)
#    outText=outText.replace("#MEMBERSHIP_RATE#","$%d"%rate)
#    outText=outText.replace("#BILLING_PERIOD#",periodStart+" - "+periodEnd)
#    adjustments=0
#    for line in memberDiscounts:
#        thisDiscountAmount=int(line[memberSystem.DISCOUNT_AMOUNT])
#        adjustments=adjustments+thisDiscountAmount
#        thisDiscountDescription=line[memberSystem.DISCOUNT_DESCRIPTION]
#        replacementString="#DISCOUNTS#<br>\n                      $%d" % thisDiscountAmount
#        replacementString=replacementString+"    %s" % thisDiscountDescription
#        outText=outText.replace("#DISCOUNTS#",replacementString)
#    amtDue="$%d" % (fees+adjustments)
#    if (adjustments == 0):
#         outText=outText.replace("#DISCOUNTS#","N/A")
#    else:
#         outText=outText.replace("#DISCOUNTS#","")
#    outText=outText.replace("#CURRENTLY_DUE#",amtDue)
#    return outText

def getProratedInvoiceHTML(plan):
   outText=memberSystem.loadTemplate("templates/invoiceTableProrated.html")
   rate=memberSystem.getMembershipRateFromPlan(plan)
   fees=memberSystem.getProratedMonthlyFeeFromToday(rate)
   periodStart=memberSystem.getToday()
   periodEnd=memberSystem.getEndOfThisMonth()
   amtDue="$%d" %fees
   outText=outText.replace("#FEES#","$%d"%fees)
   outText=outText.replace("#MEMBERSHIP_RATE#","$%d"%rate)
   outText=outText.replace("#MEMBERSHIP_LEVEL#",plan)
   outText=outText.replace("#BILLING_PERIOD#",periodStart+" - "+periodEnd)
   outText=outText.replace("#DISCOUNTS#","N/A")
   outText=outText.replace("#CURRENTLY_DUE#",amtDue)
   return outText


try:
   today=datetime.date.today()
   datestr=today.strftime('%Y-%02m-%02d')
   todayNum=int(today.strftime('%Y%02m%02d'))
   todaysMemberFile = "/var/www/html/cardsystem/MemberDatabase-%s.txt" % datestr
   #todaysDiscountFile = "/var/www/html/cardsystem/MemberDiscounts-%s.txt" % datestr
   #todaysDiscountFile = "/var/www/html/cardsystem/MemberDiscounts.txt"
   members=memberSystem.loadMemberDatabase()
   discounts=memberSystem.loadDiscountDatabase()

   form = cgi.FieldStorage()
   step = form.getfirst("next_step","")
   if (step == ""):
      stepOneGetMemberNumber()
   else:
      member_id_str = form.getfirst("member_id","-1")
      member_id_str = cgi.escape(member_id_str)
      member_id=int(member_id_str)      
      memberRecord=memberSystem.findMemberRecord(members,member_id)
      if (memberRecord[memberSystem.DBCOL_ZIP]!=cgi.escape(form.getfirst("zip",""))):
	stepTwoNotFound()
        print "<!--"
        sys.exit(0)
      if (member_id == -1):
        stepOneGetMemberNumber()
      else:
        if (memberRecord[memberSystem.DBCOL_MEMBER_NUMBER]==-1):
	        stepTwoNotFound()
        else:
	   if (isSupported(memberRecord)):
                memberDiscounts=memberSystem.getDiscountsForMember(discounts,memberRecord[memberSystem.DBCOL_MEMBER_NUMBER],memberRecord[memberSystem.DBCOL_PAID_THRU])
		step=cgi.escape(form.getfirst("next_step","2"))
		if (step == "2"):
        	    stepTwoGatherInfo(memberRecord)
                else:
		    if (step == "3"):
			stepThreeConfirmation(memberRecord)
		    else:
			stepFourProcess(memberRecord)
           else:
   		stepTwoNotSupported(memberRecord)
       
except:
   cgi.print_exception()


