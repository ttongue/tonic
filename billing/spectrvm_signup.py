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
from calendar import monthrange


print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/spectrvm_header.html")
footer=memberSystem.loadTemplate("templates/spectrvm_footer.html")
errorText=""



def buildMemberFormLine(plan):
   plainTxt=getPlainTextMemberPlanDescription(plan)
   setup = getSetupFeeFromPlan(plan)
   rate = getMonthlyRateFromPlan(plan)
   line="<input type=hidden name=memberplan value='"+plan+"'>"+plainTxt+" - $"
   line=line+"%d"%(rate+setup)
   if (plan!="associate"):
        line=line+"/month"
   return line

def getSetupFeeFromPlan(plan):
   if (plan =="associate"):
	return 25
   return 0

def getMonthlyRateFromPlan(plan):
   if (plan =="associate"):
	return 0
   if (plan =="full"):
	return 60
   if (plan == "full_student"):
	return 30
   if (plan == "super"):
	return 100
   if (plan == "super_student"):
	return 70
   if (plan =="full_family"):
	return 80
   if (plan == "full_student_family"):
	return 50
   if (plan == "super_family"):
	return 120
   if (plan == "super_student_family"):
	return 90
   if (plan == "spectrvm_standard"):
	return 200
   if (plan == "spectrvm_onsite"):
	return 100
   if (plan == "spectrvm_colo"):
	return 200
   return 1000


def getPlainTextMemberPlanDescription(plan):
   if (plan =="associate"):
	return "Associate"
   if (plan =="full"):
	return "Full"
   if (plan == "full_student"):
	return "Full (Student)"
   if (plan == "super"):
	return "Super"
   if (plan == "super_student"):
	return "Super (Student)"
   if (plan =="full_family"):
	return "Full (Family)"
   if (plan == "full_student_family"):
	return "Full (Family) (Student)"
   if (plan == "super_family"):
	return "Super (Family)"
   if (plan == "super_student_family"):
	return "Super (Student) (Family)"
   if (plan == "spectrvm_standard"):
	return "SPECTRVM Standard"
   if (plan == "spectrvm_colo"):
	return "SPECTRVM Colo"
   if (plan == "spectrvm_onsite"):
	return "SPECTRVM Onsite"
   return plan
  

def getPlanFromForm():
   plan = cgi.escape(form.getfirst("memberplan",""))
   if ((plan =="associate") | (plan =="full") | (plan == "full_student") | (plan == "super") | (plan == "super_student") | (plan =="full_family") | (plan == "full_student_family") | (plan == "super_family") | (plan == "super_student_family") | (plan == "spectrvm_standard") | (plan == "spectrvm_onsite") | (plan == "spectrvm_colo")):
	return plan
   planRoot = cgi.escape(form.getfirst("plan",""))
   planFamily = cgi.escape(form.getfirst("family",""))
   planStudent = cgi.escape(form.getfirst("student",""))
   if (planRoot == ""):
	return ""
   if ((planRoot == "spectrvm_standard") | (planRoot == "spectrvm_onsite") | (planRoot == "spectrvm_colo")):
        return planRoot
   if (planRoot == "associate"):
	return "associate"
   if ((planRoot != "full") & (planRoot != "super")):
	return ""
   if ((planFamily !="") & (planFamily !="family")):
	return ""
   if ((planStudent != "") & (planStudent != "student")):
	return ""
   plan=planRoot
   if (planStudent !=""):
	plan=plan+'_'+planStudent
   if (planFamily != ""):
	plan=plan+'_'+planFamily
   return plan





def isSupported(plan):
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
   elif (plan == "SPECTRVM Standard"):
	return True
   elif (plan == "SPECTRVM Onsite"):
	return True
   elif (plan == "SPECTRVM Colo"):
	return True
   return False


def stepOneSelectPlan():
   outText=memberSystem.loadTemplate("templates/spectrvmSignup-step1.html");
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","SPECTRVM Services Provider Signup - Step 1")
   outText=tmpheader+outText+footer
   print outText;

def stepTwoGatherInfo(plan):
   template=memberSystem.loadTemplate("templates/spectrvmSignup-step2.html")
   membershipLine=buildMemberFormLine(plan)
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","SPECTRVM Services Provider Signup - Step 2")
   outText=template
   outText=outText.replace("#MEMBERSHIP_LEVEL#",membershipLine)
   outText=outText.replace("<!--ERROR_MESSAGE-->",errorText)
   outText=outText.replace("#OVER18LINE#","<input name=over18 value='no' type=radio checked>No&nbsp;&nbsp;&nbsp;<input name=over18 value='yes' type=radio>Yes")
   invoiceHTML=getInvoiceHTML(plan)
   outText=outText.replace("#CURRENT_INVOICE#",invoiceHTML)
   print tmpheader+outText+footer

