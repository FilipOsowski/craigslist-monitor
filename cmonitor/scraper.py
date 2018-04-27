import requests
import sys
import random
from time import sleep
from collections import deque
from lxml import html


# The class that handles craigslist item monitoring and parsing.
class item_scraper():

    # The last_item_ids que stores existing item ids to determine whether an
    # item is new.
    last_item_ids = deque(maxlen=121)

    def __init__(self, monitor, options, should_quit):
        log("Created a scraper.")
        self.options = options

        # If the user specifies an item name instead of a url, requests gets
        # the default craigslist and is redirected according to the user's
        # location. The resulting url and the item name are used to create
        # a craigslist search url.
        if monitor[:7] == "https:":
            self.monitor_url = monitor
        else:
            response = requests.get("https://www.craigslist.org")
            self.monitor_url = response.url + "/search/sss?query=" + monitor + "&sort=rel"
        self.should_quit = should_quit

        # Gets initial results of craigslist search and stores all existing
        # item ids.
        self.update_page()
        self.last_item_ids.extend(
            int(item.xpath("./@data-pid")[0]) for item in self.get_new_items())

        # For testing
        # self.last_item_ids.popleft()

        self.check_for_new_items()

    # Waits the specified amount of seconds in intervals of one second. After
    # each second, the should_quit event is checked. If the event is set, the
    # wait function returns True scraper main loop is exited. Else, the wait
    # function returns False after it has waited out the specified amount of
    # seconds and the scraper's main loop continues.
    def wait(self, seconds):
        for _ in range(seconds):
            sleep(1)
            if self.should_quit.is_set():
                return True
        else:
            return False

    def update_page(self):
        self.parsed_html = html.fromstring(requests.get(self.monitor_url).text)

    def check_for_new_items(self):
        while True:
            self.update_page()

            # All unprocessed item ids are stored in relation to the html that
            # contains their data.
            new_items = self.get_new_items()
            new_item = next(new_items)
            new_item_id = int(new_item.xpath("./@data-pid")[0])

            # If the scraper finds a new item id and the item's properties
            # comply to the user's options, the scraper logs the item's details
            # and proceeds to check the next item.
            while new_item_id not in self.last_item_ids:
                self.last_item_ids.appendleft(new_item_id)
                properties = self.parse_item(new_item)

                if self.complies_to_options(properties):
                    log("Found new item-", properties)

                new_item = next(new_items)
                new_item_id = int(new_item.xpath("./@data-pid")[0])

            # If the scraper does not receive a signal to quit, it proceeds to
            # check for new items.
            if self.wait(
                    random.randrange(self.options["refresh"][0],
                                     self.options["refresh"][1])):
                log("Stopped scraper.")
                log_file.close()
                break

    # Returns a generator that upon each iteration returns a new item from the
    # craigslist html.
    def get_new_items(self):
        return (
            item
            for item in self.parsed_html.xpath("//li[@class=\"result-row\"]"))

    # Checks to see if the item's properties (name and renewal status) comply
    # to the user's settings.
    def complies_to_options(self, properties):
        if self.options["exclude_words"]:
            for word in properties["name"].split():
                if word.lower() in self.options["exclude_words"]:
                    return False

        if not self.options["renewals"] and properties["is_renewal"]:
            return False

        return True

    # Parses craigslist html of a specific item for its properties.
    def parse_item(self, item):
        link = item.xpath("./a/@href")[0]
        name = item.xpath("(.//a)[2]/text()")[0]
        time = item.xpath(".//time/@title")[0]
        is_renewal = bool(item.xpath("./@data-repost-of"))

        price = item.xpath("(.//span[@class=\"result-price\"])[1]/text()")
        price = price[0] if price else "Price not listed"
        location = item.xpath(".//span[@class=\"result-hood\"]/text()")
        location = location[0] if location else "Location not listed"

        properties = {
            "name": name,
            "price": price,
            "location": location,
            "time": time,
            "link": link,
            "is_renewal": is_renewal
        }
        return properties


# Flushes the stdout of the scraper (a file) so that output is live.
def log(*args):
    print(*args)
    log_file.flush()


# Interface for creating the scraper.
def create_scraper(monitor, renewals, exclude_words, should_quit, output,
                   time_refresh):
    import os
    global log_file

    # Uses the specified file output for the stdout and stderr of the scraper.
    log_file = open(os.path.join(os.getcwd(), output), "w+")
    sys.stdout = log_file
    sys.stderr = log_file

    options = {
        "renewals": renewals,
        "exclude_words": exclude_words,
        "refresh": time_refresh
    }

    item_scraper(monitor, options, should_quit)
