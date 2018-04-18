import socket


def send(msg, sock=None):
    if not sock:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(".craigslist_monitor_socket")

    msg_length = str(len(msg.encode("utf-8"))).zfill(6)
    sock.send((str(msg_length) + msg).encode("utf-8"))

    return sock


def receive(sock):
    from time import sleep

    msg_length = sock.recv(6)
    while not msg_length:
        sleep(1)
        msg_length = sock.recv(6)

    msg_length = int(msg_length)
    msg = sock.recv(msg_length).decode("utf-8")
    return msg
