import pandas as pd
import requests
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from shutil import copy2 as copy
from fuzzywuzzy import fuzz
from webdriver_manager.chrome import ChromeDriverManager
import time
import yaml

class JobScraper(object):
    def __init__(self):
        self.builtIn = False
        self.google = False
        self.checkIsNumber = re.compile('^[0-9\,\s]+$')
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        with open(r'./utils/jobs.yml') as file:
            document = yaml.full_load(file)
            self.jobs = list(document[0].values())[0]
        
        with open(r'./utils/experience.yml') as file:
            document = yaml.full_load(file)
            self.experience = list(document[0].values())[0]

        with open(r'./utils/keywords.yml') as file:
            document = yaml.full_load(file)
            self.keywords = list(document[0].values())[0]
    
    def checkScrape(self):
        print("There are a few places to scrape for jobs.")
        print("Which places would you like to scrape?\n 1. BuiltIn \n 2. Google \n If you'd like to select multiple, comma seperate the numbers")
        
        while True:
            scrapeAnswer = input("Enter Number(s): ")
            if self.checkIsNumber.match(scrapeAnswer) != None:
                scrapeList = list(filter(None, [int(x.strip()) for x in scrapeAnswer.split(',')]))
                if 1 in scrapeList:
                    self.builtIn = True
                if 2 in scrapeList:
                    self.google = True
                if any(x <= 2 for x in scrapeList):
                    break
        
        if self.builtIn == True:
            self.initBuiltIn()
        
        if self.google == True:
            print("this hasn't been built yet, check back in a little!")
                
    def initBuiltIn(self):
        print("Which BuiltIns would you like to scrape?")
        print("\n 1. Austin\n 2. Boston \n 3. Chicago \n 4. Colorado \n 5. Los Angeles \n 6. NYC \n 7. San Francisco \n 8. Seattle \n If you'd like to select multiple, comma seperate the numbers")

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
                    print(x)
                    print(builtInUrls[x])
                    self.scrapeBuiltIn(builtInUrls[x])
                break

    
    def scrapeBuiltIn(self, bultInUrl):
        page = 0
        
        url = bultInUrl + str(page)

        # for some reason, /jobs?page=0 is different than just normal /jobs...

        self.driver.get(url)
        time.sleep(1)
        wait = WebDriverWait(self.driver, 100).until(EC.visibility_of_element_located((By.CLASS_NAME, "view-display-id-jobs_landing")))

        body = self.driver.find_element_by_class_name('view-display-id-jobs_landing')
        rows = body.find_elements(By.CLASS_NAME, "views-row")

        for row in rows:
            try:
                title = row.find_element_by_xpath('.//h2[@class="title"]')
                company = row.find_element_by_xpath('.//div[@class="company-title"]')
                date = row.find_element_by_xpath('.//div[@class="job-date"]')
                if self.checkDistance(title.text) == True:
                    text = title.text + " " + company.text + " " + date.text + "\n"
                    #f.write(text)
            except Exception as ex:
                print(ex) # do whatever you want for debugging.
        
        return self.jobs

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
