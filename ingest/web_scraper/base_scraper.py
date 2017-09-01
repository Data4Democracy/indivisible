import logging


class AbstractWebScraper(object):
    """
    Abstract class that contains functions for scraping action text and
    tags from websites.
    """
    _name = 'abstract'
    _root_url = ''

    def extract_details(self, soup):
        """
        Extract details of an event given the web-page.
        (NOTE: Website-Dependent function; must be implemented by child class)

        Parameters
        ----------
        soup : BeautifulSoup
            Soup of events webpage.

        Returns
        -------
        details : dict
            Dictionary containing event-info.
        """
        raise NotImplemented

    def get_event_urls(self):
        """
        Return URLs of event-pages on website.
        (NOTE: Website-Dependent function; must be implemented by child class)
        """
        raise NotImplemented

    def scrape(self):
        """
        Scrape website for info on all events.
        Details are extracted into a DataFrame object.

        Returns
        -------
        event_df : pandas.core.frame.DataFrame
            DataFrame object containing info for all events scraped.
        """
        import urllib.request
        from tqdm import tqdm
        import random
        import time
        import pandas as pd

        event_urls = self.get_event_urls()
        df = pd.DataFrame()

        for url in tqdm(event_urls, desc='Parsing Events'):
            logging.debug('Reading webpage at url {}'.format(url))
            try:
                time.sleep(random.uniform(1, 3))
                soup = self.get_soup(url)
            except (urllib.error.HTTPError, urllib.error.URLError):
                error_msg = '\nHTTPError: Failure to read {}\n'.format(url)
                logging.error(error_msg)
                continue
            except KeyboardInterrupt:
                msg = 'KeyboardInterrupt received. Skipping remaining events.'
                logging.warning(msg)
                return df

            #  get details
            details = self.extract_details(soup)
            details['URL'] = url
            details['LAST_UPDATED'] = pd.Timestamp('now')
            # TODO Add timezone to LAST_UPDATED ('now', tz='US/Pacific')
            df = df.append(details, ignore_index=True)

        return df

    def save_csv(self, events_df, filename=None):
        """
        Save events_df into a CSV file.

        Parameters
        ----------
        events_df : DataFrame
            DataFrame containing info.
        filename : string, default None
            File path, if None is provided the result is returned as a string.
        """
        import time
        if filename is None:
            timestamp = time.strftime('%Y%m%dT%H%M%S')
            _filename = 'scraped_data/{}_events_{}.csv'.format(
                self._name, timestamp)
        else:
            _filename = filename

        events_df.to_csv(_filename,
                         index=False)
        logging.info('Saved events DataFrame to {}'.format(_filename))
        if filename is None:
            return _filename

    def get_soup(self, url):
        """
        Return soup of webpage at url.
        """
        import urllib.request
        from bs4 import BeautifulSoup
        #  header for request
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',  #NOQA
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  #NOQA
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        #  assemble request
        request = urllib.request.Request(url=url,
                                         data=None,
                                         headers=hdr)
        response = urllib.request.urlopen(request)
        #  get required data
        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')
        return soup

    def combine_csv_files(self, csv_files=None):
        """
        Read CSV files and combine into single DataFrame object.
        Keep only latest versions of each URL.

        Parameters
        ----------
        csv_files : list, default None
            List of path of CSV files to read, if None is provided the CSV
            files in 'scraped_data/' directory are read.

        Returns
        -------
        events_df : DataFrame
            DataFrame object of events from all CSV files.
        """
        from os import walk
        import numpy as np
        import pandas as pd

        #  find files
        if csv_files is None:
            _CSVs = []
            for dirpath, dirnames, fnames in walk('scraped_data'):
                _CSVs.extend([dirpath + '/' + f for f in fnames
                              if f.lower().endswith('.csv')])
                break
        else:
            _CSVs = csv_files

        #  read CSV files
        df_list = []
        for f in _CSVs:
            logging.debug('Reading CSV file {}'.format(f))
            df = pd.read_csv(f)
            logging.debug('Shape = {}'.format(df.shape))
            df_list.append(df)

        if len(df_list) > 1:
            logging.debug('Combining into single DataFrame...')
            events_df = (df_list[0]
                         .append(df_list[1:],
                                 ignore_index=True)
                         .reset_index(drop=True))
        else:
            events_df = df_list[0]

        logging.debug('Finding duplicate events based on URL...')
        is_latest = np.array([True] * events_df.shape[0])
        for key, group in events_df.groupby('URL'):
            if group.shape[0] > 1:
                #  find latest timestamp and mark others for deletion
                latest_ts = group.LAST_UPDATED.max()
                is_latest[group[group.LAST_UPDATED < latest_ts].index] = False

        logging.debug('Dropping {} duplicate events...'.format(
            len(is_latest) - np.sum(is_latest)))
        events_df = (events_df
                     .loc[is_latest]
                     .reset_index(drop=True)
                     .copy(deep=True))
        return events_df

    def _test_extract_details(self, test_urls):
        """
        Test extract_details() on test_urls

        Parameters
        ----------
        test_urls : list-like iteratable
            Contains URLs that should be parsable by extract_details()

        Returns
        -------
        details_list : list
            Output of calls to extract_details
        """
        details_list = []
        for url in test_urls:
            print('test_extract_details(): url = {}'.format(url))
            soup = self.get_soup(url)
            details = self.extract_details(soup)
            for k, v in details.items():
                print('{: <10s} : {}'.format(k, v))
            print('-' * 80)
            details_list.append(details)
        return details_list
