# Job Scraper

## What is this for?

This job scraper helps find jobs that one is qualified for (by scraping either/both Google or BuiltIn) and matching one's years of experience and skillsets to the job.

Additionally, the scraper can harvest emails of recruiters who work at one's qualified job opportunitiees, and can send them an email with one's resume and custom or prebuilt email templates.

To read more about this, read my article: [How I Used Python To Automate My Job Search](https://jackrothrock.com/how-i-use-python-to-automate-my-job-search/)

Once `main.py` has been run, it will ask for many inputs that pertain to the job search (such as job titles, amount of experience, keywords, location, and where to scrape), and will then commence scraping and emailing.

Credit to austinoboyle for his [linkedin scraping solution](https://github.com/austinoboyle/scrape-linkedin-selenium).

Requires Python3

## How To Use

1. Build a virualenv
    - python 3: `python3 -m venv venv; . ./venv/bin/activate`
2. Install python packages
    - `pip install -r requirements.txt`
3. Run main.py
    - python 3: `python3 main.py`


## Technologies Used
- Python
- Beautifulsoup
- Selenium Web Driver
- Pandas
- Google Mail API
- Yaml

## License 
    Released under MIT.