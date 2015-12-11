from __future__ import print_function
import mPluginImporter

mPluginImporter.importModules()
importantModules = {
    "irc ircRelay": True,
    } #Module = True/imported
plugins = {
    }
importQueue = [plugins, importantModules]
def importModules():
    for module in importQueue:
            for i in module:
                if len(i) >= 2:
                    moduleInfo = i.split()
                    moduleLocation = moduleInfo[0]
                    moduleForImport = moduleInfo[1]

                    try:
                        exec("from " + moduleLocation + " import " + moduleForImport)
                        print("Module " + moduleForImport + " from "  + moduleLocation + " has been imported")

                    except:
                        print("Module " + moduleForImport + " from " + moduleLocation + " could not be imported")

                else:
                    try:
                        exec("import " + i)
                        print("Module " + moduleForImport + " has been imported")

                    except:
                        print("Module " + moduleForImport + " could not be imported")

ircRelay.ircSend("QUIT") #In case of the bot being reloaded
ircRelay.connectAndIdentify()
irc = ircRelay.irc

while True:
    t = ircRelay.recieve()
 
            

