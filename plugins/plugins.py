from threading import Thread
from utils import add_cmd
from time import sleep
import re
import utils
import os
import requests

plugin_sources = {
    "https://github.com/devzero-xyz/Andromeda/tree/master/plugins": {}, # wil contain plugin names and raw url
    "https://github.com/devzero-xyz/Andromeda-Plugins": {},
}

name = "plugins"
cmds = ["update", "available", "updates"] # Install <plugin>, uninstall <plugin> <<< TODO

update_refresh_rate = 5 # Seconds | Recommended for minimal RAM use (300) 5 mins
installed_plugins = os.listdir("plugins")
active_plugins = [plugin.replace(".py", "") for plugin in utils.plugins.keys()]

def check():
    for get_plugin in plugin_sources:
        plugin_page = [x + ".py" for x in re.findall('plugins/(.*?).py',requests.get(get_plugin).text)]
        for plugin_name in plugin_page:
            find_url = get_plugin.replace("github", "raw.githubusercontent").replace("/tree", "") + "/" + plugin_name
            plugin_sources[get_plugin][plugin_name.replace("plugins/", "")] = find_url
    print (plugin_sources)
    return plugin_sources
#update_thread = Thread(target=check)
#update_thread.setDaemon(True)
#update_thread.start()

@add_cmd
def updates(irc, event, args):
    """takes no arguments

    Checks for plugins that can be updated.
    """
    #irc.reply(event, check())
    plugin_sources = check()
    updates = []
    #irc.reply(event, plugin_sources)
    for plugin_source_url in plugin_sources:
        for plugin_name in plugin_sources[plugin_source_url]:
            for active_plugin in os.listdir("plugins"):
                if active_plugin == plugin_name:
                    with open("plugins/" + active_plugin, "r") as deltax:
                        if deltax.read() != requests.get(plugin_sources[plugin_source_url][plugin_name]).text:
                            updates.append(active_plugin.replace(".py", ""))
                        deltax.close()
    if updates:
        irc.reply(event, "The follwing plugin(s) can be updated: {}".format(" ".join(updates)))
    else:
        irc.reply(event, "No plugins can be updated")
 
@add_cmd       
def available(irc, event, args):
    """takes no arguments

    Checks for new plugins that can be installed.
    """
    available_plugins = []
    plugin_sources = check()
    for plugin_source_url in plugin_sources:
        for plugin in plugin_sources[plugin_source_url]:
            if plugin not in os.listdir("plugins"):
                available_plugins.append(plugin.replace("plugins/",""))
    if available_plugins:
        irc.reply(event, "The follwing plugin(s) can be installed: {}".format(" ".join(available_plugins)))
    else:
        irc.reply(event, "You have all the plugins installed given the {} urls in this plugin: plugins.py".format(len(plugin_sources)))

@add_cmd
def update(irc, event, args):
    """<plugin>

    Updates <plugin> if an update is available.
    """
    plugin_sources = check()
    success = False
    try:
        if args[0] + ".py" in os.listdir("plugins"):
            for plugin_source_url in plugin_sources:
                for plugin_name in plugin_sources[plugin_source_url]:
                    if args[0] + ".py" == plugin_name:
                        success = True
                        with open("plugins/" + args[0] + ".py", "w+") as plugin_to_update:
                            try:
                                deltax = requests.get(plugin_sources[plugin_source_url][plugin_name]).text
                            
                            except:
                                irc.reply(event, "The plugin couldn't be found online")
                            if plugin_to_update.read() != deltax:
                                irc.reply(event, "Updating plugin: {}".format(args[0]))
                                plugin_to_update.write(deltax)
                                plugin_to_update.close()
                                irc.reply(event, "Plugin updated successfully")
                            else:
                                irc.reply(event, "That plugin is at its latest version")
            
        elif args[0] + ".py" not in os.listdir("plugins"):
            irc.reply(event, "That plugin isn't installed")
        
        if not success:
            irc.reply("That plugin couldn't be installed")
        
    except KeyError:
        pass
