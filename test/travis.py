from time import sleep
import signal
import os

from utils import add_handler

def on_join(irc, conn, event):
    # if something is going to go wrong
    # it'll probably happen within 10 secs
    sleep(10)
    # If we're still alive, exit cleanly
    os.kill(os.getpid(), signal.SIGINT)
add_handler(on_join, "travis")