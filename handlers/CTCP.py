from time import time

def on_ctcp(irc, conn, event):
    nick = event.source.nick
    type = event.arguments[0]
    if len(event.arguments) > 1:
        args = event.arguments[1]
    else:
        args = None
    if type != "ACTION":
        log.info("Received CTCP {} from {}".format(type, event.source))

    if type == "VERSION":
        irc.ctcp_reply(nick, "VERSION {}".format(irc.version))

    elif type == "PING":
        if len(args.split()) > 1:
            irc.ctcp_reply(nick, "PING {} {}".format(int(time()), args.split()[1]))
        else:
            irc.ctcp_reply(nick, "PING {}".format(int(time())))