from main import *

def commandS(command, chan, args, nickname, modules):

    if command == "*moo":
        irc.send("PRIVMSG {0} :{1}, Mooooo!\r\n".format(chan, nickname).encode("UTF-8"))

    elif command == "*r":
        ircSend("QUIT")
        connectAndIdentify()
        command = None

    elif command == "*m":
        irc.send("PRIVMSG {0} :test\r\n".format(chan).encode("UTF-8"))

    elif command == "*quit":        
        ircSend("QUIT", None, None, "I know i am... *cries*")

    elif command == "*list modules":
        for i in modules:
            if modules[i] == True:
                listM += i
        
        ircSend("PR", chan, nickname, listM)

def ok():
    pass
