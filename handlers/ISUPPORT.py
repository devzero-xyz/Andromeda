def on_featurelist(irc, conn, event):
    for param in event.arguments[:-1]:
        if "=" in param:
            name, value = param.split("=")
        else:
            name = param
            value = ""
        if value != "":
            if "," in value:
                for param1 in value.split(","):
                    if ":" in value:
                        if ":" in param1:
                            name1, value1 = param1.split(":")
                        else:
                            name1 = param1
                            value1 = ""
                        if name not in irc.state["server"]["isupport"]:
                            irc.state["server"]["isupport"][name] = {}
                        irc.state["server"]["isupport"][name][name1] = value1
                    else:
                        if name not in irc.state["server"]["isupport"]:
                            irc.state["server"]["isupport"][name] = []
                        irc.state["server"]["isupport"][name].append(param1)
            else:
                if ":" in value:
                    name1, value1 = value.split(":")
                    irc.state["server"]["isupport"][name] = {}
                    irc.state["server"]["isupport"][name][name1] = value1
                elif name == "PREFIX":
                    count = 0
                    value = value.split(")")
                    value[0] = value[0].lstrip("(")
                    irc.state["server"]["isupport"][name] = {}
                    for mode in value[0]:
                        name1 = mode
                        value1 = value[1][count]
                        count += 1
                        irc.state["server"]["isupport"][name][name1] = value1
                else:
                    irc.state["server"]["isupport"][name] = value
        else:
            irc.state["server"]["isupport"][name] = value
