import pandas as pd
import requests
import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time
from shutil import copy2 as copy
import yaml
import urllib.parse
from StyleFrame import StyleFrame
import http.client
import json
import datetime

class ScrapeEmails(object):
    def __init__(self):

        self.scroll_pause = 0.1
        self.scroll_increment = 300
        self.timeout = 10
        self.emails = []
        self.companies = []
        self.debounce_io = None
        self.hunter_io = ""
        self.debounce_io = ""
        self.caps = DesiredCapabilities().CHROME
        self.caps["pageLoadStrategy"] = "eager"
        self.driver = webdriver.Chrome(desired_capabilities=self.caps, executable_path=ChromeDriverManager().install())
        self.checkIsNumber = re.compile('^[0-9\.]+$')

        if os.path.exists('./utils/files.yml') == True:
            with open(r'./utils/files.yml') as file:
                self.path = yaml.full_load(file)
        else:
            self.path = {}
    
    def begin(self):
        print("\n\n//////")
        print("Email Scraper")
        print("//////")

        print("\nBefore we can continue, have you gone into the scraped_jobs.xlsx and marked the jobs you want to scrape (by putting a Y in the \"Would You Like To Scrape Emails\" columns)\nSee 3:48, in the video (https://www.youtube.com/watch?v=RvCyLQK7VMo) for more information.")

        if self.validate() == False:
            return self
        
        while True:
            if self.getCompanies() == False:
                print("\nHmm. We weren't able to find any companies in the sheet that were marked (y) in the \"Would you like to scrape emails?\" column, that weren't already scraped.\nWould you like to try again? ")
                if self.validate() == False:
                    return self
            else:
                break
        
        print("\nWhat is your li_at cookie on LinkedIn? Watch 4:02 of the instructional video (https://www.youtube.com/watch?v=RvCyLQK7VMo) on how to obtain this")
        while True:
            self.li_at = input("Paste li_at cookie: ")
            if len(self.li_at) > 0:
                break
            else:
                print("the li_at cookie is needed for scraping.")

        self.checkVerify()
                
        self.scrape()

        print("\n** Email Scraper Completed, Returning To Main Dashboard **")
        time.sleep(1)

    def scrape(self):
        print("\nScraping LinkedIn. This may take awhile...")
        self.driver.get('http://www.linkedin.com')
        self.driver.add_cookie({
            'name': 'li_at',
            'value': self.li_at,
            'domain': '.linkedin.com'
        })
        time.sleep(.5)
        for index, row in self.companies.iterrows():
            title = row["Title"]
            company = row["Company"]
            site = row["Site"]
            query = company + " recruiter"
            queryURI = urllib.parse.quote(query)
            url = "https://linkedin.com/search/results/all/?keywords="+queryURI+"&origin=GLOBAL_SEARCH_HEADER"
            self.scrapeLinkedIn(url, company, title, site)
            time.sleep(2)
            
    def scrapeLinkedIn(self, url, company, title, site):
        for i in range(3):
            # sometimes, there's a redirect error. This should minimize that
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 12).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".search-results-page")))
            except:
                print("Web browser timed out. Moving on")
                continue
            break

        self.scrape_people(company, title, site)
    
    def scrape_people(self,company, title, site):
        self.scroll_to_bottom()
        results = self.driver.find_elements(By.CSS_SELECTOR, ".search-result__wrapper")
        regexp = re.compile(r'.')
        for result in results:
            try:
                sublineLvl1 = result.find_element_by_class_name('subline-level-1').text
                sublineLvl3 = result.find_element_by_class_name('mt2').text
                name = result.find_element_by_class_name('name')
                isRecruiter = re.compile('(recruiter).*('+company+')')
                #print(isRecruiter.search(sublineLvl1) != None)
                #print(isRecruiter.search(sublineLvl3) != None)
                if name.text != "LinkedIn Member" and '.' not in name.text and ' ' in name.text:
                    if (("recruiter" in sublineLvl1.lower() or "talent" in sublineLvl1.lower() or "human resources" in sublineLvl1.lower() or "hr" in sublineLvl1.lower()) and company.lower() in sublineLvl1.lower()) or ("current:" in sublineLvl3.lower() and ("recruiter" in sublineLvl3.lower() or "talent" in sublineLvl3.lower() or "human resources" in sublineLvl3.lower() or "hr" in sublineLvl3.lower()) and company.lower() in sublineLvl3.lower()):
                    #if isRecruiter.search(sublineLvl3) != None and isRecruiter.search(sublineLvl3) != None:
                        self.checkEmail(name.text, company, title, site)
            except:
                pass
                
    
    def spinName(self,name,company,title,site):
        firstName, lastName = self.getName(name)
        companyStr = company.lower().replace(' ', '').replace(",", "").replace(".", "").replace("inc", "").replace("llc", "").replace("corp", "")

        emails = [
            firstName + '.' + lastName + '@' + companyStr + '.com',
            lastName + '.' + firstName + '@' + companyStr + '.com',
            lastName + '.' + firstName[0] + '@' + companyStr + '.com',
            firstName+ lastName + '@' + companyStr + '.com',
            lastName + firstName[0] + '@' + companyStr + '.com',
            firstName[0] + '.' + lastName + '@' + companyStr + '.com',
            firstName[0] + lastName + '@' + companyStr + '.com',
            firstName[0] + lastName[:8] + '@' + companyStr + '.com',
            firstName[0] + lastName[:7] + '@' + companyStr + '.com',
            firstName[0] + lastName[:6] + '@' + companyStr + '.com',
            firstName[0] + lastName[:5] + '@' + companyStr + '.com',
            firstName + '@' + companyStr + '.com',
            lastName + '@' + companyStr + '.com',
            firstName + '_' + lastName + '@' + companyStr + '.com',
            firstName + lastName[0] + '@' + companyStr + '.com',
            firstName[0] + '_' + lastName + '@' + companyStr + '.com'
        ]
        
        if len(self.debounce_io) > 0:
            self.checkEmailsDebounce(emails, name, company, title, site, 'y')
        else:
            print("\nWriting emails to excel sheet. These emails have not been verified though, and therefore may not work/bounce.")
            self.noteEmails(emails, name, company, title, site, 'n')
            self.updateJobsSheet(company)
    
    def checkVerify(self):
        print("\nWould you like to verify the email addresses? This will require either a hunter.io account or a debounce.io account")
        try:
            if self.validate() == True:
                print("\nWhich would you like to use? Brief explanation: Hunter.io will guess the email address of the person based on information they have scraped around the internt. Debounce.io will say whether the email exists or not, and we will try and create a bunch of different emails to test (less guarantee of getting an actual match).\nHunter.io is free for the first 50 requests, then $50 a month with 1000 requests. Debounce.io is free for the first 100 requests, then $10 for 5000 requests.\n Option 1. Hunter.io\n Option 2. Debounce.io")
                while True:
                    option = input("Which option would like to select: ")
                    if self.checkIsNumber.match(option):
                        if option == "1":
                            print("\nWhat is your hunter.io api key? Watch 4:25 of the instructional video (https://www.youtube.com/watch?v=RvCyLQK7VMo) on how to obtain this")
                            print("You can proceed through this, by hitting enter with no value, but the emails you send may not be valid, and your email account may be marked as spam.")
                            self.hunter_io = input("Paste API key: ")
                            break
                        elif option == "2":
                            print("\nWhat is your debounce.io api key?")
                            print("You can proceed through this, by hitting enter with no value, but the emails you send may not be valid, and your email account may be marked as spam.")
                            self.debounce_io = input("Paste API key: ")
                            break
                        else:
                            continue
                    else:
                        continue
        except Exception as e:
            print(e)
    
    def checkEmail(self, name, company, title, site):
        try:
            if len(self.hunter_io) > 0:
                self.checkEmailsHunter(name, company, title, site, 'y')
            else:       
                self.spinName(name, company, title, site)
        except Exception as e:
            print(e)

    def checkEmailsHunter(self, name, company, title, site, verified):
        
        conn = http.client.HTTPSConnection("api.hunter.io")

        try:
            firstName, lastName = self.getName(name)
            full_name = firstName + "+" + lastName
            print(full_name)
            conn.request("GET", "/v2/email-finder?company=" + urllib.parse.quote(company.lower()) + "&full_name=" + full_name + "&api_key=" + self.hunter_io)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            values = json.loads(data)
            print(values)
            if "errors" in values:
                if values["errors"]["code"] == 429:
                    raise ValueError('Ran out of credits, need to upgrade. Returning to dashboard')
                elif values["errors"]["code"] == 401:
                    raise ValueError('Invalid API key. Returning to dashboard')
                else:
                    print(values)
            else:
                print([values["data"]["email"]])
                self.noteEmails([values["data"]["email"]], name, company, title, site, 'y')
        except ValueError as ex:
            print(ex)
            pass
        except Exception as ex:
            print(ex)
        self.updateJobsSheet(company)

    def checkEmailsDebounce(self, emails, name, company, title, site, verified):
        conn = http.client.HTTPSConnection("api.debounce.io")
        found = False
        risky = False
        for email in emails:
            try:
                conn.request("GET", "/v1/?api=" + self.debounce_io +"&email="+email)

                res = conn.getresponse()
                data = res.read().decode("utf-8")
                values = json.loads(data)
                if values['debounce']['result'] == "Risky":
                    # stop, as all emails will just return Risky
                    risky = True
                    break
                elif values['debounce']['result'] == "Safe to Send":
                    self.noteEmails([email], name, company, title, site, verfied)
                    self.updateJobsSheet(company)
                    found = True
                    break
                elif "error" in values['debounce'] and values['debounce']["error"]  == "Credits Low":
                    print("Not enough debounce.io credits to check")
                    break
                else:
                    continue
            except Exception as ex:
                    print(ex)
        
        if risky == True:
            print("Emails for this person have been marked as Risky, and can't by identified. Proceeding without adding")
        elif found == False:
            print("Unfortunuately, all email combinations were found to be invalid for this person. Proceeding without adding")
            
    def noteEmails(self, emails, name, company, title, site, verified):
        if "path" in self.path and self.path['path'] != "":
            columns = ["Name", "Email", "Title", "Company", "Site", "Verified", "Want To Email", "Have Emailed"]
            if os.path.exists(self.path['path'] + '/emails/scraped_emails.xlsx') == False:
                emailsDf = []
                for email in emails:
                    emailsDf.append((name, email, title, company, site, verified, None, None))
                excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/emails/scraped_emails.xlsx')
                df = pd.DataFrame(emailsDf, columns=columns)
                sf = StyleFrame(df)
                sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Name','Email', 'Title', 'Company', 'Site', 'Verified'))
                excel_writer.save()
            else:
                df = pd.read_excel(self.path['path'] + '/emails/scraped_emails.xlsx', index=False)
                emailsDf = []
                for email in emails:
                    # check if email has already been scraped
                    if len(df.loc[(df.Email == email)]) == 0:
                        emailsDf.append((name, email, title, company, site, verified, None, None))
                if len(emailsDf):
                    df2 = pd.DataFrame(emailsDf, columns=columns)
                    dfnew = df.append(df2, ignore_index=True)
                    excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/emails/scraped_emails.xlsx')
                    sf = StyleFrame(dfnew)
                    sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Name', 'Email', 'Title', 'Company', 'Site', 'Verified'))
                    excel_writer.save()

        else:
            print("Remember that issue I noted earlier? Well, we finally hit it.\n I have wrote the scraped stuff into a text file that is found within this applications folders, and may be hard to reach...")
            with open("./files/jobsearch.txt","a+") as f:
                text = title + " " + company + " " + location  + " " + url + "\n"
                f.write(text)
    
    def scroll_to_bottom(self):
        current_height = 0
        while True:
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            time.sleep(self.scroll_pause)

    def updateJobsSheet(self, company):
        if "path" in self.path:
            df = pd.read_excel(self.path['path'] + '/jobs/scraped_jobs.xlsx', index=False)
            df.loc[(df["Company"] == company, ["Emails Scraped/Attempted","Date Emails Scraped"])] = ["Y", datetime.datetime.now().strftime("%x")]
            excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/jobs/scraped_jobs.xlsx')
            sf = StyleFrame(df)
            sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Title','Company','Location','URL', 'Date Posted', 'Date Scraped'))
            excel_writer.save()
        else:
            raise ValueError('Couldn\'t find the path file')

    def getCompanies(self):
        if "path" in self.path:
            try:
                df = pd.read_excel(self.path['path'] + '/jobs/scraped_jobs.xlsx', index=False)
                self.companies = df.loc[((df["Would You Like To Scrape Emails?"] == "y") |  (df["Would You Like To Scrape Emails?"] == "Y")) & ((df['Emails Scraped/Attempted'] != "y") | (df['Emails Scraped/Attempted'] != "Y"))]
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

    def getName(self, name):
        getName = name.replace('-','').encode('ascii', 'ignore').decode('ascii').strip().split(',')[0]
        nameParts = getName.split(' ')
        firstName = nameParts[0]
        lastName = nameParts[-1]
        return firstName, lastName

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
        self.quit()

    def quit(self):
        if self.driver:
            self.driver.quit()
