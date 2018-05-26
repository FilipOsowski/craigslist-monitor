import argparse
import os
import pathlib


# A decorator that checks for the manager's existence and depending on the
# result decides whether to run a function.
def check_manager(should_exist):

    # Checks for the manager's existence by checking for the existence of .pid
    # file (created by the manager).
    def decorator(function):
        result = None
        my_loc = os.path.join(str(pathlib.Path.home()), ".craigslist_monitor")
        try:
            with open(os.path.join(my_loc, ".pid")):
                result = True
        except FileNotFoundError:
            result = False

        def wrapper(*args):

            # If the manager's existence meets expectations, the wrapped
            # function is run.
            if should_exist == result:
                function(*args)
            else:
                if result:
                    print("The manager already exists")
                else:
                    print("The manager does not exist.")

        return wrapper

    return decorator


# Sends a message to the manager specifying the scraper to created. The message
# includes the specifications for the scraper.
@check_manager(should_exist=True)
def add(kwargs):
    kwargs["output"] = os.path.join(os.getcwd(), kwargs["output"])
    send_to_manager("add " + str(kwargs))


# Handles all manager related commands
def manager(kwargs):

    # Handles all manager related commands not having to do with the manager's
    # creation.
    @check_manager(should_exist=True)
    def manager_options(option):

        # Tells the manager (and active scrapers) to quit.
        if option == "quit":
            send_to_manager("quit")

        # Tells the manager to list active scrapers.
        elif option == "list":
            scrapers = send_to_manager("list", print_resp=False)
            print("Existing scrapers- ", scrapers)

        # Tells the manager to stop a scraper. The message sent includes the
        # name of the scraper to be stopped.
        elif option == "stop":
            send_to_manager(msg="stop " + kwargs["stop"][0])

    # Starts a manager if it doesn't exist by importing the manager module and
    # calling its start function.
    @check_manager(should_exist=False)
    def start_manager():

        from cmonitor import manager
        print("Creating the manager...")
        manager.create_manager()

    # If a manager command is specified, it is submitted to the manager_options
    # function. Else, a manager is initialized.
    for kw in kwargs:
        if kwargs[kw]:
            manager_options(kw)
            break
    else:
        start_manager()


# Utilizes the socket_tools module to exchange information with the manager.
# Also closes and keeps track of the client socket.
def send_to_manager(msg, print_resp=True):
    from cmonitor import socket_tools
    client_socket = socket_tools.send(msg)
    response = socket_tools.receive(client_socket)
    client_socket.close()

    if print_resp:
        print(response)
    return response


def cli():
    monitor = argparse.ArgumentParser(
        description="Monitors a craigslist search for new items.")
    monitor_subparsers = monitor.add_subparsers(
        help="Use <sub-command> followed by -h for further help.")

    # The add interface handles the addition and customization of scrapers.
    add_item = monitor_subparsers.add_parser(
        "add", description="Add an item (craigslist search) to be monitored.")
    add_item.add_argument("name", help="The name of the process.")
    add_item.add_argument(
        "monitor",
        help="The url of a craigslist search or the item name to be monitored."
    )
    add_item.add_argument(
        "output",
        help="The file to which items found by the monitor will be written to")
    add_item.add_argument(
        "-r",
        "--renewals",
        action="store_true",
        help="Include old posts that are renewed.")
    add_item.add_argument(
        "-e",
        "--exclude-words",
        nargs="+",
        metavar="word",
        default=[],
        help="Exclude posts that contain these words (not case sensitive).")
    add_item.add_argument(
        "-t",
        "--time-refresh",
        nargs=2,
        metavar="pos_int",
        type=int,
        default=[60, 180],
        help=
        "The two positive integers used with randrange(lower, upper) to determine how long (in seconds) until the scraper checks for new items (first integer must be lower than the second). The default is 60 and 180."
    )
    add_item.set_defaults(func=add)

    # The manager interface handles all commands for managing existing
    # scrapers (and the manager itself).
    manager_interface = monitor_subparsers.add_parser(
        "manager",
        description="Starts the manager if issued with no commands.")
    manager_options = manager_interface.add_mutually_exclusive_group()
    manager_options.add_argument(
        "-q",
        "--quit",
        help="Quits the manager and all scrapers",
        action="store_true")
    manager_options.add_argument(
        "-l",
        "--list",
        help="List all the currently running scrapers",
        action="store_true")
    manager_options.add_argument(
        "-s",
        "--stop",
        nargs=1,
        metavar="scraper_name",
        help="Stop the named scraper")
    manager_options.set_defaults(func=manager)
    kwargs = vars(monitor.parse_args())

    if kwargs:
        # Checks to see if the arguments of time_refresh comply to
        # random.randrange expectations. (lower and upper should both be
        # positive and lower > upper)
        if "time_refresh" in kwargs:
            lower, upper = kwargs["time_refresh"]
            if not (lower < upper and lower >= 0 and upper >= 0):

                # An error is thrown if these expectations are not met.
                raise argparse.ArgumentTypeError(
                    "Invalid time_refresh: The first integer must be greater than the second integer and both integers must be positive."
                )

        # Removing the "func" argument allows the kwargs to submitted directly
        # to the scraper.
        if kwargs:
            target_func = kwargs.pop("func")
            target_func(kwargs)
    else:

        # If the cli is used without any arguments, help is printed.
        monitor.print_help()
