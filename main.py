from __future__ import print_function
from time import sleep
from socketS import *
from commandRun import *

#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

connectAndIdentify()

while True:
    recieve()
    
    if returndata()[6] and returndata()[6].startswith("*") and command != None:
        command(returndata()[6])
        command == None

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
