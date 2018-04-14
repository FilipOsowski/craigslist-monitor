import os
from daemon import DaemonContext
from time import sleep
from sys import exit
import atexit

log_file, pid_file, pipe = (None for _ in range(3))
def main():
    print("The daemon has started")

    pid_file.write(str(os.getpid()))
    pid_file.close()

    should_run = True

    while should_run:
        sleep(1)
        input = pipe.readline()
        if input != "":
            print("Received: " + input)
            if input == "quit":
                should_run = False
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
    print("Successfully exited manager.")

atexit.register(clean_up)

if __name__ == "__main__":
    create_manager()

