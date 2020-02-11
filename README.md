# Job Scraper

## What is this for?

This job scraper helps find jobs that one is qualified for (by scraping either/both Google or BuiltIn) and matching one's years of experience and skillsets to the job.

Additionally, the scraper can harvest emails of recruiters who work at one's qualified job opportunitiees, and can send them an email with one's resume and a custom/prebuilt email templates.

To read more about this, read my article: [How I Used Python To Automate My Job Search](https://jackrothrock.com/how-i-use-python-to-automate-my-job-search/)

Once `main.py` has been run, it will ask for many inputs that pertain to the job search (such as job titles, amount of experience, keywords, location, and where to scrape), and will then commence scraping and emailing.

Credit to austinoboyle for his [linkedin scraping solution](https://github.com/austinoboyle/scrape-linkedin-selenium).

Requires Python3

## How To Use
A. Download the program (only works on Mac and Linux)
1. Download:  https://www.dropbox.com/s/77mwxqxh54ozsxa/job_scraper.zip?dl=0

2. Then open the terminal and run:
    - `find ~/downloads/ -type f -name 'job_scraper.command' | xargs chmod 755`
        - You may have to go into security on Mac and allow the file to run.


B. Build the program:

1. Build a virualenv
    - python 3: `python3 -m venv venv; . ./venv/bin/activate`
2. Install python packages
    - `pip install -r requirements.txt`
3. Run main.py
    - python 3: `python3 main.py`


Link to instructional video [https://www.youtube.com/watch?v=RvCyLQK7VMo](https://www.youtube.com/watch?v=RvCyLQK7VMo)

## Things to note:
Honestly, I really just built this for myself and decided to throw in a few more hours so that my buddies can use it. I have zero interest in pursuing this much further (unless I need to for my own job search). So if there's a bug or feature, I probably won't work on it

In order to verify email addresses, it will require either a hunter.io account (highly advised) or a debounce.io account. It can still scrape email addresses without these, but it may result in more bounced sends, and potentially marking your email as junk.

Also, when verifying your email, you will be met with a "This app isn't verified" page. Click "advanced", and then "Go to Quickstart (unsafe)". See video for more details.


## Technologies Used
- Python
- Beautifulsoup
- Selenium Web Driver
- Pandas
- Google Mail API
- Hunter.io
- Debounce.io
- Yaml

## License 
    Released under MIT.