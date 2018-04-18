import os
from daemon import DaemonContext
from sys import exit
import atexit

log_file, pid_file, manager_socket = (None for _ in range(3))
def main():
    import socket
    import socket_tools
    import multiprocessing
    from time import sleep
    from ast import literal_eval
    from scraper import create_scraper
    print("The daemon has started")

    scrapers = {}

    pid_file.write(str(os.getpid()))
    pid_file.close()

    should_run = True

    while should_run:

        cli_connection, addr = manager_socket.accept()
        cli_output = socket_tools.receive(cli_connection)
        prefix = cli_output.split()[0]

        print("Received: " + cli_output)
        if prefix == "quit":
            should_run = False
            for scraper in scrapers:
                scrapers[scraper]["should_quit"].set()
            socket_tools.send(sock=cli_connection, msg="Quitting manager...")
        elif prefix == "add":
            scraper_kwargs = literal_eval(cli_output[4:])
            scraper_name = scraper_kwargs.pop("name")

            if scraper_name in scrapers:
                socket_tools.send(sock=cli_connection, msg="You can't use the same name for multiple scrapers.")
            else:
                should_quit = multiprocessing.Event()
                scraper_kwargs["should_quit"] = should_quit

                scraper_process = multiprocessing.Process(target=create_scraper, kwargs=scraper_kwargs)
                scraper_process.start()
                scrapers[scraper_name] = {"process": scraper_process, "should_quit": should_quit}
                print(scraper_process.pid)
                socket_tools.send(sock=cli_connection, msg="Successfully added scraper.")
        elif prefix == "list":
            socket_tools.send(sock=cli_connection, msg=str([kw for kw in scrapers]))
        elif prefix == "stop":
            scraper_name = cli_output[5:]
            if scraper_name in scrapers:
                scrapers[scraper_name]["should_quit"].set()
                socket_tools.send(sock=cli_connection, msg="Successfully stopped scraper named " + scraper_name)
                del scrapers[scraper_name]
            else:
                socket_tools.send(sock=cli_connection, msg="There is no scraper named " + scraper_name)


        cli_connection.close()


def create_manager():
    import socket
    global log_file, pid_file, manager_socket

    manager_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    manager_socket.bind(".craigslist_monitor_socket")
    manager_socket.listen(1)

    log_file = open("log", "w+")
    log_file.truncate()
    pid_file = open(".pid", "w+")

    with DaemonContext(files_preserve=[manager_socket.fileno(), log_file.fileno(), pid_file.fileno()], stdout=log_file, stderr=log_file, working_directory=os.getcwd()):
        main()
    
def clean_up():
    os.remove(".pid")
    os.remove(".craigslist_monitor_socket")
    log_file.close()
    manager_socket.close()
    print("Successfully exited manager.\n\n\n\n")

atexit.register(clean_up)

# if __name__ == "__main__":
    # create_manager()

