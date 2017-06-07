from base_scraper import AbstractWebScraper


class DailyGrabBackScraper(AbstractWebScraper):
    _name = 'dailygrabback'
    _root_url = 'https://www.dailygrabback.com'

    def get_event_urls(self):

        def get_events_on_page(soup):
            event_urls = []
            for art in soup.find_all('article'):
                a = (art
                     .find('header')
                     .find('h1')
                     .find('a', href=True))
                logging.debug('EVENT: {}'.format(a['href']))
                event_urls.append(a['href'])
            return event_urls

        def get_older_page(soup):
            try:
                older = (soup
                         .find('nav', class_='pagination clear')
                         .find('div', class_='older')
                         .find('a', href=True))
            except (AttributeError, TypeError):
                return None
            return older['href'] if older is not None else None

        next_page_url = '/todays-grab-1/'
        event_urls = []
        while next_page_url is not None:
            logging.debug('Scraping ' + next_page_url)
            soup = self.get_soup(self._root_url + next_page_url)
            event_urls.extend(get_events_on_page(soup))
            next_page_url = get_older_page(soup)

        event_urls = [self._root_url + e for e in event_urls]
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
        details['SOURCE'] = 'dailygrabback.com'
        details['NOTES'] = 'Parsed www.dailygrabback.comfor training data'

        art = soup.find('article')

        # Event Name
        event_name = (art
                      .find('header')
                      .find('h1')
                      .get_text(strip=True))
        details['NAME'] = event_name

        # Event Date Time
        event_datetime = (art
                          .find('header')
                          .find('div', class_='entry-dateline')
                          .get_text(strip=True))
        details['DATE_TIME'] = event_datetime

        # Event Type
        try:
            event_types = (art
                           .find('header')
                           .find('span', class_='entry-category')
                           .get_text('\n', strip=True)
                           .split('\n'))
        except AttributeError:
            event_types = None

        try:
            event_tags = [a.get_text()
                          for a in art.find_all('a',
                                                href=re.compile('\?tag='))]
        except AttributeError:
            event_tags = None

        details['TYPES'] = event_types
        details['TAGS'] = event_tags

        # Main Text
        main = (art
                .find('div',
                      class_='entry-content e-content'))
        # hyperlink to markdown link
        for a in main.find_all('a', href=True):
            a.replace_with('[{}]({})'.format(
                a.get_text(strip=True), a['href']))

        description = (main
                       .get_text('\n', strip=True))
        details['DESCRIPTION'] = description

        # External Links
        event_links = [a['href']
                       for a in art.find_all(
                           'a',
                           target='_blank',
                           href=re.compile('facebook.com/events'))]
        details['SOCIAL'] = event_links

        # Location
        try:
            loc_lat = (soup
                       .find('meta', property="og:latitude")
                       ['content'])
            loc_lon = (soup
                       .find('meta', property="og:longitude")
                       ['content'])
            details['LOCATION_GMAPS'] = 'www.google.com/maps?q={},{}'.format(
                loc_lat, loc_lon)
        except:
            details['LOCATION_GMAPS'] = None

        details['ORGANIZER'] = None
        details['LOCATION'] = None

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
    scraper = DailyGrabBackScraper()
    #  scrap and save current events
    current_events_df = scraper.scrape()
    filename = scraper.save_csv(current_events_df)
    #  combine all events (for training?)
    all_events_df = scraper.combine_csv_files()
