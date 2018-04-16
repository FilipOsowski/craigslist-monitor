import argparse


def check_manager(should_exist):
    def decorator(function):
        result = None
        try:
            with open(".pid"):
                result = True
        except FileNotFoundError:
            result = False

        def wrapper(*args):
            if should_exist == result:
                print("Expectations met result.")
                function(*args)
            else:
                print("Expectations did not meet results.")

        return wrapper
    return decorator


@check_manager(should_exist=True)
def add(args):
    with open(".craigslist_monitor_pipe", "w") as pipe:
        pipe.write("add " + str(args))


def manager(args):
    @check_manager(should_exist=True)
    def quit_m():
        print("Quitting manager...")
        import os.path
        with open(".craigslist_monitor_pipe", "w") as pipe:
            pipe.write("quit")

    @check_manager(should_exist=False)
    def start_m():
        from os import mkfifo
        from manager import create_manager

        mkfifo(".craigslist_monitor_pipe")

        print("Creating manager...")
        create_manager()
    
    if args["quit"]:
        quit_m()
    else:
        start_m()


monitor = argparse.ArgumentParser(description="Monitors a craigslist search for new items.")
monitor_subparsers = monitor.add_subparsers(help="Sub-commands")

add_item = monitor_subparsers.add_parser("add", description="Add an item (craigslist search) to be monitored.")
add_item.add_argument("name", help="The name of the process.")
add_item.add_argument("url", help="The url of a (customized) craigslist search to be monitored.")
add_item.add_argument("-r", "--renewals", action="store_true", help="Include old posts that are renewed.")
add_item.add_argument("-e", "--exclude-words", nargs="+", metavar="word", default=[], help="Exclude posts that contain these words (not case sensative).")
add_item.set_defaults(func=add)

create_manager = monitor_subparsers.add_parser("manager", description="Starts the manager if issued with no commands.")
create_manager.add_argument("-q", "--quit", help="Quits the manager.", action="store_true")
create_manager.set_defaults(func=manager)
args = vars(monitor.parse_args())
target_func = args.pop("func")
target_func(args)
