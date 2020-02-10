import time
import os.path
import yaml
import re
import pathlib
import shutil 

class Init(object):
    def __init__(self):
        self.info = {}
        self.jobs = []
        self.experience = {}
        self.keywords = []
        self.antiwords = []
        self.yearsReg = re.compile('^[0-9\+\-\,\s]+$')
        self.checkIsNumber = re.compile('^[0-9\.]+$')

    def checkUtils(self):
        print("\n\n////")
        print("Initial Information")
        print("////")
        try:
            self.checkPersonalUtils()
            self.checkFileUtils()
            self.checkJobsUtils()
            self.checkExperienceUtils()
            self.checkKeyWordsUtils()
            self.checkAntiWordsUtils()

            print("\n\nJust to double check:")
            print('You are searching for: ' + ', '.join(self.jobs) + ' jobs')
            
            if len(self.experience) > 0:
                print('With a minimum of ' + self.experience['minimum'] + ' years and a maximum of ' + self.experience['maximum'] + ' years of experience')
            else:
                print("You did not specify a certain amount of experience")

            if len(self.keywords) > 0: 
                print('With these keywords in the description: ' + ', '.join(self.keywords))
            else:
                print("You did not specify any keywords")
            
            if len(self.antiwords) > 0:
                print('With these antiwords in the description: ' + ', '.join(self.antiwords))
            else:
                print("You did not specify any antiwords")

            print("Is this correct?\n")
            if self.validate() == False:
                self.checkUtils()
            else:
                print("\n** Initial Information Completed, Returning To Main Dashboard **")
        except Exception as e: print(e)

    def checkPersonalUtils(self):
        if os.path.exists('./utils/personal.yml') == False:
            self.newPerson()
        else:
            with open('./utils/personal.yml') as file:
                self.info = yaml.full_load(file)
                print('\nFirst Name: ' + self.info['first'] + "; Last Name: " + self.info['last'] + "; Email: " + self.info['email'] + ". Is this still correct?")
                if self.validate() == False:
                    self.newPerson()
            
    def newPerson(self):
        self.clean('personal')

        print("\nTo begin, I'll need some personal information. The info you enter is only stored on your computer")
        self.getPersonalInfo()

        with open(r'./utils/personal.yml', 'w') as file:
            documents = yaml.dump(self.info, file)
    
    def getPersonalInfo(self):
        self.enterPersonalInfo()
        
        print('\nFirst Name: ' + self.info['first'] + "\nLast Name: " + self.info['last'] + "\nEmail: " + self.info['email'])
        print('\nIs the above correct?')
        
        if self.validate() == False:
            self.getPersonalInfo()
        

    def enterPersonalInfo(self):
        self.info['first'] = input("First Name: ")
        self.info['last'] = input("Last Name: ")
        self.info['email'] = input("Email (put the email you'd use for sending resumes): ")
    
    def checkFileUtils(self):
        pathString = None
        if os.path.exists('./utils/files.yml') == False:
            homePath = str(pathlib.Path().home())
            
            print("\nLet's create a folder to house all of your stuff.\nWhere would you like to place the folder?\n 1. documents \n 2. desktop \n 3. downloads")
            while True:
                # technically, a period is allowed, but it's whatever
                destination = input("Enter number:")
                if self.checkIsNumber.match(destination) != None:
                    if destination == "1":
                        pathString = homePath + "/documents"
                        break
                    elif destination == "2":
                        pathString = homePath + "/desktop"
                        break
                    elif destination == "3":
                        pathString = homePath + "/downloads"
                        break
                    else:
                      print("Only numbers are allowed. Please enter 1 for documents, 2 for desktop, or 3 for downloads")  
                else:
                    print("Only numbers are allowed. Please enter 1 for documents, 2 for desktop, or 3 for downloads")
  
            try:
                folderPath = pathString + "/JobScraper"
                if os.path.exists(folderPath) == False:
                    currentPath = str(pathlib.Path().absolute())
                    filesPath = currentPath + "/files"
                    shutil.copytree(filesPath, folderPath) 
                    
                with open(r'./utils/files.yml', 'w') as file:
                    documents = yaml.dump({"path": folderPath}, file)
                
            except:
                print("hmm... If you see this, please report this. As this will cause a lot of problems, and I was too lazy to actually build something for this error.")


    def checkJobsUtils(self):
        if os.path.exists('./utils/jobs.yml') == False:
            self.newJobs()
        else:
            with open('./utils/jobs.yml') as file:
                document = yaml.full_load(file)
                self.jobs = list(document[0].values())[0]
                print('\nYou were searching for: ' + ', '.join(self.jobs) + ' is this still correct?')
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
        print("\nWhat type of jobs are looking for? Enter one at a time. Type \"Done\" when you're finished")
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
                self.experience = yaml.full_load(file)
                print('\nYou were searching for jobs with a minimum experience of ' + self.experience['minimum'] + ' years and maximum of ' + self.experience['maximum'] + '. Is this still correct?')
                if self.validate() == False:
                    self.newExperience()
    
    def newExperience(self):
        self.clean('experience')
        
        self.getExperience()

        with open(r'./utils/experience.yml', 'w') as file:
            documents = yaml.dump(self.experience, file)
    
    def getExperience(self):
        self.typeOfExperience()

        print('\nYou listed ' + self.experience['minimum'] + ' for the minimum, and ' + self.experience['maximum'] + ' for the maximum. Is this correct?')
        
        if self.validate() == False:
            self.getExperience()

    def typeOfExperience(self):
        self.experience = {}

        print("\nWhat are your minimum and maximum amount of years of experience you're looking for? I'll search between those two numbers \nExample: if you have two years of exerpience, and you'll take an entry level, put 0 as minimum and 2 as maximum \nI'll match for jobs with: 0-2, 1, 1+, 2+ 2-5, etc. \nEnter whole numbers, as it'll round down decimals.\n")
        
        while True:
            experienceInput = input("Minimum amount of experience (years): ")
            if self.checkIsNumber.match(experienceInput) != None:
                self.experience['minimum'] = experienceInput
                break
            else:
                print("Only numbers are allowed")
        
        while True:
            experienceInput = input("Maxmimum amount of experience (years): ")
            if self.checkIsNumber.match(experienceInput) != None:
                self.experience['maximum'] = experienceInput
                break
            else:
                print("Only numbers are allowed")
        
        print("\nWould you like to include jobs that don\'t mention years of experience in the description?")
        if self.validate() == True:
            self.experience['includeNoMention'] = True
        else:
            self.experience['includeNoMention'] = True

    
    def checkKeyWordsUtils(self):
        if os.path.exists('./utils/keywords.yml') == False:
            print("\nWould you like to look for certain keywords in the description? Keywords can be degree majors, skills, certifications, etc. (recommended)")
            if self.validate() == True:
                self.newKeyWords('Key Words')

        else:
            with open('./utils/keywords.yml') as file:
                document = yaml.full_load(file)
                self.keywords = list(document[0].values())[0]
                print('\nYou were searching for jobs with the following keywords: ' + ', '.join(self.keywords) + ' is this still correct?')
                if self.validate() == False:
                    self.newKeyWords('Key Words')
    
    def checkAntiWordsUtils(self):
        if os.path.exists('./utils/antiwords.yml') == False:
            print("\nWould you like to remove any searchs that have certain antiwords in their description? Antiwords can be things like travel, certain skills, etc.")
            if self.validate() == True:
                self.newKeyWords('Anti Words')

        else:
            with open('./utils/antiwords.yml') as file:
                document = yaml.full_load(file)
                self.keywords = list(document[0].values())[0]
                print('\nYou were searching for jobs with the following keywords: ' + ', '.join(self.keywords) + ' is this still correct?')
                if self.validate() == False:
                    self.newKeyWords('Anti Words')
    
    def newKeyWords(self, typeOfWords):
        if typeOfWords == "keywords":
            self.clean('keywords')
        else:
            self.clean('antiwords')

        words = self.getWords(typeOfWords)

        yaml_words = [{"words": words}]
        with open(r'./utils/' + typeOfWords.strip().lower().replace(" ", "") + '.yml', 'w') as file:
            documents = yaml.dump(yaml_words, file)

    def getWords(self, typeOfWords):
        words = self.typeOfWords(typeOfWords)

        print('\nYou listed: ' + ', '.join(words) + ' is this correct?')
        
        if self.validate() == False:
            self.getKeyWords()

        return words

    def typeOfWords(self, typeWords):
        words = []

        print("\n Please input the " + typeWords.strip().lower().replace(" ", "") + " you want the job to have. Single word inputs are a lot better. \n examples: Wordpress, FP&A, PMP, Salesforce, Angular, etc. \n\nEnter each one, one at a time. Enter \"Done\" when you're finished \n")
        while True:
            keywordsInput = input(typeWords + ": ")
            if keywordsInput.lower() == "done":
                break
            else:
                if "," in keywordsInput.strip():
                    keywordsList = list(filter(None, [x.strip() for x in keywordsInput.split(',')]))
                    words = self.keywords + keywordsList
                else:
                    words.append(keywordsInput.strip())
        if typeWords == "keywords":
            self.keywords = words
        else:
            self.antiwords = words
        return words

    def validate(self):
        while True:
            q = input("(Y or N): ")
            if q.lower() == "y":
                return True
            if q.lower() == "n":
                return False
        
    def clean(self, typ):
        try:
            if typ == "personal":
                os.remove('./utils/personal.yml')
            if typ == "jobs":
                os.remove('./utils/jobs.yml')
            if typ == "experience":
                os.remove('./utils/experience.yml')
            if typ == "keywords":
                os.remove('./utils/keywords.yml')
            if typ == "antiwords":
                os.remove('./utils/antiwords.yml')
        except OSError:
            pass 
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
       return self
