Scrapers implemented as separate classes for each website. These classes inherit from AbstractWebScraper in base_scraper.py

Following websites are currently scraped:
 - [Rise Stronger](https://risestronger.org)
 - [Call To Activism](http://www.calltoactivism.com)
 - [DailyGrabBack](https://www.dailygrabback.com)
 - [Five Minutes](https://tinyletter.com/FiveMinutes)
 - [Two Hours a Week](http://2hoursaweek.org)
 - [Resistance Near Me](https://resistancenearme.org)

To scrape a website, call the scrape() method for the corresponding class.
