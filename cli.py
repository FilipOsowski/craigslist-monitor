import argparse
monitor = argparse.ArgumentParser(description="Monitors a craigslist search for new items.")
monitor.add_argument("Name", help="The name of the process.")
monitor.add_argument("URL", help="The url of a (customized) craigslist search to be monitored.")
monitor.add_argument("-r", "--renewals", action="store_true", help="Include old posts that are renewed.")
monitor.add_argument("-e", "--exclude-words", nargs="+", metavar="word", default=[], help="Exclude posts that contain these words (not case sensative).")
args = vars(monitor.parse_args())
print(args)

try:
    with open(".pid") as _:
        pass
except FileNotFoundError:
    print(".pid file was not found, creating one...")
    import manager
    import multiprocessing
    manager = multiprocessing.Process(target=manager)
    print("attempting to create manager")
    manager.start()
    print("created manager")
    with open(".pid", "w+") as pid:
        pid.write(manager.pid)
        print("created pid")

with open(".craigslist_monitor_pipe", "w") as pipe:
    pipe.write(args)
# from scraper import create_scraper
# create_scraper(url=args["URL"], name=args["Name"], renewals=args["renewals"], excluded_words=args["exclude_words"])
