import braintree

# This is the config file for Tonic, the extension to Seltzer CRM for 
# Tech Valley Center of Gravity. There are several settings that may need
# to be customized below depending on the testing or production environment


# Set DEBUG to True if you want to use the test database for the payment code
# to braintree and work with the braintree sandbox instead of the production
# braintree gateway.

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
MYSQL_DB='billing'

if (DEBUG):
  braintreeConfig = (
    braintree.Environment.Sandbox,
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  )
  MYSQL_DB='billing_test'

# Mailchimp is used to manage the mailing list for new member notices. 
# The mailchimp API key needs to be set to point to the TVCOG account
# Please contact Tom Tongue for the current API key and list ID, or 
# if you have direct access to MailChimp, you can look up these credentials
# directly.

MAILCHIMP_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxx'
MAILCHIMP_LIST_ID = 'xxxxxxxxxx'


# Below are the MYSQL settings that do not change dependent on DEBUG MODE.
# The only one that likely needs to be adjusted is the MYSQL_PASS

MYSQL_PASS='fizzyH2O'

MYSQL_HOST='localhost'
MYSQL_USER='billing'
MYSQL_PAYMENT_TOKEN_TABLE='payment_tokens'
MYSQL_SUBSCRIPTION_INFO_TABLE='subscription_info'

TVCOG_SIGNUP_ADMIN_NOTIFICATION_LIST='treasurer@techvalleycenterofgravity.com,srp-membership@tvcog.net,ttongue@tvcog.net';


