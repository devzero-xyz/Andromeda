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
                
                found = False
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+k"):
                            irc.channels[channel]["modes"][iteration] = "+k " + key
                            found = True
                if not found:
                    irc.channels[channel]["modes"].append("+k " + key)
                
            elif mode.startswith("-k"):
                irc.channels[channel]["key"] = ""
                
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+k"):
                            irc.channels[channel]["modes"].pop(iteration)
                
            elif mode.startswith("+j"):
                found = False
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+j"):
                            irc.channels[channel]["modes"][iteration] = "+j " + mode.split()[1]
                            found = True
                if not found:
                    irc.channels[channel]["modes"].append("+j " + mode.split()[1])
            
            elif mode.startswith("-j"):
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+j"):
                            irc.channels[channel]["modes"].pop(iteration)
                            
            elif mode.startswith("+f"):
                found = False
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+f"):
                            irc.channels[channel]["modes"][iteration] = "+f " + mode.split()[1]
                            found = True
                if not found:
                    irc.channels[channel]["modes"].append("+f " + mode.split()[1])
                    
            elif mode.startswith("-f"):
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+f"):
                            irc.channels[channel]["modes"].pop(iteration)

            elif mode.startswith("+l"):
                found = False
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+l"):
                            irc.channels[channel]["modes"][iteration] = "+l " + mode.split()[1]
                            found = True
                if not found:
                    irc.channels[channel]["modes"].append("+l " + mode.split()[1])

            elif mode.startswith("-l"):
                if "modes" in irc.channels[channel].keys():
                    for iteration, mode in enumeration(irc.channels[channel]["modes"]):
                        if mode.startswith("+l"):
                            irc.channels[channel]["modes"].pop(iteration)

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
                    
def on_channelmodeis(irc, conn, event):
    message = event.arguments
    message[0].replace("+", "")
    modes = utils.split_modes(message[1:])
    extra = message[2:]
    channel = message[0]

    irc.channels[channel]["modes"] = []
    
    for mode in modes:
        irc.channels[channel]["modes"].append(mode)

        if mode.startswith("+k"):
            irc.channels[channel]["key"] = mode.split()[1]