def stepThreeConfirmation(plan,importantMessage):
   template=memberSystem.loadTemplate("templates/spectrvmSignup-step3.html")
   inspectionResults=inspectFormInputsForMemberInfo()
   tmpheader=header
   membershipLine=buildMemberFormLine(plan)
   template=template.replace("#MEMBERSHIP_LEVEL#",membershipLine)
   if (inspectionResults !=""):
      tmpheader=tmpheader.replace("#PAGE_TITLE#","SPECTRVM Services Provider Signup - Step 2 - TRY AGAIN - COMPLETE ALL FIELDS")
      template=memberSystem.loadTemplate("templates/spectrvmSignup-step2.html")
      template=template.replace("#MEMBERSHIP_LEVEL#",membershipLine)
      outText=processFormDataIntoTemplate(template,"value='","'")
      outText=outText.replace("<!--ERROR_MESSAGE-->",inspectionResults)
      outText=outText.replace("#FORM_PARSE_RESULTS#",inspectionResults)
   else:
      outText=processFormDataIntoTemplate(template,"","")
      if (importantMessage != ""):
	outText=outText.replace("<!--ERROR_MESSAGE-->",importantMessage)
        outText=outText.replace("#FORM_PARSE_RESULTS#",importantMessage)
      tmpheader=tmpheader.replace("#PAGE_TITLE#","SPECTRVM Services Provider Signup - Step 3 - Confirmation")
      outText=outText.replace("#FORM_PARSE_RESULTS#",inspectionResults)
   invoiceHTML=" "
   invoiceHTML=getInvoiceHTML(plan)
   outText=outText.replace("#CURRENT_INVOICE#",invoiceHTML)
   print tmpheader+outText+footer

def inspectFormInputsForMemberInfo():
   result=""
   if (cgi.escape(form.getfirst("organization","")) == ""):
     result=result+"REQUIRED: Organization<br>"
   if (cgi.escape(form.getfirst("first_name","")) == ""):
     result=result+"REQUIRED: First Name<br>"
   if (cgi.escape(form.getfirst("last_name","")) == ""):
     result=result+"REQUIRED: Last Name<br>"
   if (cgi.escape(form.getfirst("address","")) == ""):
     result=result+"REQUIRED: Address<br>"
   if (cgi.escape(form.getfirst("city","")) == ""):
     result=result+"REQUIRED: City<br>"
   if (cgi.escape(form.getfirst("state","")) == ""):
     result=result+"REQUIRED: State<br>"
   if (cgi.escape(form.getfirst("email","")) == ""):
     result=result+"REQUIRED: E-mail<br>"
   if not re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", cgi.escape(form.getfirst("email",""))):
     result=result+"INVALID E-Mail<br>"
   if (cgi.escape(form.getfirst("phone","")) == ""):
     result=result+"REQUIRED: Phone<br>"
   if (cgi.escape(form.getfirst("zip","")) == ""):
     result=result+"REQUIRED: ZIP<br>"
   #if (cgi.escape(form.getfirst("over18","")) == ""):
   #  result=result+"REQUIRED: Over 18<br>"
   if (cgi.escape(form.getfirst("emergency_contact","")) == ""):
     result=result+"REQUIRED: Emergency Contact<br>"
   if (cgi.escape(form.getfirst("emergency_relationship","")) == ""):
     result=result+"REQUIRED: Emergency Relationship<br>"
   if (cgi.escape(form.getfirst("emergency_email","")) == ""):
     result=result+"REQUIRED: Emergency Email<br>"
   if not re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", cgi.escape(form.getfirst("emergency_email",""))):
     result=result+"INVALID Emergency E-Mail<br>"
   if (cgi.escape(form.getfirst("emergency_phone","")) == ""):
     result=result+"REQUIRED: Emergency Phone<br>"
   return result

