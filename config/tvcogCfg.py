import braintree

DEBUG=False
# DEBUG=True

# Braintree credentials. TVCOG developers should contact Tom Tongue to 
# get the production and sandbox entries for our account at Braintree....
# not putting them on Github (duh!).

braintreeConfig = (
    braintree.Environment.Production,
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)
if (DEBUG):
  braintreeConfig = (
    braintree.Environment.Sandbox,
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  )
  MYSQL_DB='billing_test'

MYSQL_HOST='localhost'
MYSQL_DB='billing'
MYSQL_USER='billing'
MYSQL_PASS='fizzyH2O'
MYSQL_PAYMENT_TOKEN_TABLE='payment_tokens'
MYSQL_SUBSCRIPTION_INFO_TABLE='subscription_info'

TVCOG_SIGNUP_ADMIN_NOTIFICATION_LIST='treasurer@techvalleycenterofgravity.com,srp-membership@tvcog.net,ttongue@tvcog.net';


