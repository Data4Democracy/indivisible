"""
This module will listen to an email address and call Scraper.scrap once it
received email
"""

from Scraper import scrap
import Thread
import poplib
from email import parser
# def listen_notification():
#    pass


class EmailParser(object):
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def GetEmails(self):
        pop_conn = poplib.POP3_SSL(self.host)
        pop_conn.user(self.user)
        pop_conn.pass_(self.password)
        msg_count = len(pop_conn.list()[1])
        messages = []
        p = parser.Parser()
        for i in range(1, msg_count + 1):
            msg = '\n'.join(pop_conn.retr(i)[1])
            messages.push(p.parsestr(msg))
        pop_conn.quit()
        return messages


class EmailMonitor(Thread):
    def __init__(self, event, scrapeFunction, emailParser):
        Thread.__init__(self)
        self.stopped = event
        self.scrape = scrapeFunction
        self.emailParser = emailParser

    def run(self):
        while not self.stopped.wait(3600.0):
            messages = self.emailParser.GetEmails()
            for msg in messages:
                self.scrape(msg)


if __name__ == '__main__':
    p = EmailParser('pop.gmail.com', 'indivisible_bot', '!(ggL"JDF=6E@XbF')
    EmailMonitor(None, scrap, p)
