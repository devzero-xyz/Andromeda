from collections import defaultdict
from fnmatch import fnmatch
import irc.client as irclib
import threading
import requests
import inspect
import code
import sys
import re

from log import log

global commands, plugins, handlers, gotwho

plugins = {}
commands = {}
handlers = {}
command_hooks = defaultdict(list)
argmodes = {"set": "bqeIkfljov", "unset": "bqeIkov"}
hmregex = re.compile("\S+!\S+@\S+")
gotwho = threading.Event()

def paste(payload):
    pastebin = "http://hastebin.com/"
    url = pastebin+"documents"
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return pastebin+response.json()["key"]

def add_cmd(func, name=None):
    if name is None:
        name = func.__name__
    commands[name] = func

def add_hook(func, command):
    command = command.upper()
    command_hooks[command].append(func)

def add_handler(func, plugin):
    name = func.__name__
    if not name.startswith("on_"):
        name = "on_"+name
    if not plugin in handlers:
        handlers[plugin] = {}
    handlers[plugin][name] = func
    
def is_owner(irc, hostmask, channel=None):
    hostmask = str(hostmask)
    nick = irclib.NickMask(hostmask).nick
    for owner in irc.owners:
        if owner.startswith("$a") and getacc(irc, nick, True):
            if owner == "$a":
                return True
            else:
                owner = owner.lstrip("$a:")
                account = getacc(irc, nick, True)
                if irccmp(account, owner):
                    return True
        elif fnmatch(irclower(hostmask), irclower(owner)):
            return True
    if channel:
        try:
            owners = irc.channels[channel].get("owners", [])
            for owner in owners:
                if owner.startswith("$a") and getacc(irc, nick, True):
                    if owner == "$a":
                        return True
                    else:
                        owner = owner.lstrip("$a:")
                        account = getacc(irc, nick, True)
                        if irccmp(account, owner):
                            return True
                elif fnmatch(irclower(hostmask), irclower(owner)):
                    return True
        except KeyError:
            return False
    return False

def is_allowed(irc, hostmask, channel=None):
    hostmask = str(hostmask)
    nick = irclib.NickMask(hostmask).nick
    if is_owner(irc, hostmask, channel):
        return True
    if channel:
        try:
            allowed = irc.channels[channel].get("allowed", [])
            for allow in allowed:
                if allow.startswith("$a") and getacc(irc, nick, True):
                    if allow == "$a":
                        return True
                    else:
                        allow = allow.lstrip("$a:")
                        account = getacc(irc, nick, True)
                        if irccmp(account, allow):
                            return True
                elif fnmatch(irclower(hostmask), irclower(allow)):
                    return True
        except KeyError:
            return False
    else:
        for allow in irc.allowed:
            if allow.startswith("$a") and getacc(irc, nick, True):
                if allow == "$a":
                    return True
                else:
                    allow = allow.lstrip("$a:")
                    account = getacc(irc, nick, True)
                    if irccmp(account, allow):
                        return True
            elif fnmatch(irclower(hostmask), irclower(allow)):
                return True
    return False

def is_hostmask(string):
    return hmregex.match(string)

def is_command(irc, conn, event):
    if is_private(event):
        return True
    elif event.type == "pubmsg" or event.type == "pubnotice":
        channel = event.target
        msg = event.arguments[0]
        try:
            trigger = irc.channels[channel].get("trigger", irc.trigger)
        except KeyError:
            trigger = irc.trigger
        if msg.startswith(trigger) and len(trigger) > 0:
            return True
        elif msg.startswith(irc.get_nick()):
            return True
    return False

def handle_command(irc, conn, event):
    msg = event.arguments[0]
    if not is_private(event):
        channel = event.target
    else:
        channel = event.source.nick
    try:
        trigger = irc.channels[channel].get("trigger", irc.trigger)
    except KeyError:
        trigger = irc.trigger
    if msg.startswith(trigger) and len(trigger) > 0:
        msg = msg.split()
        command = msg[0].replace(trigger, "", 1).lower()
        if len(msg) > 1:
            args = msg[1:]
        else:
            args = []
    elif msg.startswith(irc.get_nick()):
        msg = msg.split()
        command = msg[1].lower()
        if len(msg) > 2:
            args = msg[2:]
        else:
            args = []
    else:
        msg = msg.split()
        command = msg[0].lower()
        if len(msg) > 1:
            args = msg[1:]
        else:
            args = []
    try:
        func = commands[command]

    except KeyError:
        log.info("Got invalid command '{}' from {}".format(command, event.source))

    else:
        log.info("{} called by {} with args {}".format(command, event.source, args))
        t = threading.Thread(target=func, args=(irc, event, args))
        t.daemon = True
        t.start()

def is_private(event):
    return event.type == "privmsg" or event.type == "privnotice"

def irclower(string):
    string = str(string)
    string = string.lower()
    string = string.replace("[", "{")
    string = string.replace("]", "}")
    string = string.replace("\\", "|")
    string = string.replace("~", "^")
    return string

def irccmp(str1, str2):
    return irclower(str1) == irclower(str2)

