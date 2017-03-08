""""'
Module to scrap data from email and dump in a text file
"""""

"""
This method should consider different types of emails
"""


def email_scraper(email):
    pass


"""
For now we will save everything in text file
"""


def save_data(rawData):
    with open('raw_data.txt', 'w') as file:
        file.write('rawData')


def scrap(email):
    rawData = email_scraper(email)
    save_data(rawData)
