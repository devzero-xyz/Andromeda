from collections import OrderedDict
import json

def load(config_file):
    with open(config_file) as conf:
        return json.load(conf, object_pairs_hook=OrderedDict)

def save(config_file, config):
    with open(config_file, "w") as conf:
        json.dump(config, conf, indent=4)
        conf.write("\n")
def reload_config(bot):
    bot.config = load(bot.config_file)
    bot.server = bot.config["server"]
    bot.nick = bot.config["nick"]
    bot.port = bot.config.get("port", 6667)
    bot.ident = bot.config.get("ident", bot.nick)
    bot.gecos = bot.config.get("realname", bot.version)
    bot.quitmsg = bot.config.get("quitmsg", "Ctrl-C at console.")
    bot.bindaddr = bot.config.get("bindaddr", None)
    bot.ipv6 = bot.config.get("ipv6", False)
    bot.ssl = bot.config.get("ssl", False)
    bot.sasl = bot.config.get("sasl", False)
    bot.nickserv = bot.config.get("nickserv", False)
    bot.username = bot.config.get("username", None)
    bot.password = bot.config.get("password", None)
    bot.server_password = bot.config.get("server_password", None)
    bot.autojoin = bot.config.get("autojoin", True)
    bot.autorejoin = bot.config.get("autorejoin", False)
    bot.chanserv = bot.config.get("chanserv", False)
    bot.report = bot.config.get("report", None)
    bot.silence = bot.config.get("silence", False)
    bot.channels = bot.config.get("channels", {})
    bot.owners = bot.config.get("owners", [])
    bot.allowed = bot.config.get("allowed", [])
    bot.ignored = bot.config.get("ignored", [])
    bot.trigger = bot.config.get("trigger", "+")
    bot.umodes = bot.config.get("umodes", None)
    bot.plugins = bot.config.get("plugins", {})
    bot.throttle = bot.config.get("throttle", 1)
    bot.burst = bot.config.get("burst", 5)
    bot.aliases = bot.config.get("aliases", {})
    bot.factoids = bot.config.get("factoids", {})
def save_config(bot):
    bot.config["server"] = bot.server
    bot.config["nick"] = bot.nick
    bot.config["port"] = bot.port
    bot.config["ident"] = bot.ident
    bot.config["realname"] = bot.gecos
    bot.config["quitmsg"] = bot.quitmsg
    if type(bot.bindaddr) is tuple:
        bot.config["bindaddr"] = bot.bindaddr[0]
    else:
        bot.config["bindaddr"] = bot.bindaddr
    bot.config["ipv6"] = bot.ipv6
    bot.config["ssl"] = bot.ssl
    bot.config["sasl"] = bot.sasl
    bot.config["nickserv"] = bot.nickserv
    bot.config["username"] = bot.username
    bot.config["password"] = bot.password
    bot.config["server_password"] = bot.server_password
    bot.config["autojoin"] = bot.autojoin
    bot.config["autorejoin"] = bot.autorejoin
    bot.config["chanserv"] = bot.chanserv
    bot.config["report"] = bot.report
    bot.config["silence"] = bot.silence
    bot.config["channels"] = bot.channels
    bot.config["owners"] = bot.owners
    bot.config["allowed"] = bot.allowed
    bot.config["ignored"] = bot.ignored
    bot.config["trigger"] = bot.trigger
    bot.config["umodes"] = bot.umodes
    bot.config["plugins"] = bot.plugins
    bot.config["throttle"] = bot.throttle
    bot.config["burst"] = bot.burst
    save(bot.config_file, bot.config)
       
