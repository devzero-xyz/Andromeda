from utils import *

name = "misc"
cmds = ["list", "ping", "moo", "echo", "action", "help", "version",
        "hm", "bm"]

def listcmd(irc, event, args):
    """[<plugin>]

    Lists plugins if no <plugin> is given, otherwise
    it lists commands in <plugin>
    """
    if len(args) > 0:
        try:
            plugin = args[0].lower()
            irc.reply(event, ", ".join(sorted(plugins[plugin])))
        except KeyError:
            irc.reply(event, "ERROR: No such plugin: {}".format(args[0]))
    else:
        irc.reply(event, ", ".join(sorted(plugins.keys())))
add_cmd(listcmd, "list")

@add_cmd
def ping(irc, event, args):
    """takes no arguments

    Checks if the bot is alive.
    """
    irc.reply(event, "pong")

@add_cmd
def moo(irc,event, args):
    """takes no arguments

    Replies with 'pmooooooooooooooooooooooooooooong!'
    """
    irc.reply(event, "pmooooooooooooooooooooooooooooong!")

@add_cmd
def echo(irc, event, args):
    """<text>

    Replies with the arguments given.
    """
    if len(args) > 0:
        irc.reply(event, "\u200b"+" ".join(args))

@add_cmd
def action(irc, event, args):
    """<text>

    Equivalent of /me <text>
    """
    if len(args) > 0:
        irc.reply(event, " ".join(args), action=True)

def cmdhelp(irc, event, args):
    """[<command>]

    Returns help for <command>. Use the 'list' command
    to get a list of all available plugins and commands.
    """
    if len(args) > 0:
        cmd = args[0].lower()
        irc.reply(event, gethelp(cmd))
    else:
        irc.reply(event, gethelp("help"))
add_cmd(cmdhelp, "help")

@add_cmd
def version(irc, event, args):
    """takes no arguments

    Returns the current version of the bot.
    """
    irc.reply(event, irc.version)

@add_cmd
def hm(irc, event, args):
    """[<nick>]

    Returns hostmask for <nick> (or your own if <nick>
    is not given) if it is known by the bot.
    """
    if len(args) == 0:
        nick = event.source.nick
    else:
        nick = args[0]
    host = gethm(irc, nick)
    if host:
        irc.reply(event, host)
    else:
        irc.reply(event, "ERROR: User not found: {}".format(nick))

@add_cmd
def bm(irc, event, args):
    """[<nick>]

    Returns generated banmask for <nick> (or your own
    if <nick> is not given).
    """
    if len(args) == 0:
        nick = event.source.nick
    else:
        nick = args[0]
    irc.reply(event, banmask(irc, nick))
