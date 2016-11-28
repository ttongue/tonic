#!/usr/bin/python

import sys
sys.path.append("../lib")
sys.path.append("../config")

import cardsystem
import memberSystemMySQL as memberSystem
import re
import datetime
from subprocess import call

kastellanPath="/var/www/html/kastellan"
cardlistFilename=kastellanPath+"/cardlist.txt"

today=datetime.date.today()
datestr=today.strftime('%Y-%02m-%02d')
tempfile=cardlistFilename+"."+datestr;
memberDatabase=memberSystem.loadMemberDatabase()

output=cardsystem.compileCardsListForKastellan(memberDatabase)
fo=open(tempfile,"w")
fo.write(output)
fo.close()
call("mv "+tempfile+" "+cardlistFilename,shell=True)
print output
