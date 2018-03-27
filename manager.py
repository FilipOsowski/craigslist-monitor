import os
from scraper import item_scraper
def start():
    print("The manager was run.")
    print("a")
    try:
        os.mkfifo(".craigslist_monitor_pipe")
    except FileExistsError:
        pass
    print("b")
    scrapers = []
    while True:
        print("stuck?")
        with open(".craigslist_monitor_pipe", "r") as pipe:
            print("something was posted:", pipe.read())

    os.remove(".craigslist_monitor_pipe")
    os.remove(".pid")
start()
