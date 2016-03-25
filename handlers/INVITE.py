from utils import *

def on_invite(irc, conn, event):
    source = event.source
    channel = event.arguments[0]
    log.info("Invited to {} by {}".format(channel, event.source))
    if is_allowed(irc, source, channel):
        irc.join(channel)
