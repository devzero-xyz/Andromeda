#!/usr/bin/python3
from time import sleep
import irc.connection
import irc.buffer
import irc.client
import threading
import thingdb
import glob
import imp
import ssl
import sys
import os

from log import log
import config
import utils

mtimes = {}

def reload_handlers(init=False):
    handlers = set(glob.glob(os.path.join("handlers", "*.py")))
    for filename in handlers:
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            mtimes[filename] = mtime
            try:
                eval(compile(open(filename, "U").read(), filename, "exec"), globals())
            except Exception as e:
                log.critical("Unable to reload {}: {}".format(filename, e))
                if init:
                    sys.exit(1)
                continue
            log.info("(Re)Loaded {}".format(filename))

def reload_plugins(irc, init=False):
    plugins_folder = [os.path.join(os.getcwd(), 'plugins')]
    plugins = set(glob.glob(os.path.join("plugins", "*.py")))
    for plugin in plugins:
        _plugin = os.path.join(os.getcwd(), plugin)
        mtime = os.stat(_plugin).st_mtime
        if mtime != mtimes.get(_plugin):
            mtimes[_plugin] = mtime
            try:
                moduleinfo = imp.find_module(plugin.split("/")[1].split(".")[0], plugins_folder)
                pl = imp.load_source(plugin, moduleinfo[1])
            except ImportError as e:
                if str(e).startswith('No module named'):
                    log.error("Failed to load plugin {}: the plugin could not be found.".fortmat(plugin))
                else:
                    log.error("Failed to load plugin {}: import error {}".format(plugin, str(e)))
                    if init:
                        sys.exit(1)
            except BaseException as e:
                log.error(e)

            else:
                if hasattr(pl, 'main'):
                    pl.main(irc)
                    log.debug("Calling main() function of plugin {}".format(pl))
                try:
                    if pl.name in utils.plugins.keys():
                        del(utils.plugins[pl.name])
                    utils.plugins[pl.name] = pl.cmds
                    irc.state["plugins"][pl.name] = {}
                except AttributeError:
                    pass
            log.info("(Re)Loaded {}".format(_plugin))

def reload_config(irc):
    if irc.conf_mtime != os.stat(config_file).st_mtime:
        irc.conf_mtime = os.stat(config_file).st_mtime
        irc.reload_config()
        log.info("(Re)Loaded config")

