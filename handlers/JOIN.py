import time

def on_join(irc, conn, event):
    nick = event.source.nick
    channel = event.target
    if nick == irc.get_nick():
        log.info("Joined to {}".format(channel))
        irc.state["channels"][channel] = {}
        irc.state["channels"][channel]["topic"] = "" # TOPIC chan
        irc.state["channels"][channel]["names"] = [] # NAMES chan
        irc.state["channels"][channel]["bans"] = [] # MODE chan b
        irc.state["channels"][channel]["quiets"] = [] # MODE chan q
        irc.state["channels"][channel]["excepts"] = [] # MODE chan e
        irc.state["channels"][channel]["invites"] = [] # MODE chan i
        irc.state["channels"][channel]["ops"] = []
        irc.state["channels"][channel]["voices"] = []
        irc.state["channels"][channel]["antispam"] = {}
        if channel not in irc.channels:
            irc.channels[channel] = {}
            irc.save_config()
        log.info("Syncing {} users".format(channel))
        irc.who(channel)
        log.info("Syncing {} bans".format(channel))
        irc.mode(channel, "b")
        log.info("Syncing {} quiets".format(channel))
        irc.mode(channel, "q")
    if nick not in irc.state["channels"][channel]["names"]:
        irc.state["channels"][channel]["names"].append(nick)
    if nick not in irc.state["users"]:
        irc.state["users"][nick] = {}
        irc.state["users"][nick]["channels"] = []
        irc.state["users"][nick]["lastmsg"] = {}
    irc.state["users"][nick]["lastmsg"]["time"] = time.time()
    irc.state["users"][nick]["lastmsg"]["channel"] = channel
    irc.state["users"][nick]["lastmsg"]["message"] = None
    irc.state["users"][nick]["lastmsg"]["command"] = event.type
    irc.state["users"][nick]["user"] = event.source.user
    irc.state["users"][nick]["host"] = event.source.host
    irc.state["users"][nick]["gecos"] = event.arguments[1]
    if event.arguments[0] != "*":
        irc.state["users"][nick]["account"] = event.arguments[0]
    else:
        irc.state["users"][nick]["account"] = None
    if channel not in irc.state["users"][nick]["channels"]:
        irc.state["users"][nick]["channels"].append(channel)