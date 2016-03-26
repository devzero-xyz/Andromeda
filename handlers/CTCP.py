import time

def on_ctcp(irc, conn, event):
    nick = event.source.nick
    ctcptype = event.arguments[0]
    if len(event.arguments) > 1:
        args = event.arguments[1]
    else:
        args = None
    if ctcptype != "ACTION":
        log.info("Received CTCP {} from {}".format(ctcptype, event.source))

    if ctcptype == "VERSION":
        irc.ctcp_reply(nick, "VERSION {}".format(irc.version))

    elif ctcptype == "PING":
        now = int(time.time())
        if len(args.split()) > 1:
            irc.ctcp_reply(nick, "PING {} {}".format(now, args.split()[1]))
        else:
            irc.ctcp_reply(nick, "PING {}".format(now))