def inspectFormInputsForCreditCardInfo():
   expYYYYMM=int(datetime.datetime.now().strftime("%Y%m"))
   
   result=""
   if (cgi.escape(form.getfirst("billing_first_name","")) == ""):
     result=result+"REQUIRED: Billing First Name<br>"
   if (cgi.escape(form.getfirst("billing_last_name","")) == ""):
     result=result+"REQUIRED: Billing Last Name<br>"
   if (cgi.escape(form.getfirst("billing_zip","")) == ""):
     result=result+"REQUIRED: Billing ZIP<br>"
   if (cgi.escape(form.getfirst("billing_email","")) == ""):
     result=result+"REQUIRED: Billing E-mail<br>"
   if (cgi.escape(form.getfirst("ccnum","")) == ""):
     result=result+"REQUIRED: Credit Card Number<br>"
   if (cgi.escape(form.getfirst("mm","")) == ""):
     result=result+"REQUIRED: Credit Card Expiration Month<br>"
   if (cgi.escape(form.getfirst("yyyy","")) == ""):
     result=result+"REQUIRED: Credit Card Expiration Year<br>"
   inYYYYMM=int(cgi.escape(form.getfirst("yyyy",""))+cgi.escape(form.getfirst("mm","")))
   if (expYYYYMM > inYYYYMM):
     result=result+"ERROR: Credit Card Expiration Date Invalid!"
   if (cgi.escape(form.getfirst("cvv","")) == ""):
     result=result+"REQUIRED: Credit Card Security Code (CVV)<br>"
   return result


def stepFourProcess(plan):
   template=memberSystem.loadTemplate("templates/spectrvmSignup-step4.html")
   results="<ul> "
   successmessage=" "
   inspectionResults=inspectFormInputsForMemberInfo()
   inspectionResults=inspectionResults+inspectFormInputsForCreditCardInfo()
   if (inspectionResults!=""):
      stepThreeConfirmation(plan,inspectionResults)
      sys.exit(0)
   else:
      # member_id=cgi.escape(form.getfirst("member_id",""))
      member_id="%s" % memberSystem.getNextMemberNumber()
      organization = cgi.escape(form.getfirst("organization","")) 
      first_name = cgi.escape(form.getfirst("first_name","")) 
      last_name = cgi.escape(form.getfirst("last_name","")) 
      address = cgi.escape(form.getfirst("address",""))
      city = cgi.escape(form.getfirst("city",""))
      state = cgi.escape(form.getfirst("state",""))
      zip = cgi.escape(form.getfirst("zip","")) 
      email = cgi.escape(form.getfirst("email","")) 
      phone = cgi.escape(form.getfirst("phone",""))
      #o18 = cgi.escape(form.getfirst("over18",""))
      #over18=0
      #if (o18=="yes"):
      #	over18=1
      over18=1
      emergency_contact = cgi.escape(form.getfirst("emergency_contact",""))
      emergency_relationship = cgi.escape(form.getfirst("emergency_relationship",""))
      emergency_email = cgi.escape(form.getfirst("emergency_email",""))
      emergency_phone = cgi.escape(form.getfirst("emergency_phone",""))
      ccnum = cgi.escape(form.getfirst("ccnum",""))
      mm = cgi.escape(form.getfirst("mm","")) 
      yyyy = cgi.escape(form.getfirst("yyyy","")) 
      cvv = cgi.escape(form.getfirst("cvv","")) 
      plan=cgi.escape(form.getfirst("memberplan",""))
      amtDue=int(getInvoiceAmtDue(plan))
      plan_id=memberSystem.getPlanIdFromPlanName(plan)
      transactionOutput=""
      if (btlib.customerExists(member_id)):
        results=results+"<li>"+btlib.updateCustomer(member_id,first_name, last_name, zip, ccnum, mm,yyyy,cvv)
        results=results+"<li>"+btlib.setRecurring(member_id,plan_id)
      else:
        results=results+"<li>"+btlib.createCustomer(member_id,first_name, last_name, zip, ccnum, mm,yyyy,cvv)
	today=datetime.date.today()
	thisDay=int(today.strftime('%d'))
        if (plan_id == "associate"):
        	transactionOutput=btlib.chargeCustomer(member_id,amtDue) 
        	results=results+"<li>"+ transactionOutput
	else:
	   if (thisDay == 1):
		results=results+"<li>Attempting to create subscription and charge $%d to the card provided."%amtDue
	   else:
        	transactionOutput=btlib.chargeCustomer(member_id,amtDue) 
        	results=results+"<li>"+ transactionOutput
      	   results=results+"<li>"+btlib.setRecurring(member_id,plan_id)

      successmessage=""
      if (results.find("Error:") == -1):
           memberSystem.createSeltzerContactRecords(first_name,last_name,address,city,state,zip,email,phone,over18,emergency_contact,emergency_relationship,emergency_phone,emergency_email,plan)
           successmessage="<p class=error><b><u>PLEASE NOTE: Do not use the BACK button to go to the previous page! This will result in a second submission and potentially additional transactions being posted.</u></b></p>"
      else:
           successmessage="<p class=error><b><u>MEMBERSHIP SIGNUP FAILED</b></u> -- Please note the errors above in the signup process and go back and make the necessary corrections.</p>"
      
   outText=template.replace("#RESULTS#",results+"</ul> "+successmessage)
   tmpheader=header
   tmpheader=tmpheader.replace("#PAGE_TITLE#","SPECTRVM Service Provider Signup - Results")
   print tmpheader
   print outText
   print footer
   additionalComments=""
   adminEmail=memberSystem.loadTemplate("templates/spectrvmStepFourEmail.txt")
   adminEmail=adminEmail.replace("#RESULTS#",results)
   adminEmail=adminEmail.replace("<li>","\n   ---")
   adminEmail=adminEmail.replace("<ul>","")
   adminEmail=adminEmail.replace("</ul>","\n")
   adminEmail=adminEmail.replace("#MEMBER_ID#",member_id)
   adminEmail=adminEmail.replace("#ORGANIZATION#",organization)
   adminEmail=adminEmail.replace("#FIRST_NAME#",first_name)
   adminEmail=adminEmail.replace("#LAST_NAME#",last_name)
   adminEmail=adminEmail.replace("#EMAIL#",email)
   adminEmail=adminEmail.replace("#ADDITIONAL_COMMENTS#",additionalComments)
   mailsystem.sendEmail('treasurer@techvalleycenterofgravity.com','ttongue@techvalleycenterofgravity.com,ttongue@thomastongue.com','SPECTRVM Provider Signup System Notice: %s %s'%(first_name,last_name),adminEmail)
   if (results.find("Error:") == -1):
       userEmail=memberSystem.loadTemplate("templates/spectrvmSignupEmail.txt")
       userEmail=userEmail.replace("#RESULTS#",results)
       userEmail=userEmail.replace("<li>","\n   ---")
       userEmail=userEmail.replace("<ul>","")
       userEmail=userEmail.replace("</ul>","\n")
       userEmail=userEmail.replace("#MEMBER_ID#",member_id)
       userEmail=userEmail.replace("#ORGANIZATION#",organization)
       userEmail=userEmail.replace("#FIRST_NAME#",first_name)
       userEmail=userEmail.replace("#LAST_NAME#",last_name)
       mailsystem.sendEmail('treasurer@techvalleycenterofgravity.com',email,'SPECTRVM Provider Notice - Membership Signup complete for %s'% organization,userEmail)
   
 
