from bs4 import BeautifulSoup
from base_scraper import AbstractWebScraper
import logging


class ResistanceNearMeScraper(AbstractWebScraper):
    """
    Scraper class for resistancenearme.org

    Needs selenuim to load the webpage, so this class Implements its own
    scrape() method, overriding the scrape() method from
    AbstractWebScraper.
    """
    _name = 'resistancenearme'
    _root_url = 'https://resistancenearme.org'

    def get_event_urls(self):
        raise NotImplemented

    def extract_details(self, soup):
        """
        Extract details of an event given the web-page.

        Parameters
        ----------
        soup : BeautifulSoup
            Soup of events webpage.

        Returns
        -------
        details : dict
            Dictionary containing event-info.
        """
        details = dict()
        details['SOURCE'] = 'resistancenearme.org'
        details['NOTES'] = ('Parsed {} for training data'
                            .format(self._root_url))

        event_url = soup.find('a', target='_self')
        event_url = None if event_url is None else event_url['href']
        details['URL'] = self._root_url + '/' + event_url

        meta = soup.find('ul')

        def read_meta(class_name, missing_value=None):
            obj = meta.find(class_=class_name)
            if obj is None:
                return missing_value
            else:
                return obj.getText()

        e_venue = read_meta('event-venue')
        e_address = read_meta('event-address')
        e_date = read_meta('event-date', '')
        e_time = read_meta('event-time', '')

        details['ORGANIZER'] = e_venue
        details['LOCATION'] = e_address
        details['DATE_TIME'] = e_date + e_time

        event_name = soup.find(class_='event-name',
                               **{'data-value': True})
        event_type = soup.find(class_='event-type',
                               **{'data-value': True})
        event_name = '' if event_name is None else event_name['data-value']
        event_type = '' if event_type is None else event_type['data-value']
        description = soup['data-content']

        details['NAME'] = event_name
        details['TAGS'] = [event_type]
        details['DESCRIPTION'] = description

        #  Missing info
        details['TYPES'] = []
        details['LOCATION_GMAPS'] = None
        details['SOCIAL'] = []

        logging.debug('Scraped Data:\n'
                      'Source: {SOURCE}\n'
                      'Notes: {NOTES}\n'
                      'Name: {NAME}\n'
                      'Tags: {TAGS}\n'
                      'Types: {TYPES}\n'
                      'Location: {LOCATION_GMAPS} \t| {LOCATION}\n'
                      'Social Links: {SOCIAL}\n'
                      'Description:\n{DESCRIPTION}\n'
                      'Date/Time: {DATE_TIME}\n'
                      'Organizer: {ORGANIZER}\n'
                      'URL: {URL}\n'.format(**details))
        return details

    def scrape(self):
        """
        Scrape website for info on all events.
        Details are extracted into a DataFrame object.

        Returns
        -------
        event_df : pandas.core.frame.DataFrame
            DataFrame object containing info for all events scraped.
        """
        from selenium import webdriver
        import time
        import pandas as pd
        from tqdm import tqdm
        browser = webdriver.PhantomJS()
        browser.set_window_size(1120, 550)
        browser.get(self._root_url)
        # Allow the page to load completely
        # before we start locating elements in the DOM.
        from selenium.webdriver.support.ui import WebDriverWait

        def custom_condition(driver):
            import time
            time.sleep(7)
            return True

        WebDriverWait(browser, 10).until(custom_condition)
        # first need to click on dropdown-toggle to expand it
        dropdowns = browser.find_elements_by_class_name("dropdown-toggle")
        event_dd = dropdowns[3]
        event_dd.click()
        # next click on every event category in dropdown
        el = browser.find_elements_by_xpath('//a[@data-filter="meetingType"]')
        for element in el:
            time.sleep(3)
            element.click()
            time.sleep(3)
            event_dd.click()
        # create html parser from this webpage now that events are listed
        s = BeautifulSoup(browser.page_source, 'html.parser')
        # finds all events
        events = s.find_all(class_='event-row')
        df = pd.DataFrame()
        # for every event, append info to the proper list
        for event_soup in tqdm(events, desc='Parsing Events'):
            details = self.extract_details(event_soup)
            details['LAST_UPDATED'] = pd.Timestamp('now')
            df = df.append(details, ignore_index=True)

        return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #  init scraper
    scraper = ResistanceNearMeScraper()
    #  scrap and save current events
    current_events_df = scraper.scrape()
    filename = scraper.save_csv(current_events_df)
    #  combine all events (for training?)
    all_events_df = scraper.combine_csv_files()
