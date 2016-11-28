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

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header.html")
footer=memberSystem.loadTemplate("templates/footer.html")
body=memberSystem.loadTemplate("templates/tos.html")
tmpheader=header
tmpheader=tmpheader.replace("#PAGE_TITLE#","Terms of Service")
outText=tmpheader+body+footer
print outText