def processFormDataIntoTemplate(template,stump,tail):
   slash=re.compile(r'\/')
   outTempl=template
   outTempl=outTempl.replace('#MEMBERSHIP_LEVEL#',stump+cgi.escape(form.getfirst("memberplan",""))+tail)
   outTempl=outTempl.replace('#ORGANIZATION#',stump+cgi.escape(form.getfirst("organization",""))+tail)
   outTempl=outTempl.replace('#FIRST_NAME#',stump+cgi.escape(form.getfirst("first_name",""))+tail)
   outTempl=outTempl.replace('#LAST_NAME#',stump+cgi.escape(form.getfirst("last_name",""))+tail)
   outTempl=outTempl.replace('#ADDRESS#',stump+cgi.escape(form.getfirst("address",""))+tail)
   outTempl=outTempl.replace('#CITY#',stump+cgi.escape(form.getfirst("city",""))+tail)
   outTempl=outTempl.replace('#STATE#',stump+cgi.escape(form.getfirst("state",""))+tail)
   outTempl=outTempl.replace('#ZIP#',stump+cgi.escape(form.getfirst("zip",""))+tail)
   outTempl=outTempl.replace('#EMAIL#',stump+cgi.escape(form.getfirst("email",""))+tail)
   outTempl=outTempl.replace('#PHONE#',stump+cgi.escape(form.getfirst("phone",""))+tail)
   if (cgi.escape(form.getfirst("over18"),"") == "yes"):
      outTempl=outTempl.replace('#OVER18LINE#',"<input name=over18 value='no' type=radio>No&nbsp;&nbsp;&nbsp;<input name=over18 value='yes' type=radio checked>Yes")
   else:
      outTempl=outTempl.replace('#OVER18LINE#',"<input name=over18 value='no' type=radio checked>No&nbsp;&nbsp;&nbsp;<input name=over18 value='yes' type=radio>Yes")
   outTempl=outTempl.replace('#OVER18#',stump+cgi.escape(form.getfirst("over18",""))+tail)
   outTempl=outTempl.replace('#EMERGENCY_CONTACT#',stump+cgi.escape(form.getfirst("emergency_contact",""))+tail)
   outTempl=outTempl.replace('#EMERGENCY_RELATIONSHIP#',stump+cgi.escape(form.getfirst("emergency_relationship",""))+tail)
   outTempl=outTempl.replace('#EMERGENCY_EMAIL#',stump+cgi.escape(form.getfirst("emergency_email",""))+tail)
   outTempl=outTempl.replace('#EMERGENCY_PHONE#',stump+cgi.escape(form.getfirst("emergency_phone",""))+tail)
   outTempl=outTempl.replace('#CC_NUMBER#',stump+cgi.escape(form.getfirst("ccnum",""))+tail)
   outTempl=outTempl.replace('#CC_MM#',stump+cgi.escape(form.getfirst("mm",""))+tail)
   outTempl=outTempl.replace('#CC_YYYY#',stump+cgi.escape(form.getfirst("yyyy",""))+tail)
   outTempl=outTempl.replace('#CC_CVV#',stump+cgi.escape(form.getfirst("cvv",""))+tail)
   outTempl=outTempl.replace('#BILLING_FIRST_NAME#',stump+cgi.escape(form.getfirst("billing_first_name",""))+tail)
   outTempl=outTempl.replace('#BILLING_LAST_NAME#',stump+cgi.escape(form.getfirst("billing_last_name",""))+tail)
   outTempl=outTempl.replace('#BILLING_ZIP#',stump+cgi.escape(form.getfirst("billing_zip",""))+tail)
   outTempl=outTempl.replace('#BILLING_EMAIL#',stump+cgi.escape(form.getfirst("billing_email",""))+tail)
   return outTempl
 

