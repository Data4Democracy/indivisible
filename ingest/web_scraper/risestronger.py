from base_scraper import AbstractWebScraper


class RiseStrongerScraper(AbstractWebScraper):
    """
    Scrape RiseStronger event pages and parse event details
    into relevant fields.
    """
    _name = 'risestronger'
    _root_url = 'https://risestronger.org'

    def _get_months(self):
        """
        Return set of various representations of the month name.
        """
        MONTHS = set()
        MONTHS_LIST = ['January', 'February', 'March', 'April',
                       'May', 'June', 'July', 'August',
                       'September', 'October', 'November', 'December']
        for m in MONTHS_LIST:
            MONTHS.add(m)
            MONTHS.add(m.upper())
            MONTHS.add(m[:3])
            MONTHS.add(m[:3].upper())
        return MONTHS

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
        details['SOURCE'] = 'risestronger.org'
        details['NOTES'] = 'Parsed www.risestronger.org for training data'

        # Event Name
        event_name = soup.h2.get_text(strip=True)
        details['NAME'] = event_name

        # Tags
        event_tags = []
        event_types = []
        event_location_gmaps = None
        event_location = None
        d = soup.find('div', id='page-banner')
        for a in d.find_all('a'):
            if a['href'][:12] == '/events?tags':
                event_tags.append(a.get_text())
            elif a['href'][:12] == '/events?type':
                event_types.append(a.get_text())
            elif a['href'].startswith('https://www.google.com/maps'):
                event_location = a.get_text()
                event_location_gmaps = a['href']
        details['TAGS'] = event_tags
        details['TYPES'] = event_types
        details['LOCATION'] = event_location
        details['LOCATION_GMAPS'] = event_location_gmaps

        # Main
        d = soup.find('div', id='content')
        # External Links
        event_links = []
        buttons = d.find('p', **{'class': 'center'})
        for a in buttons.find_all('a', href=True):
            if len(a['href']) == 0 or a['href'][0] == '/':
                continue
            event_links.append(a['href'])
        details['SOCIAL'] = event_links

        # Main Text
        t = buttons.find_next_sibling('p')
        event_description = t.get_text('\n').encode('utf-8')
        details['DESCRIPTION'] = event_description

        # Timing
        event_date_time = None
        event_organizer = None
        d = soup.find('div', 'subtitle')
        subtitle = d.get_text('\n', strip=True)
        for line in subtitle.split('\n'):
            if len(set(line.split(' ')).intersection(self._get_months())) > 0:
                event_date_time = line
            elif line == event_location:
                continue
            elif line in event_types:
                continue
            else:
                event_organizer = line
        details['DATE_TIME'] = event_date_time
        details['ORGANIZER'] = event_organizer

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

    def get_event_urls(self):
        """
        Return URLs of event-pages on website.
        """
        import re
        from tqdm import tqdm

        def _is_pattern(pattern):
            return (lambda x: x and bool(re.compile(pattern).search(x)))

        def get_num_pages():
            soup = self.get_soup(self._root_url +
                                 '/events')
            num_pages = 1
            for a in soup.find_all(href=_is_pattern('^/events\?page=')):
                num_pages = max(num_pages,
                                int(a['href'][len('/events?page='):]))
            return num_pages

        def get_events_on_page(page_num):
            page_url = '{}/events?page={:d}'.format(
                self._root_url,
                page_num)
            soup = self.get_soup(page_url)
            event_urls = []
            filter_strings = ['^/events/map$',
                              '^/events/map\?page=',
                              '^/events/new$']
            is_non_event = _is_pattern('|'.join(filter_strings))
            for a in soup.find_all(href=_is_pattern('^/events/')):
                if is_non_event(a['href']):
                    continue
                event_urls.append(a['href'])
            return event_urls

        event_urls = []
        num_pages = get_num_pages()
        for page_num in tqdm(range(1, num_pages + 1), desc='Finding Events'):
            event_urls.extend(get_events_on_page(page_num))

        #  append root url as prefix
        event_urls = [self._root_url + eu for eu in event_urls]
        return list(set(event_urls))


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
    scraper = RiseStrongerScraper()
    #  scrap and save current events
    current_events_df = scraper.scrape()
    filename = scraper.save_csv(current_events_df)
    #  combine all events (for training?)
    all_events_df = scraper.combine_csv_files()
