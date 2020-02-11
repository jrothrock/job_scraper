from init import Init 
from job_scraper import JobScraper
from scrape_emails import ScrapeEmails
from emailer import Emailer
import os.path
import re
import time
import yaml
import os
import shutil
from sys import exit
import pathlib

class Main(object):
    def __init__(self):
        self.checkForUtils()
        self.userQuit = False
        self.checkIsOption = re.compile('^[0-9qQ\^C]+$')
        self.checkFilesPath()

    def begin(self):
        try:
            self.intro()
            while True:
                try:
                    progress = self.checkProgress()
                    if progress == 1:
                        self.start(progress)
                    else: 
                        begin = self.getOption(progress)
                        if progress == 2:
                            # have to recheck files path, as this may have changed in the progress == 2 step, and we want the ask where to start to be current
                            self.checkFilesPath()
                except (KeyboardInterrupt, SystemExit):
                    if progress == 1 or self.userQuit == True:
                        raise
                    else: 
                        pass
                except Exception as e:
                    print(e)
                    self.tryAndFix()

        except Exception as e: 
            print(e) 

    def intro(self):
        time.sleep(0.5)
        print("\n\nWelcome to the job scraper!")
        time.sleep(1.5)   
        
    def start(self, progress):
        if progress == 1:
            with Init() as i:
                i.checkUtils()
        if progress == 2:
            with JobScraper() as js:
                js.checkScrape()
        if progress == 3:
           with ScrapeEmails() as se:
               se.begin()
        if progress == 4:
            with Emailer() as e:
                e.begin()
        
    def checkFilesPath(self):
        if os.path.exists('./utils/files.yml') == True:
            with open(r'./utils/files.yml') as file:
                self.path = yaml.full_load(file)
        else:
            self.path = {}
 

    def checkProgress(self):
        jobs = os.path.exists('./utils/jobs.yml') == True 
        personal = os.path.exists('./utils/personal.yml') == True
        files = os.path.exists('./utils/files.yml') == True
        if any(file == False for file in [personal,files,jobs]):
            return 1
        elif "path" not in self.path or os.path.exists(self.path['path'] + '/jobs/scraped_jobs.xlsx') == False:
            return 2
        elif os.path.exists(self.path['path'] + '/emails/scraped_emails.xlsx') == False:
            return 3
        else:
            return 4
         
    

    def askWhereToStart(self,progress):
        print("\n\n/////////////////")
        print("// MAIN DASHBOARD")
        print("/////////////////")

        if progress == 2:
            print("\nOptions:\n 1. Initial Information (view and edit initial information)\n 2. Scrape Jobs \n Q. Quit")
            print("You've completed initial information. Which option would you like to do?\n")
        if progress == 3:
            print("\nOptions:\n 1. Initial Information (view and edit initial information)\n 2. Scrape Jobs\n 3. Scrape Emails\n Q. Quit")
            print("You've completed initial information, and have scraped some jobs. Which option would you like to do?\n")
        if progress == 4:
            print("\nOptions:\n 1. Initial Information (view and edit initial information)\n 2. Scrape Jobs\n 3. Scrape Emails\n 4. Email The Scraped Emails\n Q. Quit")
            print("You've completed initial information, scraped some jobs, and have scraped some emails as well. Which option would you like to do?\n")
        
    def getOption(self, progress):
        self.askWhereToStart(progress)

        while True:
            option = input("Enter number or Q: ")
            if self.checkIsOption.match(option) != None:
                if option == "1":
                    self.start(1)
                    break
                elif option == "2":
                    self.start(2)
                    break
                elif option == "3":
                    if progress >= 3:
                        self.start(3)
                        break
                elif option == "4":
                    if progress == 4:
                        self.start(4)
                        break
                else:
                    self.userQuit = True
                    exit()
    
    def tryAndFix(self):
        print("\n\n\n\n\nERROR: There was a major/fatal error that occured. Read below on how to maybe fix it.")
        print("\nSomewhere deep in the code, there was an unexpected error.")
        print("My guess is this has something to do with data integrity, which I admittedly did like zero checking for.")
        print("Here's the good news. It may be fixable. Bad news, I will have to delete all application files/data, including the JobSraper folder.")
        print("I'd suggest backing up or renaming the folder")
        print("There's more bad news... The program will close when this is done (so you'll have to relaunch it.) If you get this same message, then this program will not work. I'm sorry. \n")

        print("\nWould you like to erase all of the application's files/data and see if this fixes it?")
        if self.validate() == True:
            print("\n\nJUST TO DOUBLE CHECK, are you sure you want to? This will delete things like scraped_jobs.xlsx, and scraped_emails.xlsx as well")
            if self.validate() == True:
                self.cleanEverything()
            else:
                exit()
        else:
            exit()

    def cleanEverything(self):
        files = ["./utils/experience.yml", './utils/personal.yml', './utils/files.yml', './utils/keywords.yml', './utils/jobs.yml']
        for file in files:
            try:
                os.remove(file)
            except:
                pass
        
        if "path" in self.path:
            try:
                shutil.rmtree(self.path["path"])
            except:
                pass
        
        print("All contents have been removed. Please relaunch the application.")
        time.sleep(2)
        exit()
    
    def checkForUtils(self):
        f = 'job_scraper.command'
        for path, dirs, files in os.walk(str(pathlib.Path().home()) + "/Downloads"):
            if f in files:
                os.chdir(path)
                break

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

if __name__ == '__main__':
    with Main() as main:
        main.begin()
