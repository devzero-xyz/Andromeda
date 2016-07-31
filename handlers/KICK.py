import copy

def on_kick(irc, conn, event):
    channel = event.target
    target = event.arguments[0]
    if len(event.arguments) > 1:
        reason = event.arguments[1]
    else:
        reason = ""
    if target == irc.get_nick():
        log.info("Kicked from {} by {}".format(channel, event.source))
        for user in copy.deepcopy(irc.state["users"]):
            if channel in irc.state["users"][user]["channels"]:
                irc.state["users"][user]["channels"].remove(channel)
        if irc.channels[channel].get("autorejoin", irc.autorejoin):
            log.info("Attempting to rejoin {}".format(channel))
            irc.join(channel)

    if channel in irc.state["channels"]:
        if target in irc.state["channels"][channel]["names"]:
            irc.state["channels"][channel]["names"].remove(target)
        if target in irc.state["channels"][channel]["ops"]:
            irc.state["channels"][channel]["ops"].remove(target)
        if target in irc.state["channels"][channel]["voices"]:
            irc.state["channels"][channel]["voices"].remove(target)

    if target in irc.state["users"]:
        irc.state["users"][target]["lastmsg"]["time"] = time.time()
        irc.state["users"][target]["lastmsg"]["channel"] = channel
        irc.state["users"][target]["lastmsg"]["message"] = reason
        irc.state["users"][target]["lastmsg"]["command"] = event.type
        if channel in irc.state["users"][target]["channels"]:
            irc.state["users"][target]["channels"].remove(channel)