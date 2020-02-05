from emailer import Emailer
from init import Init 
import os.path
data = []

def main():
    global data

   
    with Init() as i:
        i.intro()
        i.checkUtils()
    
    # jobs = getJobs()

    # if students:
    #     emails = getEmailsStudents()
    # else:
    #     emails = getEmailsFaculty()
    
    # with Emailer() as email:
    #     success = email.Send(emails)

    # if success:
    #     file = './cu_students_remaining.txt' if students else './cu_research_faculty_remaining.txt'
    #     with open(file, 'w') as fout:
    #         fout.writelines(data[400:])

# def getJobs():
#     if os.path.exists('./files/cu_research_faculty_remaining.txt') == False:
#         with ScraperFaculty() as sf:
#             sf.scrape()
#     return readEmails('./cu_research_faculty_remaining.txt')

# def getEmailsFaculty():
#     if os.path.exists('./cu_research_faculty_remaining.txt') == False:
#         with ScraperFaculty() as sf:
#             sf.scrape()
#     return readEmails('./cu_research_faculty_remaining.txt')

# def getEmailsStudents():
#     if os.path.exists('./cu_students_remaining.txt') == False:
#         cookie = "Change Me To The li_at Cookie!!!"
#         with ScraperStudent(cookie) as ss:
#             ss.scrape()
#     return readEmails('./cu_students_remaining.txt')

# def readEmails(file):
#     global data
#     # I'm going to ignore memory efficiency. 
#     with open(file, 'r') as fin:
#         data = fin.read().splitlines(True)
#     return ', '.join(data[:400]).replace('\n', '').replace('\r', '')


if __name__ == '__main__':
    main()