import os
from daemon import DaemonContext
import atexit

# log_file: The file that the stdout and stderr of the manager is written to.
# pid_file: Stores the pid of the manager daemon (used for checking the
# manager's existence)
# manager_socket: The unix domain socket used for communication between the cli
# and the manager.
log_file, pid_file, manager_socket = (None for _ in range(3))


def main():
    import socket_tools
    import multiprocessing
    from ast import literal_eval
    from scraper import create_scraper
    print("The manager has started.")

    # The scrapers dictionary keeps track of attributes of active scrapers.
    # name: The name of the scraper.
    # process: The scraper's process as returned by multiprocessing.Process 
    # should_quit: A multiprocessing.Event instance that is used for telling
    # the scraper when to quit.
    scrapers = {}

    # The scraper's pid is written and the .pid file is closed.
    # The existence of the .pid file tells the cli that the manager exists.
    pid_file.write(str(os.getpid()))
    pid_file.close()

    should_run = True

    while should_run:

        # The manager waits for a connection from the cli. Upon making a
        # connection, the manager receives the cli's message.
        cli_connection, addr = manager_socket.accept()
        cli_output = socket_tools.receive(cli_connection)
        prefix = cli_output.split()[0]

        print("Received: " + cli_output)

        # The manager performs an action depending on the prefix to the cli's
        # message. The manager also sends a message to the (waiting)
        # cli_connection socket confirming the action it took.

        # If the manager is ordered to quit, it ends its main loop and sets all
        # active scrapers' events (signaling them to quit).
        if prefix == "quit":
            should_run = False
            for scraper in scrapers:
                scrapers[scraper]["should_quit"].set()
            socket_tools.send(sock=cli_connection, msg="Quitting the manager...")

        # If the manager is ordered to add a scraper, it checks if the
        # requirement for adding a scraper is met, and then creates the scraper
        # and its associated properties.
        elif prefix == "add":

            # The cli's message containing the scraper's specifications is
            # parsed into a dictionary for later use.
            scraper_kwargs = literal_eval(cli_output[4:])
            scraper_name = scraper_kwargs.pop("name")

            # Checks to see if a scraper_name already exists in the scrapers dictionary.
            if scraper_name in scrapers:
                socket_tools.send(sock=cli_connection, msg="You can't use the same name for multiple scrapers.")
            else:
                
                # Setting the event (later passed to and monitored by the
                # scraper) tells the scraper when to quit.
                should_quit = multiprocessing.Event()
                scraper_kwargs["should_quit"] = should_quit

                # The scraper process is started using the multiprocessing
                # so as to not block the manager. The kwargs to the manager are
                # from the cli's message.
                scraper_process = multiprocessing.Process(target=create_scraper, kwargs=scraper_kwargs)
                scraper_process.start()
                scrapers[scraper_name] = {"process": scraper_process, "should_quit": should_quit}
                print("Started new scraper, name =", scraper_name, ", pid =", scraper_process.pid)
                socket_tools.send(sock=cli_connection, msg="Successfully added scraper.")

        # If ordered to list, the scraper sends a message to the cli a list
        # containing the names of currently active scrapers.
        elif prefix == "list":
            socket_tools.send(sock=cli_connection, msg=str([kw for kw in scrapers]))

        # If ordered to stop a scraper, the manager first checks for the
        # scraper's existence and then signals it to quit.
        elif prefix == "stop":
            scraper_name = cli_output[5:]
            if scraper_name in scrapers:
                print("Stopping scraper, name =", scraper_name, ", pid =", scrapers[scraper_name]["process"].pid)

                # The scraper's should_quit event is set, causing the scraper's
                # main loop to exit.
                scrapers[scraper_name]["should_quit"].set()
                socket_tools.send(sock=cli_connection, msg="Successfully stopped scraper named " + scraper_name)
                del scrapers[scraper_name]
            else:
                socket_tools.send(sock=cli_connection, msg="There is no scraper named " + scraper_name)

        cli_connection.close()


def create_manager():
    import socket
    global log_file, pid_file, manager_socket

    # Creates the unix domain socket for communication with between the
    # manager and the cli.
    manager_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    manager_socket.bind(".craigslist_monitor_socket")
    manager_socket.listen(1)

    log_file = open("log", "w+")
    log_file.truncate()
    pid_file = open(".pid", "w+")

    # Sets up the context for the manager daemon to run in. 
    daemon_context = DaemonContext()

    # To keep the log_file, manager_socket, and pid_file accessible after
    # opening the daemon, they are specified to be preserved.
    daemon_context.files_preserve = [manager_socket.fileno(), log_file.fileno(), pid_file.fileno()] 

    # The manager daemon's stderr and stdout is set to be sent to the log_file.
    daemon_context.stderr = log_file
    daemon_context.stdout = log_file

    # For easy access to surrounding files, the manager daemon's working
    # directory is set to the location of this script.
    daemon_context.working_directory = os.getcwd()

    # The daemon_context is opened and the manager's main is run in a (now)
    # daemon process.
    with daemon_context:
        main()
    
# Closes and removes resources that are unnecessary when the manager 
# is not running.
def clean_up():
    os.remove(".pid")
    os.remove(".craigslist_monitor_socket")
    log_file.close()
    manager_socket.close()
    print("Successfully exited manager.\n")

atexit.register(clean_up)