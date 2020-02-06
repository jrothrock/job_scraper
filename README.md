# Job Scraper

## What is this for?

This job scraper is to help eliminate one from the mass crowd of those applying to applications. Instead, this meant to email the recruiters and managers of the potential postion.

The scraper can check for jobs on BuiltIn that match a specific title(s) one is looking for, a range of experience they have, as well as keywords (such as skills, degrees, etc) that is in the job description.

To read more about this, read my article: [How I found my first job out of college with an ad spend of $300](https://jackrothrock.com/how-i-found-my-first-job-out-of-college/)

Once `main.py` has been run, it will ask for many inputs that pertain to the job search (such as job titles, amount of experience, keywords, location, and where to scrape), and will then commence scraping and emailing.

Credit to austinoboyle for his [linkedin scraping solution](https://github.com/austinoboyle/scrape-linkedin-selenium).

## How To Use

1. Build a virualenv
    - python 2: `virtualenv venv --distribute; source venv/bin/activate`
    - python 3: `python3 -m venv venv; . ./venv/bin/activate`
2. Install python packages
    - `pip install -r requirements.txt`
3. Run main.py
    - python 2: `python main.py`
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