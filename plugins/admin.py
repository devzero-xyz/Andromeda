from fnmatch import fnmatch
from time import sleep
import subprocess
import random as rand
import queue

from utils import *
import utils

name = "admin"
cmds = ["join", "part", "nick", "quit", "raw", ">>", ">", "op", "deop",
        "voice", "devoice", "ban", "kban", "unban", "sop", "sdeop",
        "svoice", "sdevoice", "squiet", "sunquiet", "kick", "quiet",
        "unquiet"]

def main(irc):
    if not name in irc.plugins:
        irc.plugins[name] = {}
    if not name in irc.state["plugins"]:
        irc.state["plugins"][name] = {}
    irc.state["plugins"][name]["opped"] = None
    irc.state["plugins"][name]["denied"] = None

@add_cmd
def join(irc, event, args):
    """<channel> [<key>,<channel>...]

    Makes the bot join <channel> using <key> if given.
    """
    args = " ".join(args)
    for channel in args.split(","):
        channel = channel.split()
        if is_allowed(irc, event.source, channel[0]):
            if irc.is_channel(channel[0]):
                if len(channel) > 1:
                    irc.join(channel[0], channel[1])
                else:
                    irc.join(channel[0])
            else:
                irc.reply(event, "ERROR: Invalid channel: {}".format(channel[0]))

@add_cmd
def part(irc, event, args):
    """[<channel>] [<message>]

    Parts <channel> with <message> if given. <channel>
    is only necessary if the command isn't given in the
    channel itself.
    """
    if len(args) > 0:
        if irc.is_channel(args[0]):
            channel = args[0]
            if len(args) > 1:
                reason = " ".join(args[1:])
            else:
                reason = event.source.nick
        elif not is_private(event):
            channel = event.target
            reason = " ".join(args)
        else:
            irc.reply(event, "ERROR: No channel specified.")
            return
    elif not is_private(event):
        channel = event.target
        reason = event.source.nick
    else:
        irc.reply(event, "ERROR: No channel specified.")
        return
    if is_owner(irc, event.source, channel):
        irc.part(channel, reason)

@add_cmd
def nick(irc, event, args):
    """<nick>

    Changes the bot's nick to <nick>.
    """
    if is_allowed(irc, event.source): # Checks if the user is on the global allowed list
        irc.chgnick(args[0]) # Calls the nickname change if the above function returns True

def botquit(irc, event, args):
    """[<message>]

    Makes the bot quit with <message> if given.
    """
    if is_owner(irc, event.source):
        if len(args) > 0:
            irc.quit(" ".join(args))
        else:
            irc.quit(event.source.nick)
add_cmd(botquit, "quit")

@add_cmd
def raw(irc, event, args):
    """<command>

    Sends <command> to the IRC server.
    """
    if is_owner(irc, event.source):
        irc.send(" ".join(args))

def _exec(irc, event, args):
    """<code>

    Executes <code> in a Python interpreter.
    """
    if is_owner(irc, event.source):
        botenv = utils.console(irc, utils, event)
        if not botenv.run(" ".join(args)) and botenv.out:
            irc.reply(event, botenv.out)
add_cmd(_exec, ">>")

def _shell(irc, event, args):
    """<command>

    Executes <command> on the shell.
    """
    if is_owner(irc, event.source):
        args = " ".join(args)
        try:
            s = subprocess.check_output(args+" | ./ircize --remove", stderr=subprocess.STDOUT, shell=True)
            if s:
                s = s.decode()
                for line in str(s).splitlines():
                    irc.reply(event, line)
        except subprocess.CalledProcessError as e:
            irc.reply(event, e)
add_cmd(_shell, ">")

