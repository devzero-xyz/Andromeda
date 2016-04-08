from utils import add_cmd
import utils

name = "alias"
cmds = ["alias add", "alias remove", "alias list"]

@add_cmd
def alias(irc, event, args):
    """<add|remove|list> [<channel>] <alias> [<command>]

    Adds or removes an alias for <channel> or globally.
    <channel> is only necessary if the command isn't sent in
    the channel itself, <command> is only necessary if adding
    an alias. Global aliases are modified by sending the command
    in private with no <channel> specified.
    """
    try:
        if args[0] == "add":
            if irc.is_channel(args[1]):
                channel = args[1]
                alias = args[2]
                command = " ".join(args[3:])
            elif irc.is_channel(event.target):
                channel = event.target
                alias = args[1]
                command = " ".join(args[2:])
            else:
                channel = None
                alias = args[1]
                command = " ".join(args[2:])

            if channel:
                if utils.is_allowed(irc, event.source, channel):
                    if len(command) >= 2 and command.split()[0] in utils.commands: #and alias.lower() not in utils.commands:
                        if "aliases" not in irc.channels[channel]:
                            irc.channels[channel]["aliases"] = {}
                        if alias != alias.lower():
                            irc.reply(event, "The alias name has to be lowercase. Changing alias name...")
                            alias = alias.lower()
                        irc.channels[channel]["aliases"][alias] = command
                        irc.reply(event, "Alias \"{}\" with arguments \"{}\" added for command \"{}\" in \"{}\"".format(alias, " ".join(command.split()[1:]), command.split()[0], channel))
                    elif command.split()[0] in utils.commands and alias not in utils.commands:
                        if "aliases" not in irc.channels[channel]:
                            irc.channels[channel]["aliases"] = {}
                        if alias != alias.lower():
                            irc.reply(event, "The alias name has to be lowercase. Changing alias name...")
                            alias = alias.lower()
                        irc.reply(event, "testing")
                        irc.channels[channel]["aliases"][alias] = command
                        irc.reply(event, "Alias \"{}\" added for command \"{}\" in \"{}\"".format(alias, command, channel))
                    elif alias in utils.commands:
                        irc.reply(event, "A command with the name \"{}\" already exists".format(alias))
                    elif not command.split()[0] in utils.commands:
                        irc.reply(event, "No command called \"{}\" exists".format(command.split()[0]))
            else:
                if utils.is_allowed(irc, event.source) and command in utils.commands and alias not in utils.commands:
                    irc.aliases[alias] = command
                    irc.reply(event, "Global alias \"{}\" added for command \"{}/\"".format(alias, command))
                elif alias in utils.commands:
                    irc.reply(event, "A command with the name \"{}\" already exists".format(command))
                elif not command in utils.commands:
                    irc.reply(event, "No command called \"{}\" exists".format(command))
        elif args[0] == "remove":
            if irc.is_channel(args[1]):
                channel = args[1]
                alias = args[2]
            elif irc.is_channel(event.target):
                channel = event.target
                alias = args[1]
            else:
                channel = None
                alias = args[1]

            if channel:
                if utils.is_allowed(irc, event.source, channel):
                    if "aliases" not in irc.channels[channel]:
                        irc.reply(event, "ERROR: No aliases exist for \"{}\"".format(channel))
                    elif alias not in irc.channels[channel]["aliases"]:
                        irc.reply(event, "Alias \"{}\" does not exist in \"{}\"".format(alias, channel))
                    elif alias in irc.channels[channel]["aliases"]:
                        del(irc.channels[channel]["aliases"][alias])
                        irc.reply(event, "Alias \"{}\" deleted in \"{}\"".format(alias, channel))
            else:
                if utils.is_allowed(irc, event.source):
                    if alias in irc.aliases:
                        del(irc.aliases[alias])
                        irc.reply(event, "Global alias {} deleted".format(alias))
                    else:
                        irc.reply(event, "ERROR: No global aliases named {} were found".format(alias))
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
                if "aliases" in irc.channels[channel]:
                    irc.reply(event, "Aliases for {} are: {}".format(channel, ", ".join(["\"{}\"".format(x) for x in irc.channels[channel]["aliases"]])))
                else:
                    irc.reply(event, "No aliases were found for {}".format(channel))
            else:
                irc.reply(event, "Global aliases are: {}".format(", ".join(["\"{}\"".format(x) for x in irc.aliases])))
    except (KeyError, IndexError):
        irc.reply(event, utils.gethelp("alias"))
        #print " ".join(["\"{}\"".format(x) for x in irc.channels["aliases"]])
        #" ".join(irc.channels[channel]["aliases"].keys())
