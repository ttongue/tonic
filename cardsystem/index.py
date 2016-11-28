#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cgi
import memberSystemMySQL as memberSystem
import datetime
import re
import os

def stepOne():
    body=memberSystem.loadTemplate("templates/frontpage.html")
    tmpheader=header
    tmpheader=tmpheader.replace("#PAGE_TITLE#","TVCOG RFID Card System")
    outText=tmpheader+body+footer
    print outText;

print("Content-type: text/html\n\n")
header=memberSystem.loadTemplate("templates/header-new.html")
footer=memberSystem.loadTemplate("templates/footer-new.html")
stepOne()
