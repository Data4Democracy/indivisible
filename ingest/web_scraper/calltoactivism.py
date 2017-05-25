from base_scraper import AbstractWebScraper
import logging


class CallToActivismScraper(AbstractWebScraper):
    _name = 'calltoactivism'
    _root_url = 'http://www.calltoactivism.com'

    def get_event_urls(self):
        url = 'http://www.calltoactivism.com/dailycalltoactions.html'
        soup = self.get_soup(url)
        event_urls = []
        for h in soup.find_all('h2', class_='wsite-content-title'):
            a = h.find('a', href=True)
            if a is not None:
                eu = a['href']
                #  append root url as prefix
                if not eu.startswith(self._root_url):
                    eu = self._root_url + eu
                event_urls.append(eu)

        return list(set(event_urls))

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
        details['SOURCE'] = 'calltoactivism.com'
        details['NOTES'] = 'Parsed www.calltoactivism.com for training data'

        d = (soup
             .find('div',
                   class_='wsite-section-content'))

        details['NAME'] = (d.find('h2')
                           .get_text('\n', strip=True)
                           .upper()
                           .split('\n')
                           [-1])

        details['TAGS'] = []
        details['TYPES'] = []
        details['LOCATION'] = None
        details['LOCATION_GMAPS'] = None
        details['SOCIAL'] = []
        details['DATE_TIME'] = (d.find('h2')
                                .get_text('\n', strip=True)
                                .split('\n')
                                [1])
        details['ORGANIZER'] = None

        #  captialize titles
        for t in d.find_all('h2', class_='wsite-content-title'):
            t.replace_with('{}\n'.format(t.get_text('\n', strip=True).upper()))

        #  hyperlinks to markdown links
        for a in d.find_all('a', href=True):
            a.replace_with('[{}]({})'.format(
                    a.get_text(strip=True), a['href']))

        #  list to markdown list
        for li in d.find_all('li'):
            li.replace_with('- {}'.format(li.get_text(strip=True)))

        details['DESCRIPTION'] = (d.get_text('\n', strip=True))
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
    scraper = CallToActivismScraper()
    #  scrap and save current events
    current_events_df = scraper.scrape()
    filename = scraper.save_csv(current_events_df)
    #  combine all events (for training?)
    all_events_df = scraper.combine_csv_files()
