import requests
import random
import time
import sched
import atexit
from collections import deque
from smtplib import SMTP
from email import message
from bs4 import BeautifulSoup
from multiprocessing import Process
from selenium import webdriver

scrapers = []

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
chrome = webdriver.Chrome(
    executable_path="",
    chrome_options=options)


def time_this(function):
    def wrapper(argument):
        start = time.time()
        function(argument)
        print("Time- ", (start - time.time()))
        del start

    return wrapper


class item_scraper():
    last_item_ids = deque(maxlen=121)
    scheduler = sched.scheduler(time.time, time.sleep)
    item = ""
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }

    def __init__(self, user, item, options):
        print("Initialized an item_scraper with", item)
        self.item = item
        self.user = user
        self.options = options
        self.url = self.get_url()

        self.update_page()

        self.last_item_ids.extend(
            int(item["data-pid"]) for item in self.get_new_items())
        self.last_item_ids.popleft()

        self.schedule_event()
        self.scheduler.run()

    def get_url(self):
        chrome.get("https://chicago.craigslist.org/d/for-sale/search/sss")

        show_catagories = chrome.find_element_by_class_name("maincats").find_element_by_class_name("closed")
        show_catagories.click()

        catagory_pane = chrome.find_element_by_class_name("search-options")
        catagory_pane.click()

        deselect_all = chrome.find_element_by_class_name("selectall").find_element_by_class_name("catcheck")
        deselect_all.click()

        categories = chrome.find_element_by_class_name("maincats")
        for category in self.options["categories"]:
            print("selecting", category, "...")
            categories.find_element_by_xpath("//a[text()=\"" + category + "\" and @class=\"category\"]/../input").click()

        search_bar = chrome.find_element_by_name("query")
        search_bar.send_keys(self.item)
        search_bar.submit()
        print(chrome.current_url)
        return chrome.current_url

    def schedule_event(self):
        delay = random.randrange(60, 180)
        # delay = random.randrange(1, 5)
        # delay = random.randrange(100, 200)
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
            self.notify_user_with(new_item)
            new_item = next(new_items)
            new_item_id = int(new_item["data-pid"])

        self.schedule_event()

    def get_new_items(self):
        return (item for item in self.soup.find_all(class_="result-row"))

    def notify_user_with(self, item):
        properties = item_properties(item)
        if self.complies_to_options(properties):
            with SMTP(host="smtp.gmail.com", port=587) as smtp_session:
                smtp_session.starttls()
                smtp_session.login("crprojectnotifier@gmail.com", "")

                msg = message.EmailMessage()
                msg.set_content("A new item was found, here are the details-" +
                                str(properties))
                msg["From"] = "crprojectnotifier@gmail.com"
                msg["To"] = self.user
                msg["Subject"] = "New Item Found"

                smtp_session.send_message(msg)

    def complies_to_options(self, properties):
        for word in properties.name.split():
            if word.lower() in self.options["words_to_exclude"]:
                print(
                    "Returned False because an excluded word was found in the item name."
                )
                return False

        if not self.options["renewals"] and properties.is_repost:
            print("Returned False because the item was a renewal.")
            return False

        if not isinstance(properties.price, int):
            if self.options["include_items_without_price"]:
                print("Returned True because the item had no listed price.")
                return True

            print("Returned False because the item had no listed price.")
            return False

        if not self.options["limit"][0] < properties.price < self.options["limit"][1]:
            print(
                "Returned false because the item's price was not within the user's price limits."
            )
            return False
        print("Returned True because the item complies to the user's options.")
        return True


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


def exit():
    chrome.quit()
    print("###################################### EXITED CHROME ########################################")


atexit.register(exit)

if __name__ == "__main__":
    print("Run as main script.")
    p = Process(
        target=item_scraper,
        args=([
            "crprojectnotifier@gmail.com", "computer", {
                "limit": (15, 100),
                "renewals": True,
                "words_to_exclude": ["abc"],
                "include_items_without_price": True,
                "categories": ["arts & crafts", "electronics"]
            }
        ]))
    p.start()


def initiate_scraper(user, item, renewals, price_limits, words_to_exclude,
                     include_items_without_price, categories):
    print("Initiating a scraper with user =", user, "| item =", item,
          "| renewals =", renewals, "| price_limits =", price_limits[0], "<",
          price_limits[1], "| Words to exclude =", words_to_exclude)

    options = {
        "limit": (int(price_limits[0]), int(price_limits[1])),
        "renewals": renewals == "1",
        "words_to_exclude": words_to_exclude,
        "include_items_without_price": include_items_without_price == "1",
        "categories": categories
    }

    scraper_process = Process(
        target=item_scraper, args=([user, item, options]))
    scraper_process.start()
    print("Process pid is", scraper_process.pid)
    scrapers.append(scraper_process)

    print("A scraper was successfully initiated")
