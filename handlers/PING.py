import time

def on_pong(irc, conn, event):
    irc.lastping = time.time()
