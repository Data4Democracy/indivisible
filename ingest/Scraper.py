"""Module to scrape data from email and dump in a text file.
"""

def email_scraper(email):
    """This method should consider different types of emails.
    """
    pass

def save_data(raw_data):
    """For now we will save everything in a text file.
    """
    with open('raw_data.txt', 'w') as file:
        file.write(raw_data)

def scrape(email):
    """Scrape email contents and write to file.
    """
    raw_data = email_scraper(email)
    save_data(raw_data)
