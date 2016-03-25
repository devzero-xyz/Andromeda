import time
import utils

def on_privnotice(irc, conn, event):
    if event.source.nick == "NickServ" and not irc.identified:
        if irc.nickserv and not irc.sasl:
            if "You are now identified" in event.arguments[0]:
                irc.identified = True
                for channel in irc.channels:
                    if irc.channels[channel].get("autojoin", irc.autojoin):
                        if irc.channels[channel].get("key"):
                            irc.join(channel, irc.channels[channel]["key"])
                        else:
                            irc.join(channel)
    elif utils.is_command(irc, conn, event):
        utils.handle_command(irc, conn, event)

def on_privmsg(irc, conn, event):
    if utils.is_command(irc, conn, event):
        utils.handle_command(irc, conn, event)

def on_pubnotice(irc, conn, event):
    nick = event.source.nick
    channel = event.target
    msg = event.arguments[0]
    irc.state["users"][nick]["lastmsg"]["time"] = time.time()
    irc.state["users"][nick]["lastmsg"]["channel"] = channel
    irc.state["users"][nick]["lastmsg"]["message"] = msg
    irc.state["users"][nick]["lastmsg"]["command"] = event.type
    if utils.is_command(irc, conn, event):
        utils.handle_command(irc, conn, event)

def on_pubmsg(irc, conn, event):
    nick = event.source.nick
    channel = event.target
    msg = event.arguments[0]
    irc.state["users"][nick]["lastmsg"]["time"] = time.time()
    irc.state["users"][nick]["lastmsg"]["channel"] = channel
    irc.state["users"][nick]["lastmsg"]["message"] = msg
    irc.state["users"][nick]["lastmsg"]["command"] = event.type
    if utils.is_command(irc, conn, event):
        utils.handle_command(irc, conn, event)