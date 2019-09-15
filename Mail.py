import smtplib
from email.mime.text import MIMEText


class Mail :
    def __init__(self,subject,mail_ID,mail_PW, msg) :
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('mail_ID', 'mail_PW')
        message = MIMEText(msg)
        msg = MIMEText(message.as_string())
        msg['Subject'] = subject
        msg['To'] = mail_ID
        smtp.sendmail(mail_ID, mail_PW, msg.as_string())
        smtp.quit()

    def sendLog(self, log):
        lines = open(log.filename, 'r')
        msgBox = []
        for i in lines :
            msgBox.append(i)

        msg = "".join(msgBox)
        return msg
