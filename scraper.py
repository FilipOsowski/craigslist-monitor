import requests
import sys
import random
from time import sleep
from collections import deque
from lxml import html


class item_scraper():
    last_item_ids = deque(maxlen=121)
    item = ""

    def __init__(self, monitor, options, should_quit):
        log("Initialized an item_scraper.")
        self.options = options
        if monitor[:7] == "https:":
            self.monitor_url = monitor
        else:
            response = requests.get("https://www.craigslist.org")


            self.monitor_url = response.url + "/search/sss?query=" + monitor + "&sort=rel"
        log(self.monitor_url)
        self.should_quit = should_quit

        self.update_page()
        self.last_item_ids.extend(
            int(item.xpath("./@data-pid")[0]) for item in self.get_new_items())
        # For testing
        self.last_item_ids.popleft()
        self.check_for_new_items()

    def wait(self, seconds):
        log("Waiting for", seconds, "seconds..")
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
            new_items = self.get_new_items()
            new_item = next(new_items)
            new_item_id = int(new_item.xpath("./@data-pid")[0])

            while new_item_id not in self.last_item_ids:
                self.last_item_ids.appendleft(new_item_id)
                log("Found new item! Id is", new_item_id)
                self.parse_item(new_item)
                new_item = next(new_items)
                new_item_id = int(new_item.xpath("./@data-pid")[0])

            if self.wait(random.randrange(60, 180)):
                import os
                log_file.close()
                break

    def get_new_items(self):
        return (item for item in self.parsed_html.xpath("//li[@class=\"result-row\"]"))

    def complies_to_options(self, properties):
        if self.options["exclude_words"]:
            for word in properties.name.split():
                if word.lower() in self.options["exclude_words"]:
                    log(
                        "Returned False because an excluded word was found in the item name."
                    )
                    return False

        if not self.options["renewals"] and properties.is_repost:
            log("Returned False because the item was a renewal.")
            return False

        log("Returned True because the item complies to the user's options.")
        return True
    
    def parse_item(self, item):
            link = item.xpath("./a/@href")[0]
            name = item.xpath("(.//a)[2]/text()")[0]
            time = item.xpath(".//time/@title")[0]
            is_renewal = bool(item.xpath("./@data-repost-of"))
            price = item.xpath("(.//span[@class=\"result-price\"])[1]/text()")
            price = price[0] if price else "Price not listed"
            location = item.xpath(".//span[@class=\"result-hood\"]/text()")
            location = location[0] if location else "Location not listed"
            log(link, name, time, is_renewal, price, location)


def log(*args):
    print(*args)
    log_file.flush()

def create_scraper(monitor, renewals, exclude_words, should_quit, output):
    global log_file
    log_file = open(output, "w+")
    sys.stdout = log_file
    sys.stderr = log_file
    log("AFTER")

    options = {
        "renewals": renewals,
        "exclude_words": exclude_words,
    }

    item_scraper(monitor, options, should_quit)

