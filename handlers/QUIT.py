import time

def on_quit(irc, conn, event):
    nick = event.source.nick
    if len(event.arguments) > 0:
        reason = event.arguments[0]
    else:
        reason = ""

    for channel in irc.state["channels"]:
        if nick in irc.state["channels"][channel]["names"]:
            irc.state["channels"][channel]["names"].remove(nick)
        if nick in irc.state["channels"][channel]["ops"]:
            irc.state["channels"][channel]["ops"].remove(nick)
        if nick in irc.state["channels"][channel]["voices"]:
            irc.state["channels"][channel]["voices"].remove(nick)

    if nick in irc.state["users"]:
        irc.state["users"][nick]["lastmsg"]["time"] = time.time()
        irc.state["users"][nick]["lastmsg"]["channel"] = None
        irc.state["users"][nick]["lastmsg"]["message"] = reason
        irc.state["users"][nick]["lastmsg"]["command"] = event.type