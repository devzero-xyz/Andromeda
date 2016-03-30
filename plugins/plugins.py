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
cmds = ["available", "updates"] # Install <plugin>, uninstall <plugin> <<< TODO

updates = [] # Stores available updates
update_refresh_rate = 300 # Seconds | Recommended for minimal RAM use (300) 5 mins
installed_plugins = os.listdir("plugins")
active_plugins = [plugin.replace(".py", "") for plugin in utils.plugins.keys()]

def check():
    while True:
        sleep(update_refresh_rate) # Delay between checking for new updates/plugins
        for get_plugin in plugin_sources:
            plugin_page = [x + ".py" for x in re.findall('plugins/(.*?).py',requests.get(get_plugin).text)]
            for plugin_name in plugin_page:
                find_url = get_plugin.replace("github", "raw.githubusercontent").replace("/tree", "") + "/" + plugin_name
                plugin_sources[get_plugin][plugin_name] = find_url

update_thread = Thread(target=check)
update_thread.setDaemon(True)
update_thread.start()

@add_cmd
def updates(irc, event, args):
    for plugin_source_url in plugin_sources:
        for plugin in plugin_sources[plugin_source_url]:
            for active_plugin in active_plugins:
                if active_plugin + ".py" == plugin:
                    with open("plugins/" + active_plugin + ".py", "r") as deltax:
                        if deltax.read() != requests.get(plugin_sources[plugin_source_url][plugin]).text:
                            updates.append(plugin)
                        deltax.close()
    if updates:
        irc.reply(event, "The follwing plugin(s) can be updated: {}".format(" ".join(updates)))
    else:
        irc.reply(event, "No plugins can be updated")
 
@add_cmd       
def available(irc, event, args):
    available_plugins = []
    for plugin_source_url in plugin_sources:
        for plugin in plugin_sources[plugin_source_url]:
            if plugin + ".py" not in active_plugins:
                available_plugins.append(plugin)
    if available_plugins:
        irc.reply(event, "The follwing plugin(s) can be installed: {}".format(" ".join(available_plugins)))
    else:
        irc.reply(event, "You have all the plugins installed given the {} urls in this plugin: plugins.py".format(len(plugin_sources)))

@add_cmd
def install(irc, event, args):
    success = False
    try:
        if args[0] + ".py" not in os.listdir("plugins"):
            for plugin_source_url in plugin_sources:
                for plugin in plugin_sources[plugin_source_url]:
                    if args[0] == plugin:
                        irc.reply(event, "That plugin is already installed")
                    else:
                        with open(args[0] + ".py", "w+") as write_plugin:
                            write_plugin.write(requests.get(plugin_sources[plugin_source_url][plugin]).text)
                            write_plugin.close()
                            irc.reply("The plugin {0} is now installed as {0}.py in plugins".format(args[0]))
                            success = True
        
        elif args[0] + ".py" in os.listdir("plugins"):
            irc.reply(event, "That plugin is already installed")
        if not success:
            irc.reply(event, "That plugin is not in the {} urls you have supplied in plugins.py in plugins".format(len(plugin_sources)))
    except KeyError:
        pass
