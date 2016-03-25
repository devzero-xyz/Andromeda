def on_nick(irc, conn, event):
    nick = event.source.nick
    newnick = event.target

    for channel in irc.state["channels"]:
        if nick in irc.state["channels"][channel]["names"]:
            irc.state["channels"][channel]["names"].remove(nick)
            irc.state["channels"][channel]["names"].append(newnick)
        if nick in irc.state["channels"][channel]["ops"]:
            irc.state["channels"][channel]["ops"].remove(nick)
            irc.state["channels"][channel]["ops"].append(newnick)
        if nick in irc.state["channels"][channel]["voices"]:
            irc.state["channels"][channel]["voices"].remove(nick)
            irc.state["channels"][channel]["voices"].append(newnick)

    if nick in irc.state["users"]:
        irc.state["users"][newnick] = irc.state["users"][nick]
        del(irc.state["users"][nick])