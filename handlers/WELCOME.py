def on_welcome(irc, conn, event):
    irc.connected = True
    irc.fifo_thread.start()
    irc.config_timer.start()
    irc.ping_timer.start()
    if irc.umodes:
        irc.mode(irc.get_nick(), irc.umodes)
    if irc.sasl or irc.identified:
        for channel in irc.channels:
            if irc.channels[channel].get("autojoin", irc.autojoin):
                if irc.channels[channel].get("key"):
                    irc.join(channel, irc.channels[channel]["key"])
                else:
                    irc.join(channel)

    elif irc.nickserv and not irc.identified:
        log.info("Attempting to identify to services as {}".format(irc.username))
        irc.privmsg("NickServ", "IDENTIFY {} {}".format(irc.username, irc.password))

    if irc.nick != irc.get_nick():
        log.info("Attempting to regain primary nickname with services")
        irc.privmsg("NickServ", "REGAIN {} {}".format(irc.nick, irc.password))
