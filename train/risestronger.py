"""
Scrap RiseStronger event pages and parse event details into relevant fields.
Store details for all events as CSV file.
Combine multiple CSV files into updated table.
"""
import logging


def _get_soup(url):
    """
    Return soup of webpage at url
    """
    import urllib.request
    from bs4 import BeautifulSoup
    #  header for request
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',  #NOQA
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


def _get_months():
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


def extract_details(soup):
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
        if len(set(line.split(' ')).intersection(_get_months())) > 0:
            event_date_time = line
        elif line == event_location:
            continue
        elif line in event_types:
            continue
        else:
            event_organizer = line
    details['DATE_TIME'] = event_date_time
    details['ORGANIZER'] = event_organizer

    logging.debug('Scrapped Data:\n'
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


def _get_event_urls():
    """
    Return URLs of event-pages on risestronger.org website
    """
    import re
    from tqdm import tqdm
    root_url = 'https://risestronger.org'

    def _is_pattern(pattern):
        return (lambda x: x and bool(re.compile(pattern).search(x)))

    def get_num_pages():
        soup = _get_soup(root_url + '/events')
        num_pages = 1
        for a in soup.find_all(href=_is_pattern('^/events\?page=')):
            num_pages = max(num_pages,
                            int(a['href'][len('/events?page='):]))
        return num_pages

    def get_events_on_page(page_num):
        page_url = '{}/events?page={:d}'.format(
            root_url,
            page_num)
        soup = _get_soup(page_url)
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
    event_urls = [root_url + eu for eu in event_urls]
    return list(set(event_urls))


def _test_extract_details(TEST_URLS):
    """
    Test extract_details() on TEST_URLS
    """
    for url in TEST_URLS:
        soup = _get_soup(url)
        details = extract_details(soup)
        print('test_extract_details(): url = {}'.format(url))
        for k, v in details.items():
            print('{: <10s} : {}'.format(k, v))


def scrap(_save_csv=True):
    """
    Scrap risestronger.org for events info.
    Webpages for all events listed on www.risestronger.org/events are scrapped
    and details are extracted into a DataFrame object.

    Parameters
    ----------
    _save_csv : bool
        Save DataFrame as csv to file.

    Returns
    -------
    event_df : pandas.core.frame.DataFrame
        DataFrame object containing info for all events scrapped.
    """
    import urllib.request
    from tqdm import tqdm
    import pandas as pd

    event_urls = _get_event_urls()
    df = pd.DataFrame()

    for url in tqdm(event_urls, desc='Parsing Events'):
        logging.debug('Reading webpage at url {}'.format(url))
        try:
            soup = _get_soup(url)
        except (urllib.error.HTTPError, urllib.error.URLError):
            error_msg = '\nHTTPError: Failure to read {}\n'.format(url)
            logging.error(error_msg)
            tqdm.write(error_msg)
            continue
        except KeyboardInterrupt:
            msg = 'KeyboardInterrupt received. Skipping remaining events.'
            logging.warning(msg)
            return df

        #  get details
        details = extract_details(soup)
        details['URL'] = url
        details['LAST_UPDATED'] = pd.Timestamp('now')  # BUG , tz='US/Pacific')
        df = df.append(details, ignore_index=True)

    return df


def _get_timestamp():
    """
    Return current timestamp.
    """
    import time
    return time.strftime('%Y%m%dT%H%M%S')


def save_csv(events_df, filename=None):
    """
    Save events_df into a CSV file.

    Parameters
    ----------
    events_df : DataFrame
        DataFrame containing info.
    filename : string, default None
        File path, if None is provided the result is returned as a string.
    """
    if filename is None:
        timestamp = _get_timestamp()
        _filename = 'scrapped_data/risestronger_events_' + timestamp + '.csv'
    else:
        _filename = filename

    events_df.to_csv(_filename,
                     index=False)
    logging.info('Saved events DataFrame to {}'.format(_filename))
    if filename is None:
        return _filename


def combine_csv_files(csv_files=None):
    """
    Read CSV files and combine into single DataFrame object.
    Keep only latest versions of each URL.

    Parameters
    ----------
    csv_files : list, default None
        List of path of CSV files to read, if None is provided the CSV files in
        'scrapped_data/' directory are read.

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
        for dirpath, dirnames, fnames in walk('scrapped_data'):
            _CSVs.extend([dirpath + '/' + f for f in fnames
                          if f.lower().endswith('.csv')])
            break
    else:
        _CSVs = csv_files

    #  read CSV files
    events_df_list = []
    for f in _CSVs:
        logging.debug('Reading CSV file {}'.format(f))
        df = pd.read_csv(f)
        logging.debug('Shape = {}'.format(df.shape))
        events_df_list.append(df)

    if len(events_df_list) > 1:
        logging.debug('Combining into single DataFrame...')
        events_df = (events_df_list[0]
                     .append(events_df_list[1:],
                             ignore_index=True)
                     .reset_index(drop=True))
    else:
        events_df = events_df_list[0]

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


if __name__ == '__main__':
    """
    Typical Usage:
        - Scrap website and get latest info
        - Save to CSV file
        - Find all previously saved CSV files and combine into single DataFrame
    """
    logging.basicConfig(level=logging.DEBUG)
    current_events_df = scrap()
    filename = save_csv(current_events_df)
    all_events_df = combine_csv_files()
