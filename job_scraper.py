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
import time
import yaml
from text2digits import text2digits
import datetime

class JobScraper(object):
    def __init__(self):
        self.builtIn = False
        self.google = False
        self.days = None
        self.minimum = None
        self.maximum = None
        self.caps = DesiredCapabilities().CHROME
        self.caps["pageLoadStrategy"] = "eager"
        self.checkIsNumber = re.compile('^[0-9\,\s]+$')
        self.findYearsOfExperience = re.compile('([\d{1}][\d{1}]?)-?\s?(to)?\s?([\d{1}][\d{1}]?)?\+?\syear.*(experience|implementing|writing)')
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
        else:
            self.minimum = None
            self.maximum = None

        if os.path.exists('./utils/personal.yml') == True:
            with open(r'./utils/personal.yml') as file:
                self.info = yaml.full_load(file)
        else:
            self.info = {}

        if os.path.exists('./utils/keywords.yml') == True:
            with open(r'./utils/keywords.yml') as file:
                document = yaml.full_load(file)
                self.keywords = list(document[0].values())[0]
        else:
            self.keywords = []
    
    def checkScrape(self):
        print('\nHow far back (in days) are you willing to look? (A smaller number is recommended [like 3], as there may already be a lot of applicants)')

        while True:
            daysAnswer = input("Enter Number Of Days: ")
            if self.checkIsNumber.match(daysAnswer) != None:
                self.days = int(daysAnswer)
                break

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

        if self.builtIn == True:
            self.initBuiltIn()
        
        if self.google == True:
            print("this hasn't been built yet, check back in a little!")
                
    def initBuiltIn(self):
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
        page = 0
        
        while True:
            urls = []

            url = bultInUrl + str(page)

            # for some reason, /jobs?page=0 is different than just normal /jobs...

            self.driver.get(url)
            time.sleep(1)
            wait = WebDriverWait(self.driver, 100).until(EC.visibility_of_element_located((By.CLASS_NAME, "view-display-id-jobs_landing")))

            body = self.driver.find_element_by_class_name('view-display-id-jobs_landing')
            rows = body.find_elements(By.CLASS_NAME, "views-row")
            lastDate = rows[-1].find_element_by_xpath('.//div[@class="job-date"]').text

            for row in rows:
                try:
                    title = row.find_element_by_xpath('.//h2[@class="title"]')
                    company = row.find_element_by_xpath('.//div[@class="company-title"]')
                    date = row.find_element_by_xpath('.//div[@class="job-date"]')
                    url = row.find_element_by_xpath('.//div[@class="wrap-view-page"]/a')
                    #print(url.get_attribute("href"))
                    if self.checkDistance(title.text) == True:
                        urls.append(url.get_attribute("href"))
                    # used for testing
                    #urls.append(url.get_attribute("href"))
                except Exception as ex:
                    print(ex)
            
            for url in urls:
                self.scrapeBuiltInPost(url)

            if self.checkTime(lastDate.lower()) == True:
                page += 1
            else:
                break
                


    def scrapeBuiltInPost(self, BuiltInUrl):
        self.driver.get(BuiltInUrl)
        time.sleep(1)
        wait = WebDriverWait(self.driver, 100).until(EC.visibility_of_element_located((By.CLASS_NAME, "block-region-middle")))

        body = self.driver.find_element_by_class_name('block-region-middle')
        try:
            button = body.find_element_by_xpath('.//div[@id="read-more-description-toggle"]/span')
            button.click()
        except:
            pass
        description = body.find_element_by_xpath('.//div[@class="job-description"]')
        t2dDescription = self.t2d.convert(description.text)
        if self.checkExperience(t2dDescription) == True:
            if len(self.keywords) == 0 or any(word in t2dDescription for word in self.keywords):
                try:
                    title = body.find_element_by_xpath('.//h1[@class="node-title"]/span').text
                    company = body.find_element_by_xpath('.//div[@class="job-info"]/div/div/a').text
                    location = body.find_element_by_xpath('.//span[@class="company-address"]').text
                    self.noteCompany(title, company, location, BuiltInUrl)
                except Exception as ex:
                    print(ex)

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

    def noteCompany(self, title, company, location, url):
        # instead of using text, change to xlsx
        # may be able to pull datePosted from schema tags on builtin
        with open("./files/jobsearch.txt","a+") as f:
            text = title + " " + company + " " + location  + " " + url + "\n"
            f.write(text)

    def checkTime(self, s):
        s = s.replace("hour ", "hours ").replace("day ", "days ").replace("month ", "months ")
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

    def checkDistance(self, word):
        values = map(lambda x : fuzz.ratio(x, word) >= 72, self.jobs)
        return any(x == True for x in values)

    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        self.quit()

    def quit(self):
        if self.driver:
            self.driver.quit()
