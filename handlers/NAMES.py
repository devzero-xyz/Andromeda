def on_namreply(irc, conn, event):
    channel = event.arguments[1]
    names = event.arguments[2]
    for nick in names.split():
        nick = nick.lstrip("@+")
        if not nick in irc.state["channels"][channel]["names"]:
            irc.state["channels"][channel]["names"].append(nick)