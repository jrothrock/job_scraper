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
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        with open(r'./utils/jobs.yml') as file:
            document = yaml.full_load(file)
            self.jobs = list(document[0].values())[0]
            print(self.jobs)
    
    def scrape(self):
        page = 0
        
        url = "https://www.builtincolorado.com/jobs?page=" + str(page)

        # for some reason, /jobs?page=0 is different than just normal /jobs...

        self.driver.get(url)
        time.sleep(5)
        wait = WebDriverWait(self.driver, 100).until(EC.visibility_of_element_located((By.CLASS_NAME, "view-display-id-jobs_landing")))

        body = self.driver.find_element_by_class_name('view-display-id-jobs_landing')
        rows = body.find_elements(By.CLASS_NAME, "views-row")

        with open("./files/jobsearch.txt","a+") as f:
            for row in rows:
                try:
                    title = row.find_element_by_xpath('.//h2[@class="title"]')
                    company = row.find_element_by_xpath('.//div[@class="company-title"]')
                    date = row.find_element_by_xpath('.//div[@class="job-date"]')
                    if self.checkDistance(title.text) == True:
                        text = title.text + " " + company.text + " " + date.text + "\n"
                        f.write(text)
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
