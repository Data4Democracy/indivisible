"""
This module will listen to an email address and call Scraper.scrap once it
received email
"""

# from Scraper import scrap
from threading import Thread
import imaplib
# from email import parser
# def listen_notification():
#    pass


class EmailParser(object):
    def __init__(self, host, mailbox, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.mailbox = mailbox

    def GetEmails(self, search_filter='UNSEEN', query='(RFC822)', n=None):
        try:
            conn = imaplib.IMAP4_SSL(self.host)
            conn.login(self.user, self.password)
            conn.select(self.mailbox)
            rv, data = conn.search(None, search_filter)
            if rv != 'OK':
                # TODO timestamp message, or just implement actual logging...
                print('No messages found!\n')
                return
            labels = data[0].split()
            count = len(labels)
            n = count if n is None else n
            n = min(n, count)

            for num in labels[:n]:
                rv, result = conn.fetch(num, query)
                if rv != 'OK':
                    raise RuntimeError('Failed to fetch message {}'
                                       .format(num))

                seen_rv, seen_data = conn.store(num, '+FLAGS', '\\Seen')

                yield result
        finally:
            conn.close()
            conn.logout()


if __name__ == '__main__':
    p = EmailParser('imap.gmail.com', 'inbox', 'USERNAME', 'PASSWORD')
    for msg in p.GetEmails():
        print(msg)
