import braintree
import tvcogCfg as tvcog
import MySQLdb as mdb
import sys


braintree.Configuration.configure(tvcog.braintreeConfig[0],tvcog.braintreeConfig[1],tvcog.braintreeConfig[2],tvcog.braintreeConfig[3])

MYSQL_HOST=tvcog.MYSQL_HOST
MYSQL_DB=tvcog.MYSQL_DB
MYSQL_USER=tvcog.MYSQL_USER
MYSQL_PASS=tvcog.MYSQL_PASS
MYSQL_PAYMENT_TOKEN_TABLE=tvcog.MYSQL_PAYMENT_TOKEN_TABLE
MYSQL_SUBSCRIPTION_INFO_TABLE=tvcog.MYSQL_SUBSCRIPTION_INFO_TABLE

def customerExists(id):
    try:
        customer=braintree.Customer.find(id)
        return True
    except braintree.exceptions.not_found_error.NotFoundError:
	return False

    

def createCustomer(id,first_name,last_name,cc_postal_code,cc_number, cc_expmonth, cc_expyear, cc_cvv):
    outText="";
    result = braintree.Customer.create({
	"id": id,
        "first_name": first_name,
        "last_name": last_name,
        "credit_card": {
            "billing_address": {
                "postal_code": cc_postal_code
            },
            "number": cc_number,
            "expiration_month": cc_expmonth,
            "expiration_year": cc_expyear,
            "cvv": cc_cvv
        }
    })
    if result.is_success:
        outText=outText+"""Member record for %s %s created with member id#: %s.""" % (result.customer.first_name, result.customer.last_name, result.customer.id)
	con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
	with con:
		cur=con.cursor()
		cur.execute("INSERT INTO %s SET member_id=%s, payment_token='%s' ON DUPLICATE KEY UPDATE payment_token='%s'" % (MYSQL_PAYMENT_TOKEN_TABLE,id,result.customer.credit_cards[0].token,result.customer.credit_cards[0].token));
	con.close()
    else:
        outText=outText+ "Error: {0}".format(result.message)
    return outText


def updateCustomer(id,first_name,last_name,cc_postal_code,cc_number, cc_expmonth, cc_expyear, cc_cvv):
    outText=""
    customer=braintree.Customer.find(id)
    payment_token=customer.credit_cards[0].token  
    result = braintree.Customer.update(id,{
        "first_name": first_name,
        "last_name": last_name,
        "credit_card": {
            "billing_address": {
                "postal_code": cc_postal_code
            },
            "number": cc_number,
            "expiration_month": cc_expmonth,
            "expiration_year": cc_expyear,
            "cvv": cc_cvv,
	    "options": {
		"update_existing_token": payment_token
	    }
        }
    })
    if result.is_success:
        outText=outText+"""Member record for %s %s under member id#: %s has been updated.""" % (result.customer.first_name, result.customer.last_name, result.customer.id)
	con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
	with con:
		cur=con.cursor()
		cur.execute("INSERT INTO %s SET member_id=%s, payment_token='%s' ON DUPLICATE KEY UPDATE payment_token='%s'" % (MYSQL_PAYMENT_TOKEN_TABLE,id,result.customer.credit_cards[0].token,result.customer.credit_cards[0].token));
	con.close()
    else:
        outText=outText+"Error: {0}".format(result.message)
    return outText


def chargeCustomer(id, amount):
        outText=""
	con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
	with con:	
		cur=con.cursor()
		cur.execute("SELECT member_id,payment_token FROM %s WHERE member_id=%s" % (MYSQL_PAYMENT_TOKEN_TABLE,id))
		thisRow = cur.fetchone()
                member_id=thisRow[0]
		payment_token=thisRow[1]
		result = braintree.Transaction.sale({
			"customer_id": id,
			"payment_method_token": payment_token,
 			"amount": amount,
			"options": {
        			"submit_for_settlement": True
    			}
		})
        	if result.is_success:
			outText=outText+"""Member #%s has been charged $%s to the credit card currently on file. """ % (id,amount)
		else:
			outText=outText+"Error: {0}".format(result.message)
	con.close()
        return outText


def setRecurring(id,plan_id):
       outText=" "
       con=mdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASS,MYSQL_DB)
       with con:
                cur=con.cursor()
                cur.execute("SELECT member_id,payment_token FROM %s WHERE member_id=%s" % (MYSQL_PAYMENT_TOKEN_TABLE,id))
                thisRow = cur.fetchone()
                member_id=thisRow[0]
                payment_token=thisRow[1]
                cur.execute("SELECT member_id,plan_id,subscription_id FROM %s WHERE member_id=%s" % (MYSQL_SUBSCRIPTION_INFO_TABLE,id))
                if (cur.rowcount == 0):
		   result = braintree.Subscription.create({
			"payment_method_token": payment_token,
 			"plan_id": plan_id
		   })
        	   if result.is_success:
		        subscription_id=result.subscription.id
			cur.execute("INSERT INTO %s SET member_id=%s, plan_id='%s', subscription_id='%s' ON DUPLICATE KEY UPDATE plan_id='%s', subscription_id='%s' " % (MYSQL_SUBSCRIPTION_INFO_TABLE,id,plan_id,subscription_id,plan_id,subscription_id))
			outText=outText+"""Member #%s  has been subscribed to %s and will be billed on a monthly basis starting at the beginning of next month. """ % (id,plan_id)
		   else:
			outText=outText+ "Error: {0}".format(result.message)
                else:
		   row=cur.fetchone()
		   subscription_id=row[2]
                   result = braintree.Subscription.update(subscription_id, {
			"price": "100.00",
			"payment_method_token": payment_token,
			"plan_id": plan_id,
			"options": {
				"prorate_charges": True
			}
		   })
		   if result.is_success:
			outText=outText+ """The subscription for member #%s has been updated to %s. """ % (id,plan_id)
		   else:
			outText=outText+ "Error: {0}".format(result.message)
       return outText

