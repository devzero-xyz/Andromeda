def on_396(irc, conn, event):
    nick = irc.get_nick()
    newhost = event.arguments[0]
    if nick in irc.state["users"]:
        irc.state["users"][nick]["host"] = newhost