def on_account(irc, conn, event):
    nick = event.source.nick
    account = event.target
    if account != "*":
        irc.state["users"][nick]["account"] = account
    else:
        irc.state["users"][nick]["account"] = None