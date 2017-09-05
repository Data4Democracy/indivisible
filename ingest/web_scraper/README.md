Following websites are currently scraped:
 - [Rise Stronger](https://risestronger.org)
 - [Call To Activism](http://www.calltoactivism.com)
 - [DailyGrabBack](https://www.dailygrabback.com)
 - [Five Minutes](https://tinyletter.com/FiveMinutes)
 - [Two Hours a Week](http://2hoursaweek.org)
 - [Resistance Near Me](https://resistancenearme.org)

Scrapers for all websites have been implemented as separate sub-classes of BaseWebScraper.
BaseWebScraper (implemented in basewebscraper.py) defines methods common to all sub-classes.
All sub-classes must implement extract_details() and event_urls() methods according to the website they scrape.
To scrape a website, call the scrape() method for the corresponding sub-class.

All websites except ResistanceNearMe can be scraped by parsing the DOM with [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/).
ResistanceNearMe uses client-side javascript to load the events from a firebase DB, hence [Selenium](http://docs.seleniumhq.org/) is used for scraping.
