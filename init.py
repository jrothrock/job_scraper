import time
import os.path
import yaml

class Init(object):
    def __init__(self):
        self.jobs = []

    def intro(self):
        time.sleep(0.5)
        print("\n\nWelcome to the job scraper!\n\n")
        time.sleep(1.5)
    
    def checkUtils(self):
        if os.path.exists('./utils/jobs.yml') == False:
            self.new()
        else:
            with open('./utils/jobs.yml') as file:
                document = yaml.full_load(file)
                try:
                    self.jobs = list(document[0].values())[0]
                    print('You were searching for: ' + ', '.join(self.jobs) + ' is this still correct?')
                    if self.validateJobs() == False:
                        self.new()
                except Exception as e: print(e)


    def new(self):
        self.clean()

        self.typeOfJobs()

        yaml_jobs = [{"Jobs": self.jobs}]
        with open(r'./utils/jobs.yml', 'w') as file:
            documents = yaml.dump(yaml_jobs, file)

    def typeOfJobs(self):
        self.getJobs()
        
        print('\nYou listed: ' + ', '.join(self.jobs) + ' is this correct?')
        
        if self.validateJobs() == False:
            self.typeOfJobs()

    def validateJobs(self):
        while True:
            q = input("(Y or N): ")
            if q.lower() == "y":
                return True
            if q.lower() == "n":
                return False

    def getJobs(self):
        self.jobs = []
        print("What type of jobs are looking for? Enter one at a time. Type \"Done\" when you're finished")
        while True:
            text = input("Job Name: ")
            if text.lower() == "done":
                break
            else:
                self.jobs.append(text)
        
    def clean(self):
        try:
            os.remove('./utils/conf.yml')
        except OSError:
            pass 
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        return self