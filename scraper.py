import requests
import random
import time
import sched
from collections import deque
from bs4 import BeautifulSoup
from multiprocessing import Process

scrapers = []


class item_scraper():
    last_item_ids = deque(maxlen=121)
    scheduler = sched.scheduler(time.time, time.sleep)
    item = ""

    def __init__(self, url, options):
        print("Initialized an item_scraper.")
        self.options = options
        self.url = url

        self.update_page()

        self.last_item_ids.extend(
            int(item["data-pid"]) for item in self.get_new_items())
        # For testing
        self.last_item_ids.popleft()

        self.schedule_event()
        self.scheduler.run()

    def schedule_event(self):
        delay = random.randrange(60, 180)
        print("Delaying for", delay)
        self.scheduler.enter(
            delay=delay, priority=1, action=self.check_for_new_items)

    def update_page(self):
        self.soup = BeautifulSoup(requests.get(self.url).text, "html.parser")

    def check_for_new_items(self):
        print("Checking for new items...")

        self.update_page()
        new_items = self.get_new_items()
        new_item = next(new_items)
        new_item_id = int(new_item["data-pid"])

        while new_item_id not in self.last_item_ids:
            self.last_item_ids.appendleft(new_item_id)
            print("Found new item! Id is", new_item_id)
            print(item_properties())
            new_item = next(new_items)
            new_item_id = int(new_item["data-pid"])

        self.schedule_event()

    def get_new_items(self):
        return (item for item in self.soup.find_all(class_="result-row"))

    def complies_to_options(self, properties):
        if self.options["excluded_words"]:
            for word in properties.name.split():
                if word.lower() in self.options["excluded_words"]:
                    print(
                        "Returned False because an excluded word was found in the item name."
                    )
                    return False

        if not self.options["renewals"] and properties.is_repost:
            print("Returned False because the item was a renewal.")
            return False

        print("Returned True because the item complies to the user's options.")
        return True
    
    def parse_item(item)


class item_properties():
    def __init__(self, item_soup):
        self.item_soup = item_soup
        self.parse_item()

    def parse_item(self):
        address_and_name = self.item_soup.find_all("a")[1]

        self.link = address_and_name["href"]
        self.name = address_and_name.text
        self.time = self.item_soup.find(class_="result-date")["title"]
        self.is_repost = self.item_soup.has_attr("data-repost-of")

        self.location = self.find_safely(
            function=self.item_soup.find, class_="result-hood")
        self.price = int(
            self.find_safely(
                function=self.item_soup.find, class_="result-price")[1:])

    def __str__(self):
        return str(
            [self.link, self.name, self.price, self.time, self.location])

    def find_safely(self, function, class_):
        try:
            return function(class_=class_).text
        except AttributeError:
            return "This element was not listed"


def initiate_scraper(url, renewals, excluded_words):
    print("URL =", url, "| renewals =", renewals, "| Excluded words =", excluded_words)

    options = {
        "renewals": renewals,
        "excluded_words": excluded_words,
    }

    scraper_process = Process(target=item_scraper, args=([url, options]))
    scraper_process.start()
    print("Process pid is", scraper_process.pid)
    scrapers.append(scraper_process)

    # print("A scraper was not actually initiated.")
    print("A scraper was successfully initiated")

