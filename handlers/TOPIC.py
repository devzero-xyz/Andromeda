def on_currenttopic(irc, conn, event):
    channel = event.arguments[0]
    topic = event.arguments[1]
    irc.state["channels"][channel]["topic"] = topic

def on_topic(irc, conn, event):
    channel = event.target
    topic = event.arguments[0]
    irc.state["channels"][channel]["topic"] = topic