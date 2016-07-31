from utils import add_cmd
import utils

name = "factoids"
cmds = ["factoid add", "factoid remove", "factoid list"]

@add_cmd
def factoid(irc, event, args):
    """<add|remove|list> [<channel>] <factoid> [<text>]

    Adds or removes a factoid for <channel> or globally.
    <channel> is only necessary if the command isn't sent in
    the channel itself, <text> is only necessary if adding a
    factoid. Global factoids are modified by sending the command
    in private with no <channel> specified.
    """
    try:
        if args[0] == "add":
            if irc.is_channel(args[1]):
                channel = args[1]
                factoid = args[2]
                text = " ".join(args[3:])
            elif irc.is_channel(event.target):
                channel = event.target
                factoid = args[1]
                text = " ".join(args[2:])
            else:
                channel = None
                factoid = args[1]
                text = " ".join(args[2:])

            if channel:
                if utils.is_allowed(irc, event.source, channel):
                    if "factoids" not in irc.channels[channel]:
                        irc.channels[channel]["factoids"] = {}
                    irc.channels[channel]["factoids"][factoid] = text
                    irc.reply(event, "Factoid {} added for '{}' in {}".format(factoid, text, channel))
            else:
                if utils.is_allowed(irc, event.source):
                    irc.factoids[factoid] = text
                    irc.reply(event, "Global factoid {} added for '{}'".format(factoid, text))
                    
        elif args[0] == "remove":
            if irc.is_channel(args[1]):
                channel = args[1]
                factoid = args[2]
            elif irc.is_channel(event.target):
                channel = event.target
                factoid = args[1]
            else:
                channel = None
                factoid = args[1]

            if channel:
                if utils.is_allowed(irc, event.source, channel):
                    if "factoids" not in irc.channels[channel]:
                        irc.reply(event, "ERROR: No factoids exist for {}".format(channel))
                    elif factoid in irc.channels[channel]["factoids"]:
                        del(irc.channels[channel]["factoids"][factoid])
                        irc.reply(event, "Factoid {} deleted in {}".format(factoid, channel))
            else:
                if utils.is_allowed(irc, event.source):
                    if factoid in irc.factoids:
                        del(irc.factoids[factoid])
                        irc.reply(event, "Global factoid {} deleted".format(factoid))
                    else:
                        irc.reply(event, "ERROR: No global factoids named {} were found".format(factoid))
        elif args[0] == "list":
            if len(args) > 1:
                if irc.is_channel(args[1]):
                    channel = args[1]
                elif irc.is_channel(event.target):
                    channel = event.target
            elif irc.is_channel(event.target):
                channel = event.target
            else:
                channel = None
            if channel:
                if "factoids" in irc.channels[channel]:
                    irc.reply(event, "Factoids for {} are: {}".format(channel, ", ".join(["\"{}\"".format(x) for x in irc.channels[channel]["factoids"]])))
                else:
                    irc.reply(event, "No factoids were found for {}".format(channel))
            else:
                irc.reply(event, "Global factoids are: {}".format(", ".join(["\"{}\"".format(x) for x in irc.factoids])))
    except (KeyError, IndexError):
        irc.reply(event, utils.gethelp("factoid"))
