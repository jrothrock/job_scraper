from __future__ import print_function
import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import yaml
import pandas as pd
from StyleFrame import StyleFrame
import re
import glob
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email import encoders

class Emailer(object):
    def __init__(self):
        self.resume = False
        self.validateEmail = False
        self.companies = []
        self.people = []
        self.templates = []
        self.template = None
        self.emailStr = None
        self.subjectLine = None
        self.onlyValid = False
        self.scopes = 'https://www.googleapis.com/auth/gmail.send'
        self.checkIsNumber = re.compile('^[0-9]+$')
        self.client_secret_file = 'client_secret.json'
        self.application_name = 'Send Jobs'
        if os.path.exists('./utils/files.yml') == True:
            with open(r'./utils/files.yml') as file:
                self.path = yaml.full_load(file)
        else:
            self.path = {}

        if os.path.exists('./utils/personal.yml') == True:
            with open(r'./utils/personal.yml') as file:
                self.info = yaml.full_load(file)
        else:
            self.info = {}


    def begin(self):
        print("\n\n//////")
        print("Email Sender")
        print("//////")

        print("\nBefore we can continue, have you gone into the scraped_jobs.xlsx and marked the jobs you want to email (by putting a Y in the \"Would you like to email?\" columns)\nSee 5:18, in the video (https://www.youtube.com/watch?v=RvCyLQK7VMo) for more information.")
        
        if self.validate() == False:
            return self

        while True:
            if self.getCompanies() == False:
                print("\nHmm. We weren't able to find any companies in the sheet that were marked (y) in the \"Would you like to email?\" column, that weren't already emailed.\nWould you like to try again?")
                if self.validate() == False:
                    return self
            else:
                break

        print("\nHave you placed your Gmail credentials.json in the files path?\nSee 6:01, in the video (https://www.youtube.com/watch?v=RvCyLQK7VMo) for more information on how to obtain this.")
        if self.validate() == False:
            return self
        else:
            while True:
                if os.path.exists(self.path['path'] + '/emails/files/credentials.json') == False:
                    print("\nHmm. We weren't able to find your credentials. We looked in this path: " + self.path['path'] + '/emails/files/credentials.json\nGo to this link to download the credentials: https://developers.google.com/gmail/api/quickstart/python and click "Enable the Gmail API"\n' + "Would you like to try again?")
                    if self.validate() == False:
                        return self
                else:
                    break

        print("\nWould you like to include your resume? We will look for you resume within the JobScraper -> emails -> files folder with the name: \"" + self.info["first"] + " " + self.info["last"] + "'s Resume.pdf\"")
        if self.validate() == True:
            while True:
                if os.path.exists(self.path['path'].strip() + '/emails/files/' + self.info["first"].strip() + ' ' + self.info["last"].strip() + '\'s Resume.pdf') == False:
                    print("\nHmm. We weren't able to your resume. We looked in this path: " + self.path['path'] + '/emails/files/' + self.info["first"] + ' ' + self.info["last"] + '\'s Resume.pdf.' + " Would you like to try again?")
                    if self.validate() == False:
                        return self
                else:
                    self.resume = True
                    break
        
        print("\nWould you like to email only verified emails?")
        if self.validate() == True:
            self.onlyValid = True
        else:
            self.onlyValid = False
        
        print("\nWould you like to do a simple verification/preview [Y or N] before each email is sent? (Highly Recommended)")
        if self.validate() == True:
            self.validateEmail = True
        try:
            self.emailCompanies()
        except Exception as e:
            print(e)
        
    
    def emailCompanies(self):
        for index, company in self.companies.iterrows():
            if self.getPeople(company["Company"]) == False:
                print("\nHmm. We weren't able to find any people in scraped_emails.xlsx that match the company's names. Are you sure there were people scraped? (If you enter N, we will move on to the next company)")
                if self.validate() == False:
                    break

            self.getEmailTemplates()
            while True:
                if len(self.templates) > 0:
                    print("\nWhich email template would you like to use?")
                    print("Options:")
                    for index, item in enumerate(self.templates):
                        print(" "+ str(index+1) + " " + item.split('/')[-1])
                    option = input("Enter number: ")
                    if self.checkIsNumber.match(option) != None:
                        ind = int(option) - 1
                        try:
                            self.template = self.templates[ind]
                            break
                        except:
                            print("Enter a valid option")
                    else:
                        print("Enter a number")
                else:
                    print("Hmm. Wasn't able to find any email templates (ending with .jset) in JobScraper -> emails -> email_templates folder.\nWould you like to double check?")
                    if self.validate() == False:
                        return self
                
            while True:
                if len(self.templates) > 0:
                    print("\nWhich subect line would you like to use?\nOptions:")
                    print(" 1. " + self.info["first"] + " " + self.info["last"] + "'s Resume - " + company["Title"])
                    print(" 2. Resume - " + company["Title"])
                    print(" 3. " + self.info["first"] + " " + self.info["last"] + "'s Application For " + company["Title"])
                    option = input("Enter number: ")
                    if self.checkIsNumber.match(option) != None:
                        self.subjectLine = int(option)
                        break
                    else:
                        print("Enter a number")
            
            
            validated = False
            for index, person in self.people.iterrows():
                while True:
                    self.getEmailStr(person)
                    if self.validateEmail == True and validated == False:
                        print('\n----')
                        print(self.emailStr)
                        print('----\n')
                        print("\nDoes this look okay?")
                        if self.validate() == False:
                           return self
                        validated = True
                    self.Send(person, company)
                    self.notePerson(person)
                    break
            
            self.noteCompany(company)
        


    def get_credentials(self):
        credential_path = self.path['path'] + '/emails/files/credentials.json'
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.path['path'] + '/emails/files/token.pickle'):
            with open(self.path['path'] + '/emails/files/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.path['path'] + '/emails/files/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.path['path'] + '/emails/files/token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    def SendMessage(self, sender, to, bcc, subject, msgHtml, msgPlain, attachmentFile=None):
        credentials = self.get_credentials()
        service = discovery.build('gmail', 'v1', credentials=credentials)
        if attachmentFile:
            message1 = self.CreateMessageWithAttachment(sender, to, bcc, subject, msgHtml, msgPlain, attachmentFile)
        else: 
            message1 = self.CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain)
        
        result = self.SendMessageInternal(service, "me", message1)
        return result
    
    def SendMessageInternal(self, service, user_id, message):
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())
            print('Message Id: %s' % message['id'])
            return True
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            return False
        return "OK"

    def CreateMessageHtml(self, sender, to, bcc, subject, msgHtml, msgPlain):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg['BCC'] = bcc
        msg.attach(MIMEText(msgPlain, 'plain'))
        msg.attach(MIMEText(msgHtml, 'html'))
        return {'raw': base64.urlsafe_b64encode(msg.as_string())}

    def CreateMessageWithAttachment(self, sender, to, bcc, subject, msgHtml, msgPlain, attachmentFile):
        """Create a message for an email.
        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        msgHtml: Html message to be sent
        msgPlain: Alternative plain text message for older email clients          
        attachmentFile: The path to the file to be attached.
        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEMultipart('mixed')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message['BCC'] = bcc
        messageA = MIMEMultipart('alternative')
        messageR = MIMEMultipart('related')

        messageR.attach(MIMEText(msgHtml, 'html'))
        messageA.attach(MIMEText(msgPlain, 'plain'))
        messageA.attach(messageR)

        message.attach(messageA)

        print("create_message_with_attachment: file: %s" % attachmentFile)
        content_type, encoding = mimetypes.guess_type(attachmentFile)
        
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(attachmentFile, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(attachmentFile, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(attachmentFile, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(attachmentFile, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            fp.close()
        filename = os.path.basename(attachmentFile)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string().encode('UTF-8')).decode('ascii')}


    def getSubjectLine(self, company):
        if self.subjectLine == 1:
            return self.info["first"] + " " + self.info["last"] + "'s Resume - " + company["Title"]
        elif self.subjectLine == 2:
            return "Resume - " + company["Title"]
        else:
            return self.info["first"] + " " + self.info["last"] + "'s Application For " + company["Title"]

    def Send(self, person, company):
        try:
            to = person['Email']
            bcc = ""
            sender = self.info['email']
            subject = self.getSubjectLine(company)
            msgHtml = self.emailStr
            msgPlain = self.emailStr
            if self.resume == True:
                resume = self.path['path'] + '/emails/files/' + self.info["first"] + ' ' + self.info["last"] + '\'s Resume.pdf'
            else:
                resume = None
            return self.SendMessage(sender, to, bcc, subject, msgHtml, msgPlain, resume)
        except Exception as ex:
            print(ex)

    def getEmailStr(self, person):
        if self.template:
            with open(self.template) as file:
                text = file.read()
                self.emailStr = text.replace('{company}', person['Company']).replace('{recipientFirst}', person["Name"].split(' ')[0]).replace('{first}', self.info["first"]).replace('{last}', self.info["last"]).replace('{recipientLast}', person["Name"].split(' ')[-1]).replace('{title}', person["Title"]).replace("{website}", person["Site"])
        else:
            raise ValueError('Couldn\'t find email template')
    
    def getEmailTemplates(self):
        if "path" in self.path:
            self.templates = glob.glob(self.path["path"] + "/emails/email_templates/*.jset")
        else: 
            raise ValueError('Couldn\'t find the path file')

    def getCompanies(self):
        if "path" in self.path:
            try:
                df = pd.read_excel(self.path['path'] + '/jobs/scraped_jobs.xlsx', index=False)
                self.companies = df.loc[((df["Would you like to email?"] == "y") |  (df["Would you like to email?"] == "Y")) & ((df['Have Emailed'] != "y") | (df['Have Emailed'] != "Y"))]
                if len(self.companies) > 0:
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                print("Hmm. Did you change any column names in the Excel sheet?")
                raise ValueError('Something happened with pandas')
        else:
            raise ValueError('Couldn\'t find the path file')
    
    def getPeople(self, company):
        if "path" in self.path:
            try:
                df = pd.read_excel(self.path['path'] + '/emails/scraped_emails.xlsx', index=False)
                if self.onlyValid == True:
                    people = df.loc[(df["Company"] == company ) & ((df['Have Emailed'] != "y") | (df['Have Emailed'] != "Y")) & ((df['Verified'] != "y") | (df['Verified'] != "Y"))]
                else:
                    people = df.loc[(df["Company"] == company ) & ((df['Have Emailed'] != "y") | (df['Have Emailed'] != "Y"))]
                if len(people) > 0:
                    if len(self.people) > 0:
                        self.people = pd.concat([self.people, people])
                    else:
                        self.people = people
                if len(self.people) > 0:
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                print("Hmm. Did you change any column names in the Excel sheet?")
                raise ValueError('Something happened with pandas')
        else:
            raise ValueError('Couldn\'t find the path file')
    
    def notePerson(self, person):
        if "path" in self.path:
            df = pd.read_excel(self.path['path'] + '/emails/scraped_emails.xlsx', index=False)
            df.loc[(df["Email"] == person["Email"], "Have Emailed")] = ["Y"]
            excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/emails/scraped_emails.xlsx')
            sf = StyleFrame(df)
            sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Name','Email', 'Title', 'Company', 'Site', 'Verified'))
            excel_writer.save()
        else:
            raise ValueError('Couldn\'t find the path file')

    def noteCompany(self, company):
        if "path" in self.path:
            df = pd.read_excel(self.path['path'] + '/jobs/scraped_jobs.xlsx', index=False)
            df.loc[(df["Company"] == company["Company"], ["Have Emailed","Date Emailed"])] = ["Y", datetime.datetime.now().strftime("%x")]
            excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/jobs/scraped_jobs.xlsx')
            sf = StyleFrame(df)
            sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Title','Company','Location','URL', 'Date Posted', 'Date Scraped'))
            excel_writer.save()
        else:
            raise ValueError('Couldn\'t find the path file')

    
    def validate(self):
        while True:
            q = input("(Y or N): ")
            if q.lower() == "y":
                return True
            if q.lower() == "n":
                return False
            
    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        return self
