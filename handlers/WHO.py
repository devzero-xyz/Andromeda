import utils

def on_whoreply(irc, conn, event):
    nick = event.arguments[4]
    user = event.arguments[1]
    host = event.arguments[2]
    gecos = event.arguments[6].lstrip("0 ")
    channel = event.arguments[0]
    status = event.arguments[5]
    if not nick in irc.state["users"]:
        irc.state["users"][nick] = {}
        irc.state["users"][nick]["channels"] = []
    irc.state["users"][nick]["user"] = user
    irc.state["users"][nick]["host"] = host
    irc.state["users"][nick]["gecos"] = gecos
    irc.state["users"][nick]["account"] = None
    if channel != "*":
        if not channel in irc.state["users"][nick]["channels"]:
            irc.state["users"][nick]["channels"].append(channel)
        if "@" in status:
            if nick not in irc.state["channels"][channel]["ops"]:
                irc.state["channels"][channel]["ops"].append(nick)
        if "+" in status:
            if nick not in irc.state["channels"][channel]["voices"]:
                irc.state["channels"][channel]["voices"].append(nick)

def on_whospcrpl(irc, conn, event):
    magic = event.arguments[0]
    if magic != "162":
        return
    channel = event.arguments[1]
    user = event.arguments[2]
    host = event.arguments[3]
    nick = event.arguments[4]
    status = event.arguments[5]
    account = event.arguments[6]
    gecos = event.arguments[7]
    if not nick in irc.state["users"]:
        irc.state["users"][nick] = {}
        irc.state["users"][nick]["channels"] = []
        irc.state["users"][nick]["lastmsg"] = {}
    irc.state["users"][nick]["user"] = user
    irc.state["users"][nick]["host"] = host
    irc.state["users"][nick]["gecos"] = gecos
    if account != "0":
        irc.state["users"][nick]["account"] = account
    else:
        irc.state["users"][nick]["account"] = None
    if channel != "*":
        if channel not in irc.state["users"][nick]["channels"]:
            irc.state["users"][nick]["channels"].append(channel)
        if "@" in status:
            if nick not in irc.state["channels"][channel]["ops"]:
                irc.state["channels"][channel]["ops"].append(nick)
        if "+" in status:
            if nick not in irc.state["channels"][channel]["voices"]:
                irc.state["channels"][channel]["voices"].append(nick)

def on_endofwho(irc, conn, event):
    utils.gotwho.set()