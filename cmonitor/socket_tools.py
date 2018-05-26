# A small socket handling module to make communication between the cli and
# the manager easier.
#
# The first 6 characters of a message sent by this module contain the length of
# the actual message. The receive function reads these first six digits and
# and uses them to obtain the actual message in one receive.
#
import socket


# Uses a newly created socket or one that is passed in to send a message
# between the cli and the manager.
def send(msg, sock=None):
    if not sock:
        import os
        import pathlib

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # my_loc = os.path.dirname(os.path.abspath(__file__))
        my_loc = os.path.join(str(pathlib.Path.home()), ".craigslist_monitor")
        os.chdir(my_loc)
        sock.connect(".craigslist_monitor_socket")

    # The length of the message in bytes is determined and made 6 characters
    # long (padded with zeroes).
    msg_length = str(len(msg.encode("utf-8"))).zfill(6)

    # The socket sends the message length along with the actual encoded
    # message.
    sock.send((str(msg_length) + msg).encode("utf-8"))

    return sock


# Uses the passed in socket to receive, decode, and return a message.
def receive(sock):
    from time import sleep

    # The socket keeps receiving until until it receives a message length.
    msg_length = sock.recv(6)
    while not msg_length:
        sleep(1)
        msg_length = sock.recv(6)

    # The socket uses the message length to receive the entire message at once.
    msg_length = int(msg_length)
    msg = sock.recv(msg_length).decode("utf-8")
    return msg
