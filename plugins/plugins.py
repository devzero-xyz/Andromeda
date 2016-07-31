from threading import Thread
from utils import add_cmd
from time import sleep
import re
import utils
import os
import requests
import bs4

plugin_sources = {
    "https://github.com/devzero-xyz/Andromeda/tree/master/plugins": {},
    "https://github.com/devzero-xyz/Andromeda-Plugins": {},
    "https://github.com/IndigoTiger/Andromeda-plugins": {},
    "https://github.com/itslukej/Andromeda-plugins": {}
}

name = "plugins"
cmds = ["update", "available", "updates", "install", "uninstall"] # Install <plugin>, uninstall <plugin> <<< TODO

update_refresh_rate = 5 # Seconds | Recommended for minimal RAM use (300) 5 mins
installed_plugins = os.listdir("plugins")
active_plugins = [plugin.replace(".py", "") for plugin in utils.plugins.keys()]

def main(irc):
    if name not in irc.plugins:
        irc.plugins[name] = {"urls":{}}
    irc.plugins[name]["urls"].update(plugin_sources)

def check(irc):
    for get_plugin in irc.plugins[name]["urls"]:
        soup = bs4.BeautifulSoup(requests.get(get_plugin).text)
        soup = [x.get('href') for x in soup.find_all('a') if x.get('href').endswith(".py")]
        for plugin_url in soup:
            plugin_name = plugin_url.split('/')[-1]
            find_url = "http://raw.githubusercontent.com" + plugin_url.replace("blob/", "")
            irc.plugins[name]["urls"][get_plugin][plugin_name] = find_url
    print (plugin_sources)
    return plugin_sources

@add_cmd
def updates(irc, event, args):
    """takes no arguments

    Checks for plugins that can be updated.
    """
    plugin_sources = check(irc)
    updates = []
    if utils.is_owner(irc, event.source):
        for plugin_source_url in irc.plugins[name]["urls"]:
            for plugin_name in irc.plugins[name]["urls"][plugin_source_url]:
                for active_plugin in os.listdir("plugins"):
                    if active_plugin == plugin_name:
                        with open("plugins/" + active_plugin, "r") as deltax:
                            if deltax.read() != requests.get(irc.plugins[name]["urls"][plugin_source_url][plugin_name]).text:
                                updates.append(active_plugin.replace(".py", ""))
                            deltax.close()
        if updates:
            irc.reply(event, "The following plugin(s) can be updated: {}".format(" ".join(updates)))
        else:
            irc.reply(event, "No plugins can be updated")

@add_cmd
def available(irc, event, args):
    """takes no arguments

    Checks for new plugins that can be installed.
    """
    available_plugins = []
    plugin_sources = check(irc)
    if utils.is_owner(irc, event.source):
        for plugin_source_url in irc.plugins[name]["urls"]:
            for plugin in irc.plugins[name]["urls"][plugin_source_url]:
                if plugin not in os.listdir("plugins"):
                    available_plugins.append(plugin.replace("plugins/","").replace(".py", ""))
        if available_plugins:
            irc.reply(event, "The following plugin(s) can be installed: {}".format(" | ".join(available_plugins)))
        else:
            irc.reply(event, "You have all the plugins installed given the {} urls in this plugin: plugins.py".format(len(irc.plugins[name]["urls"])))

@add_cmd
def update(irc, event, args):
    """<plugin>

    Updates <plugin> if an update is available.
    """
    plugin_sources = check(irc)
    success = False
    if utils.is_owner(irc, event.source):
        try:
            if args[0] + ".py" in os.listdir("plugins"):
                for plugin_source_url in irc.plugins[name]["urls"]:
                    for plugin_name in irc.plugins[name]["urls"][plugin_source_url]:
                        if args[0] + ".py" == plugin_name:
                            with open("plugins/" + args[0] + ".py", "r") as plugin_to_read:
                                try:
                                    deltax = requests.get(irc.plugins[name]["urls"][plugin_source_url][plugin_name]).text
                                except:
                                    irc.reply(event, "The plugin couldn't be found online")
                                if plugin_to_read.read() != deltax:
                                    plugin_to_read.close()
                                    with open("plugins/" + args[0] + ".py", "w") as plugin_to_write:
                                        irc.reply(event, "Updating plugin: {}".format(args[0]))
                                        plugin_to_write.write(deltax)
                                        plugin_to_write.close()
                                        success = True
                                        irc.reply(event, "Plugin updated successfully")
                                else:
                                    irc.reply(event, "That plugin is at its latest version")

            elif args[0] + ".py" not in os.listdir("plugins"):
                irc.reply(event, "That plugin isn't installed")

            if not success:
                irc.reply(event, "That plugin couldn't be installed")

        except KeyError:
            pass

@add_cmd
def install(irc, event, args):
    """<plugin>

    Installs <plugin> if plugin is found online and is not already installed
    """
    plugin_sources = check(irc)
    success = False
    if utils.is_owner(irc, event.source):
        try:
            if args[0] + ".py" not in os.listdir("plugins"):
                for plugin_source_url in irc.plugins[name]["urls"]:
                    for plugin_name in irc.plugins[name]["urls"][plugin_source_url]:
                        if args[0] + ".py" == plugin_name:
                            try:
                                deltax = requests.get(irc.plugins[name]["urls"][plugin_source_url][plugin_name]).text
                                with open("plugins/" + args[0] + ".py", "w") as plugin_to_write:
                                    irc.reply(event, "Installing plugin: {}".format(args[0]))
                                    plugin_to_write.write(deltax)
                                    plugin_to_write.close()
                                    success = True
                                    irc.reply(event, "Plugin successfully installed")
                            except:
                                irc.reply(event, "The plugin couldn't be found online")
            elif args[0] + ".py" in os.listdir("plugins"):
                irc.reply(event, "That plugin is already installed")

        except KeyError:
            pass

@add_cmd
def uninstall(irc, event, args, utils = utils):
    plugin_sources = check(irc)
    if utils.is_owner(irc, event.source):
        try:
            if utils.is_allowed(irc, event.source, event.target):
                for plugin_source_url in irc.plugins[name]["urls"]:
                    for plugin in irc.plugins[name]["urls"][plugin_source_url]:
                        if plugin in os.listdir("plugins") and args[0] == plugin.replace(".py", ""):
                            try:
                                irc.reply(event, "Uninstalling plugin")
                                os.remove("plugins/" + plugin)
                                irc.reply(event, "Plugin successfully uninstalled")
                            except:
                                irc.reply(event, "That plugin cannot be uninstalled")
                        elif plugin not in os.listdir("plugins") and args[0] == plugin.replace(".py", ""):
                            irc.reply(event, "That plugin isn't installed")
            else:
                pass
        except KeyError:
            pass
