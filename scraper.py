import requests
import random
import time
import sched
import pprint
from collections import deque
from lxml import html
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
            int(item.xpath("./@data-pid")[0]) for item in self.get_new_items())
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
        self.parsed_html = html.fromstring(requests.get(self.url).text)

    def check_for_new_items(self):
        print("Checking for new items...")

        self.update_page()
        new_items = self.get_new_items()
        new_item = next(new_items)
        new_item_id = int(new_item.xpath("./@data-pid")[0])

        while new_item_id not in self.last_item_ids:
            self.last_item_ids.appendleft(new_item_id)
            print("Found new item! Id is", new_item_id)
            # print(item_properties())
            self.parse_item(new_item)
            new_item = next(new_items)
            new_item_id = int(new_item.xpath("./@data-pid")[0])

        self.schedule_event()

    def get_new_items(self):
        return (item for item in self.parsed_html.xpath("//li[@class=\"result-row\"]"))

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
    
    def parse_item(self, item):
            link = item.xpath("./a/@href")[0]
            name = item.xpath("(.//a)[2]/text()")[0]
            time = item.xpath(".//time/@title")[0]
            is_renewal = bool(item.xpath("./@data-repost-of"))
            location = item.xpath(".//span[@class=\"result-hood\"]/text()")[0]
            price = item.xpath("(.//span[@class=\"result-price\"])[1]/text()")[0]
            pprint.pprint({"link": link, "name": name, "time": time, "is_renewal": is_renewal, "location": location, "price": price}, indent=4, width=120)


def initiate_scraper(url, name, renewals, excluded_words):
    print("URL =", url, "| renewals =", renewals, "| Excluded words =", excluded_words, "| Name =", name)

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

if __name__ == "__main__":
    initiate_scraper("https://chicago.craigslist.org/search/sss?query=laptop&sort=rel", True, [])
