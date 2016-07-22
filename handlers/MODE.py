import utils

def on_mode(irc, conn, event):
    if irc.is_channel(event.target):
        channel = event.target
        modes = utils.split_modes(event.arguments)
        for mode in modes:
            if mode.startswith("+b"):
                mask = mode.split()[1]
                irc.state["channels"][channel]["bans"].append(mask)
            elif mode.startswith("-b"):
                mask = mode.split()[1]
                if mask in irc.state["channels"][channel]["bans"]:
                    irc.state["channels"][channel]["bans"].remove(mask)
            elif mode.startswith("+q"):
                mask = mode.split()[1]
                irc.state["channels"][channel]["quiets"].append(mask)

            elif mode.startswith("-q"):
                mask = mode.split()[1]
                if mask in irc.state["channels"][channel]["quiets"]:
                    irc.state["channels"][channel]["quiets"].remove(mask)

            elif mode.startswith("+e"):
                mask = mode.split()[1]
                irc.state["channels"][channel]["excepts"].append(mask)

            elif mode.startswith("-e"):
                mask = mode.split()[1]
                if mask in irc.state["channels"][channel]["excepts"]:
                    irc.state["channels"][channel]["excepts"].remove(mask)

            elif mode.startswith("+I"):
                mask = mode.split()[1]
                irc.state["channels"][channel]["invites"].append(mask)

            elif mode.startswith("-I"):
                mask = mode.split()[1]
                if mask in irc.state["channels"][channel]["invites"]:
                    irc.state["channels"][channel]["invites"].remove(mask)
                    
            elif mode.startswith("+k"):
                key = mode.split()[1]
                irc.channels[channel]["key"] = key
                
            elif mode.startswith("-k"):
                irc.channels[channel][key] = ""

            elif mode.startswith("+o"):
                nick = mode.split()[1]
                if nick == irc.get_nick():
                    log.info("Recieved op in {} from {}".format(channel, event.source))
                    log.info("Syncing {} exempts".format(channel))
                    irc.mode(channel, "e")
                    log.info("Syncing {} invites".format(channel))
                    irc.mode(channel, "I")
                if nick not in irc.state["channels"][channel]["ops"]:
                    irc.state["channels"][channel]["ops"].append(nick)

            elif mode.startswith("-o"):
                nick = mode.split()[1]
                if nick in irc.state["channels"][channel]["ops"]:
                    irc.state["channels"][channel]["ops"].remove(nick)

            elif mode.startswith("+v"):
                nick = mode.split()[1]
                if nick not in irc.state["channels"][channel]["voices"]:
                    irc.state["channels"][channel]["voices"].append(nick)

            elif mode.startswith("-v"):
                nick = mode.split()[1]
                if nick in irc.state["channels"][channel]["voices"]:
                    irc.state["channels"][channel]["voices"].remove(nick)
