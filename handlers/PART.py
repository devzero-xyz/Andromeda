import copy
import time

def on_part(irc, conn, event):
    nick = event.source.nick
    channel = event.target
    if len(event.arguments) > 0:
        reason = event.arguments[0]
    else:
        reason = ""

    if event.source.nick == irc.get_nick():
        for user in copy.deepcopy(irc.state["users"]):
            if channel in irc.state["users"][user]["channels"]:
                irc.state["users"][user]["channels"].remove(channel)
        if reason:
            if reason.startswith("requested by"):
                log.info("Removed from {}".format(channel))
                if irc.channels[channel].get("autorejoin", irc.autorejoin):
                    log.info("Attempting to re-join {}".format(channel))
                    irc.join(channel)

    if channel in irc.state["channels"]:
        if nick in irc.state["channels"][channel]["names"]:
            irc.state["channels"][channel]["names"].remove(nick)
        if nick in irc.state["channels"][channel]["ops"]:
            irc.state["channels"][channel]["ops"].remove(nick)
        if nick in irc.state["channels"][channel]["voices"]:
            irc.state["channels"][channel]["voices"].remove(nick)

    if nick in irc.state["users"]:
        irc.state["users"][nick]["lastmsg"]["time"] = time.time()
        irc.state["users"][nick]["lastmsg"]["channel"] = channel
        irc.state["users"][nick]["lastmsg"]["message"] = reason
        irc.state["users"][nick]["lastmsg"]["command"] = event.type
        if channel in irc.state["users"][nick]["channels"]:
            irc.state["users"][nick]["channels"].remove(channel)