@add_cmd
def sop(irc, event, args):
    """[<channel>] [<nick>...]

    Ops <nick> (or the bot if no <nick> is given) in <channel> using services.
    <channel> is only necessary if the command isn't sent in the channel itself.
    """
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [irc.get_nick()]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [irc.get_nick()]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [irc.get_nick()]

    except IndexError:
        irc.reply(event, utils.gethelp("sop"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            try:
                if irc.channels[channel].get("chanserv", irc.chanserv):
                    for nick in nicks:
                        if irc.is_opped(nick, channel):
                            nicks.remove(nick)
                    if len(nicks) > 0:
                        irc.privmsg("ChanServ", "OP {} {}".format(channel, " ".join(nicks)))
            except KeyError:
                pass

@add_cmd
def sdeop(irc, event, args):
    """[<channel>] [<nick>...]

    Deops <nick> (or the bot if no <nick> is given) in <channel> using services.
    <channel> is only necessary if the command isn't sent in the channel itself.
    """
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [irc.get_nick()]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [irc.get_nick()]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [irc.get_nick()]

    except IndexError:
        irc.reply(event, utils.gethelp("sdeop"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            try:
                if irc.channels[channel].get("chanserv", irc.chanserv):
                    for nick in nicks:
                        if not irc.is_opped(nick, channel):
                            nicks.remove(nick)
                    if len(nicks) > 0:
                        irc.privmsg("ChanServ", "DEOP {} {}".format(channel, " ".join(nicks)))
            except KeyError:
                pass

@add_cmd
def svoice(irc, event, args):
    """[<channel>] [<nick>...]

    Voices <nick> (or the bot if no <nick> is given) in <channel> using services.
    <channel> is only necessary if the command isn't sent in the channel itself.
    """
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [irc.get_nick()]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [irc.get_nick()]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [irc.get_nick()]

    except IndexError:
        irc.reply(event, utils.gethelp("svoice"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            try:
                if irc.channels[channel].get("chanserv", irc.chanserv):
                    for nick in nicks:
                        if irc.is_voiced(nick, channel):
                            nicks.remove(nick)
                    if len(nicks) > 0:
                        irc.privmsg("ChanServ", "VOICE {} {}".format(channel, " ".join(nicks)))
            except KeyError:
                pass

@add_cmd
def sdevoice(irc, event, args):
    """[<channel>] [<nick>...]

    Devoices <nick> (or the bot if no <nick> is given) in <channel> using services.
    <channel> is only necessary if the command isn't sent in the channel itself.
    """
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [irc.get_nick()]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [irc.get_nick()]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [irc.get_nick()]

    except IndexError:
        irc.reply(event, utils.gethelp("sdevoice"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            try:
                if irc.channels[channel].get("chanserv", irc.chanserv):
                    for nick in nicks:
                        if not irc.is_voiced(nick, channel):
                            nicks.remove(nick)
                    if len(nicks) > 0:
                        irc.privmsg("ChanServ", "DEVOICE {} {}".format(channel, " ".join(nicks)))
            except KeyError:
                pass

@add_cmd
def squiet(irc, event, args):
    """[<channel>] <nick|hostmask> [<nick|hostmask>...]

    Quiets <nick> in <channel> using services. <channel> is only necessary
    if the command isn't sent in the channel itself.
    """
    try:
        if utils.is_private(event):
            channel = args[0]
            nicks = args[1:]
        else:
            if irc.is_channel(args[0]):
                channel = args[0]
                nicks = args[1:]
            else:
                channel = event.target
                nicks = args

    except IndexError:
        irc.reply(event, utils.gethelp("squiet"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            try:
                if irc.channels[channel].get("chanserv", irc.chanserv):
                    irc.privmsg("ChanServ", "QUIET {} {}".format(channel, " ".join(nicks)))
            except KeyError:
                pass

@add_cmd
def sunquiet(irc, event, args):
    """[<channel>] [<nick|hostmask>...]

    Unquiets <nick> (or yourself if no <nick> is given) in <channel>
    using services. <channel> is only necessary if the command isn't
    sent in the channel itself.
    """
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [event.source.nick]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [event.source.nick]

    except IndexError:
        irc.reply(event, utils.gethelp("sunquiet"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            try:
                if irc.channels[channel].get("chanserv", irc.chanserv):
                    irc.privmsg("ChanServ", "UNQUIET {} {}".format(channel, " ".join(nicks)))
            except KeyError:
                pass

@add_cmd
def op(irc, event, args):
    """[<channel>] [<nick>...]

    Ops <nick> (or yourself if no <nick> is specified) in <channel>.
    <channel> is only necessary if the command isn't sent in the
    channel itself.
    """
    setmodes = []
    try:
        if len(args) == 0:
            nicks = [event.source.nick]
            channel = event.target
        elif irc.is_channel(args[0]):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            nicks = args
            channel = event.target

    except IndexError:
        irc.reply(event, utils.gethelp("op"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            already_op = irc.is_opped(irc.get_nick(), channel)
            if "*" in nicks:
                nicks = irc.state["channels"][channel]["names"]
            for nick in nicks:
                if not irc.is_opped(nick, channel):
                    setmodes.append("+o {}".format(nick))
            if len(setmodes) == 0:
                return
            if not already_op and irc.get_nick() not in nicks:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def deop(irc, event, args):
    """[<channel>] [<nick>...]

    Deops <nick> (or yourself if no <nick> is specified) in <channel>.
    <channel> is only necessary if the command isn't set in the channel
    itself.
    """
    setmodes = []
    try:
        if len(args) == 0:
            nicks = [event.source.nick]
            channel = event.target
        elif irc.is_channel(args[0]):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            nicks = args
            channel = event.target

    except IndexError:
        irc.reply(event, utils.gethelp("deop"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            already_op = irc.is_opped(irc.get_nick(), channel)
            if "*" in nicks:
                nicks = irc.state["channels"][channel]["names"]
            for nick in nicks:
                if irc.is_opped(nick, channel):
                    setmodes.append("-o {}".format(nick))
            if len(setmodes) == 0:
                return
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def voice(irc, event, args):
    """[<channel>] [<nick>...]

    Voices <nick> (or yourself if no <nick> is specified) in <channel>.
    <channel> is only necessary if the command isn't sent in the channel
    itself.
    """
    setmodes = []
    try:
        if len(args) == 0:
            nicks = [event.source.nick]
            channel = event.target
        
        elif irc.is_channel(args):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            nicks = args
            channel = event.target

    except IndexError:
        irc.reply(event, utils.gethelp("devoice"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            already_op = irc.is_opped(irc.get_nick(), channel)
            if "*" in nicks:
                nicks = irc.state["channels"][channel]["names"]
            for nick in nicks:
                if not irc.is_voiced(nick, channel):
                    setmodes.append("+v {}".format(nick))
            if len(setmodes) == 0:
                return
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def devoice(irc, event, args):
    """[<channel>] [<nick>...]
    
    Devoices <nick> (or yourself if no <nick> is specified) in <channel>.
    <channel> is only necessary if the command isn't sent in the channel
    itself.
    """
    setmodes = []
    try:
        if len(args) == 0:
            nicks = [event.source.nick]
            channel = event.target
        elif irc.is_channel(args[0]):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            nicks = args
            channel = event.target

    except IndexError:
        irc.reply(event, utils.gethelp("devoice"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            already_op = irc.is_opped(irc.get_nick(), channel)
            if "*" in nicks:
                nicks = irc.state["channels"][channel]["names"]
            for nick in nicks:
                if irc.is_voiced(nick, channel):
                    setmodes.append("-v {}".format(nick))
            if len(setmodes) == 0:
                return
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def ban(irc, event, args):
    """[<channel>] <nick|hostmask> [<nick|hostmask>...]

    Bans <nick> in <channel>. <channel> is only necessary if the command
    isn't sent in the channel itself.
    """
    setmodes = []
    affected = []
    try:
        if utils.is_private(event):
            channel = args[0]
            nicks = args[1:]
        else:
            if irc.is_channel(args[0]):
                channel = args[0]
                nicks = args[1:]
            else:
                channel = event.target
                nicks = args

    except IndexError:
        irc.reply(event, utils.gethelp("ban"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            for nick in nicks:
                if utils.is_hostmask(nick):
                    bmask = nick
                else:
                    bmask = utils.banmask(irc, nick)
                setmodes.append("+b {}".format(bmask))
                for affect in utils.ban_affects(irc, channel, bmask):
                    if not affect in affected:
                        affected.append(affect)
            for nick in affected:
                if irc.is_opped(nick, channel):
                    setmodes.append("-o {}".format(nick))
                if irc.is_voiced(nick, channel):
                    setmodes.append("-v {}".format(nick))
            if len(setmodes) == 0:
                return
            already_op = irc.is_opped(irc.get_nick(), channel)
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick())) # remove op from self after ban
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def kban(irc, event, args):
    """[<channel>] <nick|hostmask> [<nick|hostmask>...] [:][<reason>]

    Bans <nick> in <channel> and kicks anyone affected using <reason>
    as the kick message if specified. <channel> is only necessary if
    the command isn't sent in the channel itself. It is recommended to
    use ':' as a seperator between <nick> and <reason>, otherwise, if
    there's a nick in the channel matching the first word in reason it
    will be kicked.
    """
    prepare_nicks = []
    setmodes = []
    affected = []
    reason = None
    try:
        if utils.is_private(event):
            channel = args[0]
            nicks = args[1:]

        else:
            if irc.is_channel(args[0]):
                channel = args[0]
                nicks = args[1:]

            else:
                channel = event.target
                nicks = args

    except IndexError:
        irc.reply(event, utils.gethelp("kban"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            for nick in nicks:
                if nick in irc.state["channels"][channel]["names"] and nick not in prepare_nicks and not nick.startswith(":"):
                    prepare_nicks.append(nick)
                elif utils.is_hostmask(nick):
                    prepare_nicks.append(nick)
                else:
                    reason = " ".join(nicks[len(prepare_nicks):]).lstrip(": ")
                    break
            nicks = prepare_nicks
            for nick in nicks:
                if utils.is_hostmask(nick):
                    bmask = nick
                else:
                    bmask = utils.banmask(irc, nick)
                setmodes.append("+b {}".format(bmask))
                for affect in utils.ban_affects(irc, channel, bmask):
                    if affect not in affected:
                        if irc.is_opped(irc, affect, channel):
                            setmodes.append("-o {}".format(affect))
                        if irc.is_voiced(irc, affect, channel):
                            setmodes.append("-v {}".format(affect))
                        affected.append(affect)
            if len(setmodes) == 0:
                return
            already_op = irc.is_opped(irc.get_nick(), channel)
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)
                for nick in affected:
                    if reason:
                        irc.kick(channel, nick, reason)
                    else:
                        irc.kick(channel, nick)
                if not already_op:
                    irc.mode(channel, "-o {}".format(irc.get_nick()))

@add_cmd
def kick(irc, event, args):
    """[<channel>] <nick> [<nick>...] [:][<reason>]

    Kicks <nick> in <channel>. <channel> is only necessary if the
    command isn't sent in the channel itself. It is recommended to
    use ':' as a seperator between <nick> and <reason>, otherwise, if
    there's a nick in the channel matching the first word in reason it
    will be kicked.
    """
    prepare_nicks = []
    reason = None
    try:
        if utils.is_private(event):
            channel = args[0]
            nicks = args[1:]

        else:
            if irc.is_channel(args[0]):
                channel = args[0]
                nicks = args[1:]

            else:
                channel = event.target
                nicks = args

    except IndexError:
        irc.reply(event, utils.gethelp("kick"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            for nick in nicks:
                if nick in irc.state["channels"][channel]["names"] and nick not in prepare_nicks and not nick.startswith(":"):
                    prepare_nicks.append(nick)
                else:
                    reason = " ".join(nicks[len(prepare_nicks):]).lstrip(": ")
                    break
            nicks = prepare_nicks
            already_op = irc.is_opped(irc.get_nick(), channel)
            gotop = getop(irc, channel)
            if gotop:
                for nick in nicks:
                    if reason:
                        irc.kick(channel, nick, reason)
                    else:
                        irc.kick(channel, nick)
                if not already_op:
                    irc.mode(channel, "-o {}".format(irc.get_nick()))

@add_cmd
def unban(irc, event, args):
    """[<channel>] [<nick|hostmask>...]

    Unbans <nick> (or yourself if no <nick> is specified) in <channel>.
    <channel> is only necessary if the command isn't sent in the channel
    itself.
    """
    setmodes = []
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [event.source.nick]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [event.source.nick]

    except IndexError:
        irc.reply(event, utils.gethelp("unban"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            for nick in nicks:
                if utils.is_hostmask(nick):
                    hmask = nick
                else:
                    hmask = utils.gethm(irc, nick)
                if hmask and channel in irc.state["channels"]:
                    for bmask in irc.state["channels"][channel]["bans"]:
                        if fnmatch(utils.irclower(hmask), utils.irclower(bmask)):
                            setmodes.append("-b {}".format(bmask))
                else:
                    return
            if len(setmodes) == 0:
                return
            already_op = irc.is_opped(irc.get_nick(), channel)
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def quiet(irc, event, args):
    """[<channel>] <nick|hostmask> [<nick|hostmask>...]

    Quiets <nick> in <channel>. <channel> is only necessary if the command
    isn't sent in the channel itself.
    """
    setmodes = []
    affected = []
    try:
        if utils.is_private(event):
            channel = args[0]
            nicks = args[1:]
        else:
            if irc.is_channel(args[0]):
                channel = args[0]
                nicks = args[1:]
            else:
                channel = event.target
                nicks = args

    except IndexError:
        irc.reply(event, utils.gethelp("quiet"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            for nick in nicks:
                if utils.is_hostmask(nick):
                    bmask = nick
                else:
                    bmask = utils.banmask(irc, nick)
                setmodes.append("+q {}".format(bmask))
                for affect in utils.ban_affects(irc, channel, bmask):
                    if not affect in affected:
                        affected.append(affect)
            for nick in affected:
                if irc.is_opped(nick, channel):
                    setmodes.append("-o {}".format(nick))
                if irc.is_voiced(nick, channel):
                    setmodes.append("-v {}".format(nick))
            if len(setmodes) == 0:
                return
            already_op = irc.is_opped(irc.get_nick(), channel)
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def unquiet(irc, event, args):
    """[<channel>] [<nick|hostmask>...]

    Unquiets <nick> (or yourself if no <nick> is specified) in <channel>.
    <channel> is only necessary if the command isn't sent in the channel
    itself.
    """
    setmodes = []
    try:
        if utils.is_private(event):
            channel = args[0]
            if len(args) > 1:
                nicks = args[1:]
            else:
                nicks = [event.source.nick]
        else:
            if len(args) > 0:
                if irc.is_channel(args[0]):
                    channel = args[0]
                    if len(args) > 1:
                        nicks = args[1:]
                    else:
                        nicks = [event.source.nick]
                else:
                    channel = event.target
                    nicks = args
            else:
                channel = event.target
                nicks = [event.source.nick]

    except IndexError:
        irc.reply(event, utils.gethelp("unquiet"))

    else:
        if utils.is_allowed(irc, event.source, channel):
            for nick in nicks:
                if utils.is_hostmask(nick):
                    hmask = nick
                else:
                    hmask = utils.gethm(irc, nick)
                if hmask and channel in irc.state["channels"]:
                    for bmask in irc.state["channels"][channel]["quiets"]:
                        if fnmatch(utils.irclower(hmask), utils.irclower(bmask)):
                            setmodes.append("-q {}".format(bmask))
                else:
                    return
            if len(setmodes) == 0:
                return
            already_op = irc.is_opped(irc.get_nick(), channel)
            if not already_op:
                setmodes.append("-o {}".format(irc.get_nick()))
            gotop = getop(irc, channel)
            if gotop:
                for mode in utils.unsplit_modes(setmodes):
                    irc.mode(channel, mode)

@add_cmd
def random(irc, event, args): # I'll delete this after
    """takes no arguments

    Returns random statement
    """
    random_events = ["moo{}".format("o"*rand.randint(0, 100)), "lol"]
    irc.reply(event, rand.choice(random_events))

def getop(irc, channel):
    if not irc.is_opped(irc.get_nick(), channel):
        if not irc.channels[channel].get("chanserv", irc.chanserv):
            return False
        irc.privmsg("ChanServ", "OP {}".format(channel))
        log.info("Waiting for op in {}".format(channel))
        irc.state["plugins"][name]["opped"] = queue.Queue()
        irc.state["plugins"][name]["denied"] = queue.Queue()
        while True:
            if not irc.state["plugins"][name]["opped"].empty():
                opchan = irc.state["plugins"][name]["opped"].get()
                if utils.irccmp(opchan, channel):
                    irc.state["plugins"][name]["opped"] = None
                    irc.state["plugins"][name]["denied"] = None
                    return True
            elif not irc.state["plugins"][name]["denied"].empty():
                denychan = irc.state["plugins"][name]["denied"].get()
                if utils.irccmp(denychan, channel):
                    log.info("ChanServ denied op in {}".format(channel))
                    irc.state["plugins"][name]["opped"] = None
                    irc.state["plugins"][name]["denied"] = None
                    return False
            sleep(0.2)
    else:
        return True

def on_mode(irc, conn, event):
    channel = event.target
    modes = utils.split_modes(event.arguments)
    for mode in modes:
        if mode.startswith("+b"):
            mask = mode.split()[1]
            affects = utils.ban_affects(irc, channel, mask)
            names = irc.state["channels"][channel]["names"]
            if len(affects) >= len(names) / 2:
                setmodes = []
                bmask = utils.banmask(irc, event.source)
                setmodes.append("-b {}".format(mask))
                baffects = utils.ban_affects(irc, channel, bmask)
                for nick in baffects:
                    if irc.is_opped(nick, channel):
                        setmodes.append("-o {}".format(nick))
                setmodes.append("+b {}".format(bmask))
                already_op = irc.is_opped(irc.get_nick(), channel)
                gotop = getop(irc, channel)
                if gotop:
                    for modes in utils.unsplit_modes(setmodes):
                        irc.mode(channel, modes)
                    for nick in baffects:
                        irc.kick(channel, nick)
                    if not already_op:
                        irc.mode(channel, "-o {}".format(irc.get_nick()))
    if not name in irc.state["plugins"]:
        irc.state["plugins"][name] = {}
    if irc.state["plugins"][name]["opped"]:
        for mode in modes:
            if mode == "+o {}".format(irc.get_nick()):
                irc.state["plugins"][name]["opped"].put_nowait(channel)
add_handler(on_mode, name)

def on_privnotice(irc, conn, event):
    if not name in irc.state["plugins"]:
        irc.state["plugins"][name] = {}
    nick = event.source.nick
    msg = event.arguments[0]
    if nick == "ChanServ" and irc.state["plugins"][name]["denied"]:
        if "You are not authorized" in msg:
            channel = msg.split("\x02")[3]
            irc.state["plugins"][name]["denied"].put(channel)
        elif "is not registered" in msg:
            channel = msg.split("\x02")[1]
            irc.state["plugins"][name]["denied"].put(channel)
add_handler(on_privnotice, name)