def gethm(irc, nick, use_cache=False):
    hmask = None
    if not use_cache:
        gotwho.clear()
        irc.who(nick)
        while not gotwho.is_set():
            gotwho.wait()
    for user in irc.state["users"].keys():
        if irccmp(user, nick):
            nick = user
            user = irc.state["users"][nick]["user"]
            host = irc.state["users"][nick]["host"]
            hmask = irclib.NickMask.from_params(nick, user, host)
            break
    if gotwho.is_set():
        gotwho.clear()
    return hmask

def getacc(irc, nick, use_cache=False):
    account = None
    if not use_cache:
        gotwho.clear()
        irc.who(nick)
        while not gotwho.is_set():
            gotwho.wait()
    for user in irc.state["users"].keys():
        if irccmp(user, nick):
            if irc.state["users"][user]["account"]:
                account = irc.state["users"][user]["account"]
                break
    if gotwho.is_set():
        gotwho.clear()
    return account

def ban_affects(irc, channel, bmask):
    affected = []
    try:
        for nick in irc.state["channels"][channel]["names"]:
            if fnmatch(irclower(gethm(irc, nick, True)), irclower(bmask)):
                affected.append(nick)
        return affected
    except KeyError:
        return affected

def banmask(irc, hostmask):
    if is_hostmask(hostmask):
        hm = irclib.NickMask(hostmask)
    else:
        hm = gethm(irc, hostmask)
        if not hm:
            return "{}!*@*".format(hostmask)
    user = hm.user
    host = hm.host
    if host.startswith("gateway/"):
        if "/irccloud.com/" in host:
            uid = user[1:]
            host = host.split("/")
            host = "/".join(host[:-1])
            bm = "*!*{}@{}/*".format(uid, host)
            return bm
        elif "/ip." in host:
            host = host.split("/ip.")
            host = host[1]
            bm = "*!*@*{}".format(host)
            return bm
        else:
            host = host.split("/")
            host = "/".join(host[:-1])
            bm = "*!{}@{}/*".format(user, host)
            return bm
    elif host.startswith("nat/"):
        host = host.split("/")
        host = "/".join(host[:-1])
        bm = "*!{}@{}/*".format(user, host)
        return bm
    elif "/" in host:
        bm = "*!*@{}".format(host)
        return bm
    elif user.startswith("~"):
        bm = "*!*@{}".format(host)
        return bm
    else:
        bm = "*!{}@{}".join(user, host)
        return bm

def split_modes(modes):
    splitmodes = []
    argscount = 1
    setmode = True
    for mode in modes[0]:
        if mode == "+":
            setmode = True
            continue
        elif mode == "-":
            setmode = False
            continue
        if setmode:
            if mode in argmodes["set"]:
                modearg = modes[argscount]
                argscount += 1
                splitmodes.append("+{} {}".format(mode, modearg))
            else:
                splitmodes.append("+{}".format(mode))
        else:
            if mode in argmodes["unset"]:
                modearg = modes[argscount]
                argscount += 1
                splitmodes.append("-{} {}".format(mode, modearg))
            else:
                splitmodes.append("-{}".format(mode))
    return splitmodes

def unsplit_modes(modes):
    unsplitmodes = [""]
    finalmodes = []
    argscount = 0
    setmode = True
    for mode in modes:
        if mode.startswith("+"):
            if len(unsplitmodes[0]) == 0:
                unsplitmodes[0] = "+"
            elif not setmode:
                unsplitmodes[0] += "+"
            setmode = True
        elif mode.startswith("-"):
            if len(unsplitmodes[0]) == 0:
                unsplitmodes[0] = "-"
            elif setmode:
                unsplitmodes[0] += "-"
            setmode = False
        mode = mode.lstrip("+-")
        mode = mode.split()
        unsplitmodes[0] += mode[0]
        if len(mode) > 1:
            unsplitmodes.append(mode[1])
            argscount += 1
            if argscount == 4:
                finalmodes.append(" ".join(unsplitmodes))
                unsplitmodes = [""]
                argscount = 0
    if unsplitmodes != [""]:
        finalmodes.append(" ".join(unsplitmodes))
    return finalmodes

def gethelp(cmd):
    try:
        cmd = cmd.lower()
        func = commands[cmd]
        docstring = inspect.getdoc(func)
        if docstring:
            docstring = docstring.splitlines()
            if len(docstring) > 1:
                usage = docstring[0]
                info = " ".join(docstring[1:]).strip()
                return "({} {}) -- {}".format(cmd, usage, info)
            else:
                usage = docstring[0]
                return "({} {})".format(cmd, usage)
        else:
            return "No help found for: {}".format(cmd)
    except (NameError, KeyError):
        return "ERROR: No such command: {}".format(cmd)

class console(code.InteractiveConsole):
    def __init__(self, irc, utils, event):
        code.InteractiveConsole.__init__(self, {
            "irc": irc,
            "utils": utils,
            "event": event,
            "globals": globals
        })
        self.out = ""
        self.data = ""

    def write(self, data):
        self.data += data

    def commit(self, code):
        self.lastout = self.out
        msg = self.data
        msg = msg.rstrip("\n")
        self.out = ' | '.join(msg.splitlines())
        self.lastcode = code
        self.data = ""

    def showtraceback(self):
        err, msg, _ = sys.exc_info()
        self.write("%s: %s"%(err.__name__, msg))

    def showsyntaxerror(self, filename):
        self.showtraceback()

    def run(self, code):
        sys.stdout = self
        v = self.push(code)
        sys.stdout = sys.__stdout__
        self.commit(code)
        return v
