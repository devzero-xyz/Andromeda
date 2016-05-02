from jaraco.functools import first_invoke
from collections import defaultdict
from fnmatch import fnmatch
import irc.client as irclib
import functools
import threading
import requests
import inspect
import codecs
import socket
import queue
import code
import time
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
bfregex = re.compile("\S+!\S+@\S+\$\S+")
gotwho = threading.Event()
denied = None

def paste(payload):
    pastebin = "https://paste.indigotiger.me/"
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

def is_ignored(irc, hostmask, channel=None):
    hostmask = str(hostmask)
    nick = irclib.NickMask(hostmask).nick
    if is_owner(irc, hostmask, channel):
        return False
    if is_allowed(irc, hostmask, channel):
        return False
    for ignore in irc.ignored:
        if ignore.startswith("$a") and getacc(irc, nick, True):
            if ignore == "$a":
                return True
            else:
                ignore = ignore.lstrip("$a:")
                account = getacc(irc, nick, True)
                if irccmp(account, ignore):
                    return True
        elif fnmatch(irclower(hostmask), irclower(ignore)):
            return True
    if channel:
        try:
            ignored = irc.channels[channel].get("ignored", [])
            for ignore in ignored:
                if ignore.startswith("$a") and getacc(irc, nick, True):
                    if ignore == "$a":
                        return True
                    else:
                        ignore = ignore.lstrip("$a:")
                        account = getacc(irc, nick, True)
                        if irccmp(account, ignore):
                            return True
                elif fnmatch(irclower(hostmask), irclower(ignore)):
                    return True
        except KeyError:
            return False
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
            silence = irc.channels[channel].get("silence", irc.silence)
        except KeyError:
            silence = irc.silence
        try:
            trigger = irc.channels[channel].get("trigger", irc.trigger)
        except KeyError:
            trigger = irc.trigger
        if silence or is_ignored(irc, event.source, channel):
            return False
        elif msg.startswith(trigger) and len(trigger) > 0:
            return True
        elif len(msg.split()) > 0:
            if msg.split()[0].rstrip(":,") == irc.get_nick():
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
        aliases = irc.channels[channel].get("aliases", irc.aliases)
        factoids = irc.channels[channel].get("factoids", irc.factoids)
    except KeyError:
        trigger = irc.trigger
        aliases = irc.aliases
        factoids = irc.factoids
    for alias in irc.aliases:
        if alias not in aliases:
            aliases[alias] = irc.aliases[alias]
    for factoid in irc.factoids:
        if factoid not in factoids:
            factoids[factoid] = irc.factoids[factoid]
    if msg.startswith(trigger) and len(trigger) > 0:
        msg = msg.split()
        command = msg[0].replace(trigger, "", 1).lower()
        if len(msg) > 1:
            args = msg[1:]
        else:
            args = []
    elif msg.startswith(irc.get_nick()):
        msg = msg.split()
        if len(msg) > 1:
            command = msg[1].lower()
            if len(msg) > 2:
                args = msg[2:]
            else:
                args = []
        else:
            command = ""
            args = []
    else:
        msg = msg.split()
        command = msg[0].lower()
        if len(msg) > 1:
            args = msg[1:]
        else:
            args = []
    try:
        if command in aliases:
            alias = aliases[command].split()
            command = alias[0].lower()
            if len(alias) > 1:
                origargs = args
                args = alias[1:]
                if args:
                    try:
                        args = [arg
                        .replace("%n", event.source.nick)
                        .replace("%cc", event.target)
                        .replace("%h", irc.state["users"][event.source.nick]["host"])
                        .replace("%a", irc.state["users"][event.source.nick]["account"])
                        .replace("%u", irc.state["users"][event.source.nick]["user"])
                        .replace("%g", irc.state["users"][event.source.nick]["gecos"])
                        .replace("%cs", " ".join(irc.state["users"][event.source.nick]["channels"]))
                        for arg  in args]
                    except:
                        pass # User can't be found
                for arg in origargs:
                    args.append(arg)
        elif command in factoids:
            irc.reply(event, factoids[command])
            return
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

def getip(irc, hmask, use_cache=False):
    ip = None
    if not is_hostmask(hmask):
        hmask = gethm(irc, hmask, use_cache)
    hmask = irclib.NickMask(hmask)
    user = hmask.user
    host = hmask.host
    if host.startswith("gateway/"):
        if "/ip." in host:
            ip = host.split("/ip.")[1]
        elif host.endswith("/session"):
            try:
                hexip = codecs.decode(user, "hex")
                ip = socket.inet_ntop(socket.AF_INET, hexip)
            except (binascii.Error, ValueError):
                pass
    else:
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            pass
    return ip

def ban_affects(irc, channel, bmask):
    affected = []
    if bfregex.match(bmask):
        bmask = bmask.split("$")[0]
    try:
        for nick in irc.state["channels"][channel]["names"]:
            hmask = irclower(gethm(irc, nick, True))
            if fnmatch(hmask, irclower(bmask)):
                affected.append(nick)
            elif "@gateway/web/freenode/" in hmask:
                host = irclib.NickMask(hmask).host
                hmask = hmask.replace(host, getip(irc, nick, True))
                if fnmatch(hmask, irclower(bmask)):
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
        bm = "*!{}@{}".format(user, host)
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

def getop(irc, channel):
    if not irc.is_opped(irc.get_nick(), channel):
        if not irc.channels[channel].get("chanserv", irc.chanserv):
            return False
        irc.privmsg("ChanServ", "OP {}".format(channel))
        log.info("Waiting for op in {}".format(channel))
        denied = queue.Queue()
        while True:
            if irc.is_opped(irc.get_nick(), channel):
                    return True
            elif not denied.empty():
                denychan = denied.get()
                if irccmp(denychan, channel):
                    log.info("ChanServ denied op in {}".format(channel))
                    denied = None
                    return False
            time.sleep(0.2)
    else:
        return True

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

# Modified version of Throttler in jaraco.functools
class Throttler(object):
	"""
	Rate-limit a function (or other callable)
	"""
	def __init__(self, func, max_rate=float('Inf'), skip_for=0):
		if isinstance(func, Throttler):
			func = func.func
		self.func = func
		self.max_rate = max_rate
		self.skip_for = skip_for
		self.reset()

	def reset(self):
		self.last_called = 0

	def __call__(self, *args, **kwargs):
		self._wait()
		return self.func(*args, **kwargs)

	def _wait(self):
		"ensure at least 1/max_rate seconds from last call"
		elapsed = time.time() - self.last_called
		if elapsed > self.max_rate:
			self.called_times = 0
		if self.called_times > self.skip_for:
			must_wait = 1 / self.max_rate - elapsed
			time.sleep(max(0, must_wait))
		self.called_times += 1
		self.last_called = time.time()

	def __get__(self, obj, type=None):
		return first_invoke(self._wait, functools.partial(self.func, obj))
