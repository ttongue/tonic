import smtplib
from email.mime.text import  MIMEText

def sendEmail(fromEmail,toEmail,subject, contents):
	msg=MIMEText(contents)
        msg['Subject']=subject
        msg['From']=fromEmail
        msg['To']=toEmail
        s=smtplib.SMTP('localhost')
        s.sendmail(fromEmail,toEmail,msg.as_string())
        s.quit()