def getStartDate():
   today=datetime.date.today()
   return today.strftime('%m/%d/%Y')

def getEndDate():
   today=datetime.date.today()
   thisDay=int(today.strftime('%d'))
   thisMonth=int(today.strftime('%m'))
   thisYear=int(today.strftime('%Y')) 
   if (thisDay > 10):
     thisMonth=thisMonth+1
     if (thisMonth>12):
	thisMonth=1
        thisYear=thisYear+1
   (junk,daysInMonth)=monthrange(thisYear,thisMonth)
   endOfMonth="%d/%d/%d"%(thisMonth,daysInMonth,thisYear)
   return endOfMonth

def getInvoiceHTML(plan):
   slash=re.compile(r'\/')
   outText=memberSystem.loadTemplate("templates/memberSignup-invoiceTable.html")
   setup = getSetupFeeFromPlan(plan)
   rate = getMonthlyRateFromPlan(plan)
   periodStart=getStartDate()
   periodEnd=getEndDate()
   proratedFee = memberSystem.getProratedRateFromToday(rate)
   outText=outText.replace("#SETUP#","$%d"%setup)
   outText=outText.replace("#RATE#","$%d"%rate)
   outText=outText.replace("#BILLING_PERIOD#",periodStart+" - "+periodEnd)
   outText=outText.replace("#CURRENTLY_DUE#","$%d"%(proratedFee+setup))
   return outText

def getInvoiceAmtDue(plan):
   setup = getSetupFeeFromPlan(plan)
   rate = getMonthlyRateFromPlan(plan)
   proratedFee = memberSystem.getProratedRateFromToday(rate)
   return proratedFee+setup



try:
   today=datetime.date.today()
   datestr=today.strftime('%Y-%02m-%02d')
   todayNum=int(today.strftime('%Y%02m%02d'))
   members=memberSystem.loadMemberDatabase()

   form = cgi.FieldStorage()
   step = form.getfirst("next_step","")
   if (step == ""):
      stepOneSelectPlan()
   else:
      memberplan = getPlanFromForm();
      if (memberplan==""):
	stepOneSelectPlan()
        print "<!--"
        sys.exit(0)

      step=cgi.escape(form.getfirst("next_step","2"))
      if (step == "2"):
            stepTwoGatherInfo(memberplan)
      else:
	    if (step == "3"):
		stepThreeConfirmation(memberplan,"")
	    else:
		stepFourProcess(memberplan)
       
except:
   cgi.print_exception()


