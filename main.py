from __future__ import print_function
from time import sleep
from socketS import *
from commandRun import *
modules = ["socketS", "commandRun", "yo"]

print ("yes")

for i in module:
    try:
        exec("exec("+ i + ")")
    except:
        print ("Module doesn't exist")
#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

connectAndIdentify()

while True:
    recieve()
    
    if command == "*moo":
        irc.send("PRIVMSG {0} :{1}, Mooooo!\r\n".format(chan, nickname).encode("UTF-8"))

    elif command == "*r":
        ircSend("QUIT")
        connectAndIdentify()
        command = None

    elif command == "*m":
        irc.send("PRIVMSG {0} :test\r\n".format(chan).encode("UTF-8"))

    elif command == "*whackme":
        gamewhackAMole(nickname)
        ircSend("PRIVMSG", chan, nickname)

    elif command == "*reload":        
        ircSend("QUIT")

    elif command == "*echo":
        ircSend("PR", chan, nick)

    try:
      print("next")
    except UnicodeEncodeError:
      pass




    
    
#=========================================================================================#
#=========================================================================================#
#=========================================================================================#
