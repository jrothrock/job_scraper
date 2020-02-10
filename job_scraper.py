import pandas as pd
import requests
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from shutil import copy2 as copy
from fuzzywuzzy import fuzz
from webdriver_manager.chrome import ChromeDriverManager
import yaml
from text2digits import text2digits
import datetime
import xlrd
import time
from StyleFrame import StyleFrame

class JobScraper(object):
    def __init__(self):
        self.builtIn = False
        self.google = False
        self.days = None
        self.minimum = None
        self.maximum = None
        self.contractToHireBoolean = True
        self.caps = DesiredCapabilities().CHROME
        self.caps["pageLoadStrategy"] = "eager"
        self.checkIsNumber = re.compile('^[0-9\,\s]+$')
        self.findYearsOfExperience = re.compile('([\d{1}][\d{1}]?)-?\s?(to)?\s?([\d{1}][\d{1}]?)?\+?\syear.*(experience|implementing|writing)')
        self.contractToHire = re.compile('(has a client)?((d|D)uration(:)? [\d]?-?[\d]?[\d]? (month(s)?|year(s)?|week(s)?))?((o|O)ur .* client is (looking|seeking|searching))?((C|c)ontract position)?([\d]?-?[\d]?[\d]? (month(s)?|year(s)?|week(s))? contract)?')
        self.t2d = text2digits.Text2Digits()
        self.driver = webdriver.Chrome(desired_capabilities=self.caps, executable_path=ChromeDriverManager().install())
        if os.path.exists('./utils/jobs.yml') == True:
            with open(r'./utils/jobs.yml') as file:
                document = yaml.full_load(file)
                self.jobs = list(document[0].values())[0]
        else:
            print("Specific job titles need to be set. Exiting...")
            time.sleep(1)
            return False

        if os.path.exists('./utils/experience.yml') == True:
            with open(r'./utils/experience.yml') as f:    
                data = yaml.load(f, Loader=yaml.FullLoader)
                self.minimum = int(data['minimum']) if data['minimum'] != None else None
                self.maximum = int(data['maximum']) if data['maximum'] != None else None
                self.includeNoMention = bool(data['includeNoMention'])
        else:
            self.minimum = None
            self.maximum = None
        
        if os.path.exists('./utils/files.yml') == True:
            with open(r'./utils/files.yml') as file:
                self.path = yaml.full_load(file)
        else:
            self.path = {}

        if os.path.exists('./utils/keywords.yml') == True:
            with open(r'./utils/keywords.yml') as file:
                document = yaml.full_load(file)
                self.keywords = list(document[0].values())[0]
        else:
            self.keywords = []
        
        if os.path.exists('./utils/antiwords.yml') == True:
            with open(r'./utils/antiwords.yml') as file:
                document = yaml.full_load(file)
                self.antiwords = list(document[0].values())[0]
        else:
            self.antiwords = []
    
    def checkScrape(self):
        print("\n\n//////")
        print("Job Scraper")
        print("//////")

        print("\nThere are a few places to scrape for jobs.")
        print("Which places would you like to scrape?\n 1. Google \n 2. BuiltIn \nIf you'd like to select multiple, comma seperate the numbers")
        
        while True:
            scrapeAnswer = input("Enter Number(s): ")
            if self.checkIsNumber.match(scrapeAnswer) != None:
                scrapeList = list(filter(None, [int(x.strip()) for x in scrapeAnswer.split(',')]))
                if 1 in scrapeList:
                    self.google = True
                if 2 in scrapeList:
                    self.builtIn = True
                if any(x <= 2 for x in scrapeList):
                    break

        if self.google == True:
            self.initGoogle()

        if self.builtIn == True:
            self.initBuiltIn()
        
        print("\n** Job Scraper Completed, Returning To Main Dashboard **")
        time.sleep(1)
                
    def initBuiltIn(self):
        print('\nHow far back (in days) are you willing to look? (A smaller number is recommended [like 3], as there may already be a lot of applicants)')

        while True:
            daysAnswer = input("Enter Number Of Days: ")
            if self.checkIsNumber.match(daysAnswer) != None:
                self.days = int(daysAnswer)
                break

        print("\nWhich BuiltIns would you like to scrape?")
        print(" 1. Austin\n 2. Boston \n 3. Chicago \n 4. Colorado \n 5. Los Angeles \n 6. NYC \n 7. San Francisco \n 8. Seattle \nIf you'd like to select multiple, comma seperate the numbers")

        builtInUrls = {
            "1":"https://www.builtinaustin.com/jobs?page=",
            "2":"https://www.builtinboston.com/jobs?page=",
            "3":"https://www.builtinchicago.org/jobs?page=",
            "4":"http://builtincolorado.com/jobs?page=",
            "5":"http://builtinla.com/jobs?page=",
            "6":"http://builtinnyc.com/jobs?page=",
            "7":"https://www.builtinsf.com/jobs?page=",
            "8":"https://www.builtinseattle.com/jobs?page="
        }

        while True:
            scrapeAnswer = input("Enter Number(s): ")
            if self.checkIsNumber.match(scrapeAnswer) != None:
                scrapeList = list(filter(None, [x.strip() for x in scrapeAnswer.split(',')]))
                for x in scrapeList:
                    self.scrapeBuiltIn(builtInUrls[x])
                break

    
    def scrapeBuiltIn(self, bultInUrl):
        print("\n\nScraping... This may take awhile")
        page = 0
        
        while True:

            posts = []
            url = bultInUrl + str(page)

            # for some reason, /jobs?page=0 is different than just normal /jobs...

            self.driver.get(url)
            time.sleep(1)
            try:
                wait = WebDriverWait(self.driver, 12).until(EC.visibility_of_element_located((By.CLASS_NAME, "view-display-id-jobs_landing")))
            except:
                print("Browser timed out. You may have been flagged as a bot")
                return self

            body = self.driver.find_element_by_class_name('view-display-id-jobs_landing')
            rows = body.find_elements(By.CLASS_NAME, "views-row")
            lastDate = rows[-1].find_element_by_xpath('.//div[@class="job-date"]').text

            for row in rows:
                try:
                    title = row.find_element_by_xpath('.//h2[@class="title"]').text
                    date = row.find_element_by_xpath('.//div[@class="job-date"]').text
                    url = row.find_element_by_xpath('.//div[@class="wrap-view-page"]/a').get_attribute("href")
                    #print(url)
                    if self.checkDistance(title) == True:
                        posts.append({"href": url, "posted": date})
                    # used for testing
                    #posts.append({"href": url, "posted": date})
                except Exception as ex:
                    pass

            for post in posts:
                 self.scrapeBuiltInPost(post["href"], post["posted"])

            if self.checkTime(lastDate) == True:
                page += 1
                time.sleep(2)
            else:
                break
                


    def scrapeBuiltInPost(self, BuiltInUrl, posted):
        self.driver.get(BuiltInUrl)
        time.sleep(1)
        wait = WebDriverWait(self.driver, 12).until(EC.visibility_of_element_located((By.CLASS_NAME, "block-region-middle")))

        body = self.driver.find_element_by_class_name('block-region-middle')

        try:
            button = body.find_element_by_xpath('.//div[@id="read-more-description-toggle"]/span')
            button.click()
        except:
            pass

        description = body.find_element_by_xpath('.//div[@class="job-description"]')
        t2dDescription = self.t2d.convert(description.text)
        if (self.includeNoMention == True and self.findYearsOfExperience.match(t2dDescription) == None) or self.checkExperience(t2dDescription) == True:
            if len(self.keywords) == 0 or any(word in t2dDescription for word in self.keywords):
                if len(self.antiwords) == 0 or any(word in t2dDescription for word in self.antiwords) == False:
                    try:
                        title = body.find_element_by_xpath('.//h1[@class="node-title"]/span').text
                        company = body.find_element_by_xpath('.//div[@class="job-info"]/div/div/a').text
                        location = body.find_element_by_xpath('.//span[@class="company-address"]').text
                        self.noteCompany(title, company, location, BuiltInUrl, 'BuiltIn', self.getDate(posted))
                    except Exception as ex:
                        print(ex)
        
    def initGoogle(self):
        print("\nWhat is the location of the job you're looking for:\nIf you'd like to select multiple cities, comma seperat them. (Ex: Denver, LA, Boston)")
        location = input("Location: ")

        locationList = list(filter(None, [x.strip() for x in location.split(',')]))

        print('\nHow far back (in days) are you willing to look? (A smaller number is recommended, as there may already be a lot of applicants)\nOptions:\n 1. Today\n 2. 3 days\n 3. 1 week \n 4. 1 month')

        daysStr = None
        while True:
            daysAnswer = input("Enter Option: ")
            if self.checkIsNumber.match(daysAnswer) != None:
                if daysAnswer == "1":
                    daysStr = "today"
                    break
                elif daysAnswer == "2":
                    daysStr = "3days"
                    break
                elif daysAnswer == "3":
                    daysStr = "week"
                    break
                elif daysAnswer == "4":
                    daysStr = "month"
                    break
        
        print("\nWhat is the radius of your job search?\nOptions:\n 1. 5 mi\n 2. 15 mi\n 3. 30 mi\n 4. 60 mi \n 5. 200 mi \n 6. Anywhere")
        radiusStr = None
        while True:
            radiusAnswer = input("Enter Option: ")
            if self.checkIsNumber.match(radiusAnswer) != None:
                if radiusAnswer == "1":
                    radiusStr = "8.0467"
                    break
                elif radiusAnswer == "2":
                    radiusStr = "24.1401"
                    break
                elif radiusAnswer == "3":
                    radiusStr = "48.2802"
                    break
                elif radiusAnswer == "4":
                    radiusStr = "96.5604"
                    break
                elif radiusAnswer == "5":
                    radiusStr = "321.868"
                    break
                elif radiusAnswer == "6":
                    radiusStr = "-1"
                    break
        
        print("\nWould you like to keep contract to hires? (If you don't know what this is, select Y) - Note, this feature doesn't work 100% of the time")

        if self.validate() == True:
            self.contractToHireBoolean = True
        else:
            self.contractToHireBoolean = False

        for job in self.jobs:
            for location in locationList:
                jobStr = job.replace(" ", "+")
                locStr = location.strip().replace(" ", "+") 
                url = "https://www.google.com/search?q=" + jobStr + "+" + locStr + "+jobs" + "&ibp=htl;jobs#htivrt=jobs&fpstate=tldetail&htichips=date_posted:"+daysStr+"&htischips=date_posted;"+daysStr+"&htilrad="+radiusStr
                self.scrapeGoogle(url)

    def scrapeGoogle(self, url):
        print("\nScraping Google. This may take awhile...")

        self.driver.get(url)
        time.sleep(5)
        wait = WebDriverWait(self.driver, 100).until(EC.visibility_of_element_located((By.CLASS_NAME, "ZBwwL")))
        # this really isn't the best way to do this. Should try and figure out how to do the recursion with execute_script
        for _ in range(10):
            time.sleep(1)
            self.driver.execute_script("var bottom = function(){var bottomLI = document.getElementsByClassName('gws-plugins-horizon-jobs__li-ed')[document.getElementsByClassName('gws-plugins-horizon-jobs__li-ed').length-1].offsetTop;document.getElementsByClassName('zxU94d')[0].scrollTop=bottomLI;}()")
        body = body = self.driver.find_element_by_class_name('ZBwwL')
        rows = body.find_elements(By.CLASS_NAME, "gws-plugins-horizon-jobs__li-ed")

        for index in range(len(rows)):
            title = self.driver.execute_script("return document.getElementsByClassName('KLsYvd')["+str(index)+"].innerText")
            company = self.driver.execute_script("return document.getElementsByClassName('nJlQNd')["+str(index)+"].innerText")
            location = self.driver.execute_script("return document.getElementsByClassName('tJ9zfc')["+str(index)+"].children[1].innerText")
            description = self.driver.execute_script("return document.getElementsByClassName('HBvzbc')["+str(index)+"].innerText")
            posted = self.driver.execute_script("return document.getElementsByClassName('ocResc')["+str(index)+"].querySelectorAll('span[aria-label=\"Posted\"]')[0].parentElement.querySelector('.SuWscb').innerText")
            # there's a better way to do get the postURL, but it requires clicking on every post, so that the other links load. Then it's possible to scrape for LinkedIn urls.
            # example for LinkedIn, but it'd need an if statement if there's no LinkedIn one in the end.
            # document.evaluate(".//div[contains(@class, 'mR2gOd')]//a[contains(text(),'Apply on LinkedIn')]", document.getElementsByClassName('pE8vnd')[11], null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue

            postUrl = self.driver.execute_script("return document.evaluate(\".//div[contains(@class, 'mR2gOd')]//a\", document.getElementsByClassName('pE8vnd')["+str(index)+"], null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.getAttribute('href')")

            t2dDescription = self.t2d.convert(description)
            if (self.includeNoMention == True and self.findYearsOfExperience.match(t2dDescription) == None) or self.checkExperience(t2dDescription) == True:
                if len(self.keywords) == 0 or any(word in t2dDescription for word in self.keywords):
                    if len(self.antiwords) == 0 or any(word in t2dDescription for word in self.antiwords) == False:
                        if self.contractToHireBoolean == True or self.contractToHire.match(t2dDescription) != None:
                            self.noteCompany(title, company, location, postUrl, 'Google Jobs', self.getDate(posted))

        time.sleep(2)

    def checkExperience(self, text):
        captured = self.findYearsOfExperience.search(text)
        if captured != None:
            minimum = int(captured.groups()[0]) if captured.groups()[0] != None else None
            maximum = int(captured.groups()[2]) if captured.groups()[2] != None else None
            if minimum != None and minimum >= self.minimum and minimum <= self.maximum and (maximum == None or maximum >= self.minimum):
                return True
            else:
                return False
        else:
            return False

    def noteCompany(self, title, company, location, url, placeScraped, datePosted):
        if "path" in self.path and self.path['path'] != "":
            columns = ['Title','Company','Location','URL', 'Site', 'Date Posted', 'Date Scraped', 'Would You Like To Scrape Emails?','Emails Scraped/Attempted', 'Date Emails Scraped', 'Would you like to email?', 'Have Emailed', 'Date Emailed', 'Applied To (This one you\'ll have to manager on your own)', 'Applied To Date (Again, you\'ll have to manage this)']
            job = [(title, company, location, url, placeScraped, datePosted, datetime.datetime.now().strftime("%x"), None, None, None, None, None, None, None, None)]
            if os.path.exists(self.path['path'] + '/jobs/scraped_jobs.xlsx') == False:
                excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/jobs/scraped_jobs.xlsx')
                df = pd.DataFrame(job, columns=columns)
                sf = StyleFrame(df)
                sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Title','Company','Location','URL', 'Site', 'Date Posted', 'Date Scraped'))
                excel_writer.save()
            else:
                df = pd.read_excel(self.path['path'] + '/jobs/scraped_jobs.xlsx', index=False)
                # check if job has already been scraped
                if len(df.loc[(df.Title == title ) & (df.Company == company)]) == 0:
                    df2 = pd.DataFrame(job, columns=columns)
                    dfnew = df.append(df2, ignore_index=True)
                    excel_writer = StyleFrame.ExcelWriter(self.path['path'] + '/jobs/scraped_jobs.xlsx')
                    sf = StyleFrame(dfnew)
                    sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, best_fit=('Title','Company','Location','URL', 'Site', 'Date Posted', 'Date Scraped'))
                    excel_writer.save()

        else:
            print("Remember that issue I noted earlier? Well, we finally hit it.\n I have wrote the scraped stuff into a text file that is found within this applications folders, and may be hard to reach...")
            with open("./files/jobsearch.txt","a+") as f:
                text = title + " " + company + " " + location  + " " + url + "\n"
                f.write(text)

    def checkTime(self, s):
        s = s.lower().replace("hour ", "hours ").replace("day ", "days ").replace("month ", "months ")
        parsed_s = [s.split()[:2]]
        time_dict = dict((fmt,float(amount)) for amount,fmt in parsed_s)
        timeDelta = datetime.timedelta(**time_dict)
        max_dict = {"days": int(self.days)}
        maxDelta = datetime.timedelta(**max_dict)
        try:
            if timeDelta < maxDelta:
                return True
            else:
                return False
        except:
            return False
    
    def getDate(self, s):
        s = s.lower().replace("hour ", "hours ").replace("day ", "days ").replace("month ", "months ")
        parsed_s = [s.split()[:2]]
        time_dict = dict((fmt,float(amount)) for amount,fmt in parsed_s)
        timeDelta = datetime.timedelta(**time_dict)
        today = datetime.datetime.today()
        posted = today - timeDelta
        return posted.strftime("%x")

    def checkDistance(self, word):
        values = map(lambda x : fuzz.ratio(x, word) >= 72, self.jobs)
        return any(x == True for x in values)
    
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
