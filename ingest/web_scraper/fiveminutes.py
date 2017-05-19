import logging
from base_scraper import AbstractWebScraper


class FiveMinutesScraper(AbstractWebScraper):
    _root_url = 'https://tinyletter.com/FiveMinutes'
    _name = 'fiveminutes'

    def get_event_urls(self):
        page_url = '{}/archive?page=1&recs=1000&sort=desc&q='.format(
                self._root_url)
        soup = self.get_soup(page_url)
        event_urls = []
        for a in soup.find_all('a', href=True, class_='message-link'):
            logging.debug('EVENT: {}'.format(a['href']))
            event_urls.append(a['href'])
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
        details = dict()
        details['SOURCE'] = 'FiveMinutes'
        details['NOTES'] = 'Parsed {} for training data'.format(self._root_url)

        details['NAME'] = (soup
                           .find('h1', class_='subject')
                           .get_text('\n', strip=True))

        details['TAGS'] = []
        details['TYPES'] = []
        details['LOCATION'] = None
        details['LOCATION_GMAPS'] = None
        details['SOCIAL'] = []
        details['DATE_TIME'] = (soup
                                .find('div', class_='message-heading')
                                .find('div', class_='date')
                                .get_text(strip=True)
                                )

        details['ORGANIZER'] = (soup
                                .find('div', class_='by-line')
                                .get_text(strip=True)
                                .replace('by ', '', 1))

        body = soup.find('div', class_='message-body')
        for a in body.find_all('a', href=True):
            a.replace_with('[{}]({})'.format(
                a.get_text(strip=True),
                a['href']))
        details['DESCRIPTION'] = body.get_text('\n', strip=True)

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
    logging.basicConfig(level=logging.DEBUG)
    #  init scraper
    scraper = FiveMinutesScraper()
    #  scrap and save current events
    current_events_df = scraper.scrape()
    filename = scraper.save_csv(current_events_df)
    #  combine all events (for training?)
    all_events_df = scraper.combine_csv_files()
