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
import MySQLdb as mdb
import tvcogCfg as tvcog
import seltzerCfg as seltzer

MYSQL_HOST='localhost'
MYSQL_BILLING_DB = tvcog.MYSQL_DB
MYSQL_BILLING_USER = tvcog.MYSQL_USER
MYSQL_BILLING_PASS = tvcog.MYSQL_PASS
MYSQL_SUBSCRIPTION_INFO_TABLE = tvcog.MYSQL_SUBSCRIPTION_INFO_TABLE

ACTIVE_WINDOW = 3  # Number of months back from today that we should consider
		   # for this script

#braintree.Configuration.configure(
#    braintree.Environment.Sandbox,
#    "mvb2qkcvbb6fnr85",
#    "g7yn7kqsf6vxt64s",
#    "5375b0a83ea61ecd3d807e4373e70519"
#)

# print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")

members=memberSystem.loadMemberDatabase()
con=mdb.connect(MYSQL_HOST,MYSQL_BILLING_USER,MYSQL_BILLING_PASS,MYSQL_BILLING_DB)
slash=re.compile(r'\/')
dash=re.compile(r'\-')
today=datetime.date.today()
today_numeric=int(today.strftime("%Y%02m%02d"))
active_numeric = today_numeric - ACTIVE_WINDOW*100
todayYM_numeric=int(today.strftime("%Y%02m"))
endOfMonth_numeric=int(memberSystem.getEndOfThisMonthYYYYMMDD())

updateSeltzerOutput=" #   Name             Plan          Subscr  Sub Paid   Seltzer Paid\n"
manualCheckOutput=" #   Name             Plan          Subscr  Sub Paid   Seltzer Paid\n"
pastDueOutput=" #   Name             Plan          Subscr  Sub Paid   Seltzer Paid   # Months\n"
chronicPastDueOutput=" #   Name             Plan          Subscr  Sub Paid   Seltzer Paid   # Months\n"
seltzerBraintreeMatchOutput=" #   Name             Plan          Subscr  Sub Paid   Seltzer Paid\n"


with con:
	cur=con.cursor()
	cur.execute("SELECT member_id, plan_id, subscription_id from %s ORDER BY member_id" % MYSQL_SUBSCRIPTION_INFO_TABLE)
	rows = cur.fetchall()
	for row in rows:
		member_id = row[0]
		plan_id = row[1]
		subscription_id = row[2]
                memberRecord=memberSystem.findMemberRecord(members,member_id)
                memberPlan = memberRecord[memberSystem.DBCOL_PLAN]
                if ((memberPlan == "Cancelled") | (memberPlan == "Comped") | (memberPlan == "Associate")):
                    continue
		
                member_name="{} {}".format(memberRecord[memberSystem.DBCOL_FIRST_NAME],memberRecord[memberSystem.DBCOL_LAST_NAME])

                # Load the subscription information from Braintree for this
		# subscription
		subscription = braintree.Subscription.find(subscription_id)
                subscription_paid_through = subscription.paid_through_date;
                subscription_paid_numeric=0
                subscription_paid_formatted = "0000-00-00"
		try:
                  subscription_paid_formatted = "{:%Y-%m-%d}".format(subscription_paid_through)
                  subscription_paid_numeric = int("{:%Y%m%d}".format(subscription_paid_through))
 		except:
		  # In some cases, there is no payment processed under the
		  # subscription. This is usually a new membership that has
 		  # not been processed through the renewal at the beginning
		  # of the month.
		  subscription_paid_numeric=0

		# Get the current paid-through date for the account according
		# to Seltzer. In a perfect world, this is the same as above,
		# but there are scenarios where it is not, and we need to
		# take action in some cases.
                current_paid_through="0000-00-00"
                current_paid_numeric=0
                numMonthsDue=99 
		current_paidThru = slash.split(memberRecord[memberSystem.DBCOL_PAID_THRU])
		try:
                	current_paid_through = "{0:s}-{1:02d}-{2:02d}".format(current_paidThru[2],int(current_paidThru[0]),int(current_paidThru[1]))
                	current_paid_numeric = int("{0:s}{1:02d}{2:02d}".format(current_paidThru[2],int(current_paidThru[0]),int(current_paidThru[1])))
                	numMonthsDue=memberSystem.howManyMonthsDue(memberRecord) 
		except:
			current_paid_numeric=0

		# Compute a numeric month for when they joined and compare it
		# the current month. If it's the current month, then we should
		# not expect the subscription to have been processed.
		#splitJoined=dash.split(memberRecord[memberSystem.DBCOL_JOINED])
                #joined_numeric=int("{0:s}{1:02d}".format(splitJoined[0],splitJoined[1]))
		outString="{:3}: {:<15.15} ({:<10.10}) - {:7} {} {:10}".format(member_id, member_name, memberPlan, subscription_id,subscription_paid_formatted,current_paid_through)
                
		action=""		# Needed to make sure action is in scope
                if (numMonthsDue > 0):
			action="{} month(s). ".format(numMonthsDue)
                        if (endOfMonth_numeric != subscription_paid_numeric):
                           if (numMonthsDue > 2):
				chronicPastDueOutput="{}\n{} {}".format(chronicPastDueOutput,outString,action)
			   else:
				pastDueOutput="{}\n{} {}".format(pastDueOutput,outString,action)
 		else:
			action="Account Current. "
               
                if ((subscription_paid_numeric > active_numeric) | (current_paid_numeric > active_numeric)):
                	if (subscription_paid_numeric > current_paid_numeric):
				action="{}Update Seltzer Paid Thru".format(action)
			        updateSeltzerOutput="{}\n{}".format(updateSeltzerOutput,outString)
                	if (subscription_paid_numeric < current_paid_numeric):
				action="{}Manual Check Needed".format(action)
			        manualCheckOutput="{}\n{}".format(manualCheckOutput,outString)
  			if (subscription_paid_numeric == current_paid_numeric):
				action="{} Up to Date".format(action)
				seltzerBraintreeMatchOutput="{}\n{}".format(seltzerBraintreeMatchOutput,outString,action)
                
            
print "Update Seltzer Paid Thru List:\n"
print updateSeltzerOutput
print "\n\nPaid by date in Seltzer is later than in Braintree subscription, manually check:\n"
print manualCheckOutput
print "\n\nThe following subscriptions are recently past due:\n"
print pastDueOutput
print "\n\nThe following subscriptions are chronically past due:\n"
print chronicPastDueOutput

print "\n\nThe following subscriptions are in sync between Seltzer and Braintree:\n"
print seltzerBraintreeMatchOutput
   
 
