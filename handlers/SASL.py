from base64 import b64encode

def on_cap(irc, conn, event):
    if event.arguments[0] == "ACK":
        irc.state["server"]["caps"] = event.arguments[1].split()
        if "sasl" in irc.state["server"]["caps"]:
            irc.send("AUTHENTICATE PLAIN")
        else:
            irc.send("CAP END")

def on_authenticate(irc, conn, event):
    if event.target == "+":
        saslstr = b64encode("{0}\x00{0}\x00{1}".format(irc.username,
                            irc.password).encode()).decode()
        irc.send("AUTHENTICATE {}".format(saslstr))

def on_903(irc, conn, event):
    irc.identifed = True
    irc.send("CAP END")

def on_904(irc, conn, event):
    log.critical("SASL authentication failed.")
    sys.exit(1)

def on_905(irc, conn, event):
    log.critical("SASL authentication aborted.")
    sys.exit(1)
