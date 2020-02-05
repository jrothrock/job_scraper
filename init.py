import time
import os.path
import yaml
import re

class Init(object):
    def __init__(self):
        self.jobs = []
        self.experience = []
        self.keywords = []
        self.yearsReg = re.compile('^[0-9\+\-\,\s]+$')

    def intro(self):
        time.sleep(0.5)
        print("\n\nWelcome to the job scraper!\n\n")
        time.sleep(1.5)
    
    def checkUtils(self):
        try:
            self.checkJobsUtils()
            self.checkExperienceUtils()
            self.checkKeyWordsUtils()

            print("\n\nJust to double check:")
            print('You are searching for: ' + ', '.join(self.jobs) + ' jobs')
            
            if len(self.experience) > 0:
                print('With: ' + ', '.join(self.experience) + ' years of experience')
            else:
                print("You did not specify a certain amount of experience")

            if len(self.keywords) > 0: 
                print('With these keywords in the description: ' + ', '.join(self.keywords))
            else:
                print("You did not specify any keywords")

            print("Is this correct?\n")
            if self.validate() == False:
                self.checkUtils()
        except Exception as e: print(e)

    def checkJobsUtils(self):
        if os.path.exists('./utils/jobs.yml') == False:
            self.newJobs()
        else:
            with open('./utils/jobs.yml') as file:
                document = yaml.full_load(file)
                self.jobs = list(document[0].values())[0]
                print('You were searching for: ' + ', '.join(self.jobs) + ' is this still correct?')
                if self.validate() == False:
                    self.newJobs()
                
    def newJobs(self):
        self.clean('jobs')

        self.getJobs()

        yaml_jobs = [{"Jobs": self.jobs}]
        with open(r'./utils/jobs.yml', 'w') as file:
            documents = yaml.dump(yaml_jobs, file)

    def getJobs(self):
        self.typeOfJobs()
        
        print('\nYou listed: ' + ', '.join(self.jobs) + ' is this correct?')
        
        if self.validate() == False:
            self.getJobs()

    def typeOfJobs(self):
        self.jobs = []
        print("What type of jobs are looking for? Enter one at a time. Type \"Done\" when you're finished")
        while True:
            jobsInput = input("Job Name: ")
            if jobsInput.lower() == "done":
                break
            else:
                if "," in jobsInput.strip():
                    jobsList = list(filter(None, [x.strip() for x in jobsInput.split(',')]))
                    self.jobs = self.jobs + jobsList
                else:
                    self.jobs.append(jobsInput.strip())
    
    def checkExperienceUtils(self):
        if os.path.exists('./utils/experience.yml') == False:
            print("\nWould you like to specify how much experience a job should have? (Highly recommended)")
            if self.validate() == True:
                self.newExperience()
        else:
            with open('./utils/experience.yml') as file:
                document = yaml.full_load(file)
                self.experience = list(document[0].values())[0]
                print('You were searching for jobs with: ' + ', '.join(self.experience) + ' experience, is this still correct?')
                if self.validate() == False:
                    self.newExperience()
    
    def newExperience(self):
        self.clean('experience')
        
        self.getExperience()

        yaml_experience = [{"Experience": self.experience}]
        with open(r'./utils/experience.yml', 'w') as file:
            documents = yaml.dump(yaml_experience, file)
    
    def getExperience(self):
        self.typeOfExperience()

        print('\nYou listed: ' + ', '.join(self.experience) + ' is this correct?')
        
        if self.validate() == False:
            self.getExperience()

    def typeOfExperience(self):
        self.experience = []

        print("\n Please input the amount of experience you want the job to have. \n The only characters allowed are numbers, pluses, and hyphens. No need for spaces. \n examples: 0, 0+, 0-2, 2+, 3-5, 5+, 5-7, 7+, etc+ \n\n Enter each one, one at a time. Enter \"done\" when you're finished \n")
        while True:
            experienceInput = input("Experience: ")
            if experienceInput.lower() == "done":
                    break
            else:
                if self.yearsReg.match(experienceInput) != None:
                    if "," in experienceInput.strip():
                        experienceList = list(filter(None, [x.strip() for x in experienceInput.split(',')]))
                        self.experience = self.experience + experienceList
                    else:
                        self.experience.append(experienceInput.strip())
                else:
                    print("Only numbers, pluses, and hyphens are allowed. \n")
    
    def checkKeyWordsUtils(self):
        if os.path.exists('./utils/keywords.yml') == False:
            print("\nWould you like to look for certain keywords in the description? (recommended)")
            if self.validate() == True:
                self.newKeyWords()
        else:
            with open('./utils/keywords.yml') as file:
                document = yaml.full_load(file)
                self.experience = list(document[0].values())[0]
                print('You were searching for jobs with the following keywords: ' + ', '.join(self.keywords) + ' is this still correct?')
                if self.validate() == False:
                    self.newExperience()
    
    def newKeyWords(self):
        self.clean('keywords')
        
        self.getKeyWords()

        yaml_keywords = [{"KeyWords": self.keywords}]
        with open(r'./utils/keywords.yml', 'w') as file:
            documents = yaml.dump(yaml_keywords, file)
    
    def getKeyWords(self):
        self.typeOfKeywords()

        print('\nYou listed: ' + ', '.join(self.keywords) + ' is this correct?')
        
        if self.validate() == False:
            self.getKeyWords()

    def typeOfKeywords(self):
        self.keywords = []

        print("\n Please input the keywords you want the job to have. Single word inputs are a lot better. \n examples: Wordpress, FP&A, PMP, Salesforce, Angular, etc. \n\n Enter each one, one at a time. Enter \"done\" when you're finished \n")
        while True:
            keywordsInput = input("Key Words: ")
            if keywordsInput.lower() == "done":
                break
            else:
                if "," in keywordsInput.strip():
                    keywordsList = list(filter(None, [x.strip() for x in keywordsInput.split(',')]))
                    self.keywords = self.keywords + keywordsList
                else:
                    self.keywords.append(keywordsInput.strip())

    def validate(self):
        while True:
            q = input("(Y or N): ")
            if q.lower() == "y":
                return True
            if q.lower() == "n":
                return False
        
    def clean(self, typ):
        try:
            if typ == "jobs":
                os.remove('./utils/jobs.yml')
            if typ == "experience":
                os.remove('./utils/experience.yml')
            if typ == "keywords":
                os.remove('./utils/keywords.yml')
        except OSError:
            pass 
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        return self