def on_banlist(irc, conn, event):
    channel = event.arguments[0]
    mask = event.arguments[1]
    if not mask in irc.state["channels"][channel]["bans"]:
        irc.state["channels"][channel]["bans"].append(mask)

def on_728(irc, conn, event):
    channel = event.arguments[0]
    mask = event.arguments[2]
    if not mask in irc.state["channels"][channel]["quiets"]:
        irc.state["channels"][channel]["quiets"].append(mask)

def on_exceptlist(irc, conn, event):
    channel = event.arguments[0]
    mask = event.arguments[1]
    if not mask in irc.state["channels"][channel]["excepts"]:
        irc.state["channels"][channel]["excepts"].append(mask)

def on_invitelist(irc, conn, event):
    channel = event.arguments[0]
    mask = event.arguments[1]
    if not mask in irc.state["channels"][channel]["invites"]:
        irc.state["channels"][channel]["invites"].append(mask)