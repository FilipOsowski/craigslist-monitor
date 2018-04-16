import os
from daemon import DaemonContext
from sys import exit
import atexit

log_file, pid_file, pipe = (None for _ in range(3))
def main():
    from time import sleep
    from ast import literal_eval
    from scraper import create_scraper
    import multiprocessing
    print("The daemon has started")

    scrapers = {}

    pid_file.write(str(os.getpid()))
    pid_file.close()

    should_run = True

    while should_run:
        sleep(1)
        cli_output = pipe.readline()
        if cli_output != "":
            prefix = cli_output.split()[0]
            print("Received: " + cli_output)
            if prefix == "quit":
                should_run = False
            elif prefix == "add":
                scraper_kwargs = literal_eval(cli_output[3:])
                scraper_name = scraper_kwargs.pop("name")
                should_quit = multiprocessing.Event()
                scraper_kwargs["should_quit"] = should_quit

                scraper_process = multiprocessing.Process(target=create_scraper, kwargs=scraper_kwargs)
                scraper_process.start()
                print(scraper_process.pid)
                scrapers[scraper_name] = {"process": scraper_process, "should_quit": should_quit}
            elif prefix == "list":
                pipe.write(str(scrapers))


    print("Quitting manager...")


def create_manager():
    global log_file, pid_file, pipe
    log_file = open("log", "w+")
    log_file.truncate()
    pid_file = open(".pid", "w+")
    pipe = os.fdopen(os.open(".craigslist_monitor_pipe", os.O_NONBLOCK | os.O_RDONLY))

    with DaemonContext(files_preserve=[pipe.fileno(), log_file.fileno(), pid_file.fileno()], stdout=log_file, stderr=log_file, working_directory=os.getcwd()):
        main()
    
def clean_up():
    os.remove(".pid")
    os.remove(".craigslist_monitor_pipe")
    pipe.close()
    log_file.close()
    print("Successfully exited manager.\n\n\n\n")

atexit.register(clean_up)

if __name__ == "__main__":
    create_manager()

