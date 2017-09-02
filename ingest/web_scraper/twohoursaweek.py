from basewebscraper import BaseWebScraper


class TwoHoursAWeekScraper(BaseWebScraper):
    _name = 'twohoursaweek'
    _root_url = 'http://2hoursaweek.org'

    def get_event_urls(self):
        page_url = 'http://2hoursaweek.org'
        soup = self.get_soup(page_url)
        event_urls = []
        for art in soup.find_all('article', class_=True):
            read_more = (art
                         .find('main')
                         .find('a',
                               href=True,
                               class_='read-more action-link'))
            logging.debug('EVENT: {}'.format(read_more['href']))
            event_urls.append(read_more['href'])
        return event_urls

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
        import re
        details = dict()
        details['SOURCE'] = '2hoursaweek.org'
        details['NOTES'] = 'Parsed www.2hoursaweek.org for training data'

        art = soup.find('article',
                        class_=True)
        main = art.find('main')
        action_number = (art
                         .find('div', class_='number')
                         .get_text())

        # Event Name
        event_name = (main
                      .find('h3').
                      get_text('\n'))
        details['NAME'] = event_name

        # Event Type
        event_types = art['class']
        details['TYPES'] = [event_types[0]]
        details['TAGS'] = [action_number] + event_types[1:]

        # External Links
        event_links = [a['href']
                       for a in art.find_all(
                           'a',
                           target='_blank',
                           href=re.compile('facebook.com/events'))]
        details['SOCIAL'] = event_links

        # Main Text
        for a in main.find_all('a', href=True):
            a.replace_with('[{}]({})'.format(
                a.get_text(strip=True), a['href']))

        description = (main
                       .get_text('\n', strip=True))
        details['DESCRIPTION'] = description

        details['DATE_TIME'] = None
        details['ORGANIZER'] = None
        details['LOCATION'] = None
        details['LOCATION_GMAPS'] = None

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
                      'Organizer: {ORGANIZER}\n'.format(**details))

        return details


if __name__ == '__main__':
    """
    Typical Usage:
        - Scrape website and get latest info
        - Save to CSV file
        - Find all previously saved CSV files and combine into single DataFrame
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    #  init scraper
    scraper = TwoHoursAWeekScraper()
    #  scrap and save current events
    current_events_df = scraper.scrape()
    filename = scraper.save_csv(current_events_df)
    #  combine all events (for training?)
    all_events_df = scraper.combine_csv_files()