class IRC(irc.client.SimpleIRCClient):

    def __init__(self):
        irc.client.SimpleIRCClient.__init__(self)
        self.config_file = config_file
        self.conf_mtime = None
        self.connected = False
        if not os.path.exists("state.db"):
            thingdb.save({}, "state.db")
        self.state = thingdb.start("state.db")
        if "server" not in self.state:
            self.state["server"] = {}
        if "channels" not in self.state:
            self.state["channels"] = {}
        if "users" not in self.state:
            self.state["users"] = {}
        if "plugins" not in self.state:
            self.state["plugins"] = {}
        self.version = "Andromeda 2.0.0-dev"
        reload_config(self)
        reload_handlers(init=True)
        reload_plugins(self, init=True)
        self.identified = not self.sasl and not self.nickserv
        if self.bindaddr:
            self.bindaddr = (self.bindaddr, 0)
        if self.ssl:
            self.connect_factory = irc.connection.Factory(
                                                    bind_address=self.bindaddr,
                                                    wrapper=ssl.wrap_socket,
                                                    ipv6=self.ipv6)
        else:
            self.connect_factory = irc.connection.Factory(
                                                    bind_address=self.bindaddr,
                                                    ipv6=self.ipv6)
        self.connection.buffer_class = irc.buffer.LenientDecodingLineBuffer
        self.caps = ["account-notify", "extended-join"]
        if self.sasl:
            self.caps.append("sasl")
        log.info("Connecting to {}/{} as {}".format(self.server, str(self.port),
                                                    self.nick))
        self.connect(self.server, self.port, self.nick,self.server_password,
                     self.ident, self.gecos, self.connect_factory, self.caps)
        self.connection.add_global_handler("all_events", self.on_all_events)
        self.fifo_thread = threading.Thread(target=self.fifo)
        self.fifo_thread.daemon = True
        self.config_timer = threading.Timer(300, self.save_config)
        self.config_timer.daemon = True
        try:
            self.start()
        except KeyboardInterrupt:
            self.quit("Ctrl-C at console.")
            sys.exit(0)

    def reload_config(self):
        self.config = config.load(self.config_file)
        self.server = self.config["server"]
        self.nick = self.config["nick"]
        self.port = self.config.get("port", 6667)
        self.ident = self.config.get("ident", self.nick)
        self.gecos = self.config.get("realname", self.version)
        self.bindaddr = self.config.get("bindaddr", None)
        self.ipv6 = self.config.get("ipv6", False)
        self.ssl = self.config.get("ssl", False)
        self.sasl = self.config.get("sasl", False)
        self.nickserv = self.config.get("nickserv", False)
        self.username = self.config.get("username", None)
        self.password = self.config.get("password", None)
        self.server_password = self.config.get("server_password", None)
        self.autojoin = self.config.get("autojoin", True)
        self.autorejoin = self.config.get("autorejoin", False)
        self.chanserv = self.config.get("chanserv", False)
        self.channels = self.config.get("channels", {})
        self.owners = self.config.get("owners", [])
        self.allowed = self.config.get("allowed", [])
        self.trigger = self.config.get("trigger", "+")
        self.umodes = self.config.get("umodes", None)
        self.plugins = self.config.get("plugins", {})

    def save_config(self):
        self.config["server"] = self.server
        self.config["nick"] = self.nick
        self.config["port"] = self.port
        self.config["ident"] = self.ident
        self.config["realname"] = self.gecos
        self.config["bindaddr"] = self.bindaddr
        self.config["ipv6"] = self.ipv6
        self.config["ssl"] = self.ssl
        self.config["sasl"] = self.sasl
        self.config["nickserv"] = self.nickserv
        self.config["username"] = self.username
        self.config["password"] = self.password
        self.config["server_password"] = self.server_password
        self.config["autojoin"] = self.autojoin
        self.config["autorejoin"] = self.autorejoin
        self.config["chanserv"] = self.chanserv
        self.config["channels"] = self.channels
        self.config["owners"] = self.owners
        self.config["allowed"] = self.allowed
        self.config["trigger"] = self.trigger
        self.config["umodes"] = self.umodes
        self.config["plugins"] = self.plugins
        config.save(self.config_file, self.config)
        thingdb.save(self.state, "state.db")
        log.info("Config saved to file.")

    def get_nick(self):
        return self.connection.get_nickname()

    def on_all_events(self, conn, event):
        reload_config(self)
        reload_handlers()
        reload_plugins(self)
        if event.type != "all_raw_messages":
            try:
                func = globals()['on_'+event.type]
            except KeyError:
                pass
            else:
                func(self, conn, event)

            try:
                funcs = []
                for plugin in utils.handlers:
                    try:
                        funcs.append(utils.handlers[plugin]["on_"+event.type])
                    except KeyError:
                        continue
            except KeyError:
                pass
            else:
                for func in funcs:
                    t = threading.Thread(target=func, args=(self, conn, event))
                    t.daemon = True
                    t.start()

    def on_nicknameinuse(self, conn, event):
        if not self.connected:
            log.error("Primary nick {} in use! Trying a fallback one.".format(self.nick))
            self.nick(self.connection.get_nickname()+"_")

    def on_unavailresource(self, conn, event):
        if not self.connected:
            log.error("Primary nick is unavailable! Trying a fallback one.")
            self.nick(self.connection.get_nickname()+"_")

    def on_disconnect(self, conn, event):
        self.__init__()

    @staticmethod
    def is_channel(channel):
        return irc.client.is_channel(channel)

    def is_opped(self, nick, channel):
        try:
            return nick in self.state["channels"][channel]["ops"]
        except KeyError:
            return False

    def is_voiced(self, nick, channel):
        try:
            return nick in self.state["channels"][channel]["voices"]
        except KeyError:
            return False

    def fifo(self):
        if not os.path.exists("fifo"):
            os.mkfifo("fifo")
        with open("fifo", "r") as pipein:
            while True:
                line = pipein.readline()[:-1]
                if len(line) > 0:
                    self.send(line)
                sleep(0.2)

    def action(self, target, msg):
        self.connection.action(target, msg)

    def ctcp(self, ctcptype, target, args=None):
        if args:
            self.connection.ctcp(ctcptype, target, args)
        else:
            self.connection.ctcp(ctcptype, target)

    def ctcp_reply(self, target, args):
        self.connection.ctcp_reply(target, args)

    def join(self, channel, key=None):
        if key:
            self.connection.join(channel, key)
        else:
            self.connection.join(channel)

    def part(self, channel, msg=None):
        if msg:
            self.connection.part(channel, msg)
        else:
            self.connection.part(channel)

    def send(self, line):
        self.connection.send_raw(line)

    def chgnick(self, newnick):
        self.connection.nick(newnick)

    def mode(self, channel, modes):
        self.connection.mode(channel, modes)

    def notice(self, target, msg):
        msg = str(msg)
        msgs = [msg[i:i+480] for i in range(0, len(msg), 480)]
        if len(msgs) > 3:
            self.connection.notice(target, utils.paste("".join(msgs)))
        else:
            for msg in msgs:
                msg = msg.strip("\r\n")
                self.connection.notice(target, msg)

    def privmsg(self, target, msg):
        msg = str(msg)
        msgs = [msg[i:i+480] for i in range(0, len(msg), 480)]
        if len(msgs) > 3:
            self.connection.privmsg(target, utils.paste("".join(msgs)))
        else:
            for msg in msgs:
                msg = msg.strip("\r\n")
                self.connection.privmsg(target, msg)

    def kick(self, channel, nick, msg="Goodbye."):
        self.connection.kick(channel, nick, msg)

    def remove(self, channel, nick, msg="Goodbye."):
        self.send("REMOVE {} {} :{}".format(channel, nick, msg))

    def reply(self, event, msg, action=False):
        if irc.client.is_channel(event.target):
            if action:
                self.action(event.target, msg)
            else:
                self.privmsg(event.target, msg)
        else:
            if action:
                self.action(event.source.nick, msg)
            else:
                self.privmsg(event.source.nick, msg)

    def quit(self, message=None):
        if message:
            self.connection.quit(message)
        else:
            self.connection.quit()
        self.save_config()

    def who(self, target):
        if "extended-join" in self.state["server"]["caps"]:
            self.send("WHO {} %tcnuhraf,162".format(target))
        else:
            self.connection.who(target)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        config_file = sys.argv[1]
        irc = IRC()
    else:
        log.critical("No config file specified.")
        sys.exit(1)
