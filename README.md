# craigslist-monitor 
A monitor for craigslist searches.  
__*Does not work on Windows.__

The craigslist monitor uses a command line interface to create web scrapers which monitor craigslist searches for new listings. A scraper monitoring a search will check periodically for new listings and output their details into a text file.

## Monitoring a craigslist search

First, create a manager which will oversee active scrapers:
```
cmonitor manager
```

Next, to add a scraper, three things must be specified in the following order:
1. The name of the scraper (used for stopping the scraper).
2. The name of the item to be searched and monitored __or__ the url of a craigslist search.
3. The file that the scraper will output details of new items to.
```
cmonitor add computer_scraper computer output
```
The above example of a scraper would monitor [this](https://craigslist.org/search/sss?query=computer&sort=rel) craigslist search for new listings. There are other options to further customize the scraper listed under ``cmonitor add --help``.

To stop the scraper:
```
cmonitor manager -s computer_scraper
```

Alternatively, to quit both, the manager and any active scrapers:
```
cmonitor manager -q
```

## Commands/Flags
### Manager
* To list the names of all active scrapers: ``cmonitor manager -l``
* To quit the manager and all active scrapers: ``cmonitor manager -q``
* To stop an active scraper: ``cmonitor manager -s <scraper_name>``

### Add
* If a listing contains words specified by --exclude-words, the scraper will not output the details of that listing: ``cmonitor add <scraper details> -e [words...]``
* If --renewals is used, the scraper will output the details of listings that have been renewed (off by default): ``cmonitor add <scraper details> -r``
* The two positive digits following --time-refresh are used with random.randrange to determine how long (in seconds) until the scraper checks for new listing (default is 60 and 180): ``cmonitor add <scraper details> -t 200 300``


## Additional Help

### Add
```
usage: cmonitor add [-h] [-r] [-e word [word ...]] [-t pos_int pos_int]
                    name monitor output

Add an item (craigslist search) to be monitored.

positional arguments:
  name                  The name of the process.
  monitor               The url of a craigslist search or the item name to be
                        monitored.
  output                The file to which items found by the monitor will be
                        written to

optional arguments:
  -h, --help            show this help message and exit
  -r, --renewals        Include old posts that are renewed.
  -e word [word ...], --exclude-words word [word ...]
                        Exclude posts that contain these words (not case
                        sensitive).
  -t pos_int pos_int, --time-refresh pos_int pos_int
                        The two positive integers used with randrange(lower,
                        upper) to determine how long (in seconds) until the
                        scraper checks for new items (first integer must be
                        lower than the second). The default is 60 and 180.
```       
### Manager
```
usage: cmonitor manager [-h] [-q | -l | -s scraper_name]

Starts the manager if issued with no commands.

optional arguments:
  -h, --help            show this help message and exit
  -q, --quit            Quits the manager and all scrapers
  -l, --list            List all the currently running scrapers
  -s scraper_name, --stop scraper_name
                        Stop the named scraper
```








