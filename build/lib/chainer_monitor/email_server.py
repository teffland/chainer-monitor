""" A simple server to send status update emails """
import os
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage

class EmailServer(object):
    def __init__(self, email_config):
        self.email_config = email_config
        self.EMAIL_ADDRESS = email_config['FROM_UID'] + email_config['EMAIL_ORG']
        self.FROM_PWD = email_config['FROM_PWD']
        self.SMTP_SERVER = email_config['SMTP_SERVER']
        self.SMTP_PORT = email_config['SMTP_PORT']
        # IMAP_SERVER = email_config['IMAP_SERVER']

        # set up to send emails

    def connect(self):
        self.sendserver = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
        self.sendserver.ehlo()
        self.sendserver.starttls()
        self.sendserver.ehlo()
        self.sendserver.login(self.EMAIL_ADDRESS, self.FROM_PWD)

        # set up to receive emails
#         self.inbox = imaplib.IMAP4_SSL(IMAP_SERVER)
#         self.inbox.login(self.EMAIL_ADDRESS, self.FROM_PWD)
#         self.inbox.select('inbox')

    def send_email(self, to, subject, body_text):
        self.connect()
        new = MIMEMultipart("mixed")
        body = MIMEMultipart("alternative")
        body.attach( MIMEText("<html>{}</html>".format(body_text.encode('utf-8')), "html") )
        # body.attach( MIMEText("<html>reply body text</html>", "html") )
        new.attach(body)

        new["Message-ID"] = email.utils.make_msgid()
        new["Subject"] = subject
        new["To"] = to
        new["From"] = self.EMAIL_ADDRESS

        self.sendserver.sendmail(self.EMAIL_ADDRESS, [new["To"]], new.as_string())

    def quit(self):
        self.sendserver.quit()
        # self.inbox.quit()
