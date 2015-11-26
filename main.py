from __future__ import print_function
from time import sleep
from commandRun import *
import socket
import sys
from random import *

modules = {
    "commandRun": False, #True = imported
    "botCommands": False,
    }

for i in modules:
    try:
        exec("from " + i + " import *", None)
        modules[i] = True
        print ("module", i, "imported")
    except:
        print ("module not installed")
        modules[i] = False

print (modules)

server = "chat.freenode.net"
port = 6667
channels = ["##BWBellairs", "##powder-bots", "#botters-test"]
botnick = "BWBellairs[Bot]"
realname = "BWBellairs[Bot]"
ident = "BWBellairs[Bot]"
password = "[REDACTED]]"
username = "BWBellairs[Bot]"
command = ""

def connectAndIdentify():

    global irc

    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # defines the socket
    print("connecting to: " + server)
    irc.connect((server, port))  # connects to the server
    irc.send("USER {0} {1} blah :{2}\r\n".format(
            ident, botnick, realname).encode("UTF-8"))  # user authentication
    irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))  # sets nick
    irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
            username, password).encode("UTF-8"))  # auth

    irc.send("JOIN {0}\r\n".format(",".join(channels)).encode("UTF-8"))  # join the channel(s)

def recieve():

    global t, nickname, hotmask, msg_type, chan, message, command, args
    
    binary_data = irc.recv(1024)
    # Decode data from UTF-8
    #data = binary_data.decode("UTF-8", "ignore")
    data = binary_data
    # Split data by spaces
    t = data.replace(":", "")#.split()
    t = t.split()
    
    print (t)
    # Listen for PING

    try:
        if t[0] == "PING":
            # Respond with PONG
            irc.send("PONG\r\n".encode("UTF-8"))


        
        elif "!" in t[0]:
            nickname = t[0].split("!")[0] 
            nickname = nickname.replace(":", "")
            hostmask = t[0]
            msg_type = t[1]
            chan = t[2]
            message = t[3:]
            
            
            if message:
                message[0] = message[0][0:]
                command = message[0].lower()
                command = str(command)
                print (command)

            if command:
                args = message[1:]

    except:
        pass
    
def ircSend(type, chan = None, nick = None, *args):
    if type == "PR":
        irc.send("PRIVMSG {0} :{1} {2}\r\n".format(chan, nickname or args, args or "").encode("UTF-8"))

    elif type == "QUIT":
        irc.send("QUIT {0} :{1}\r\n".format(chan or channels[randint(0,(len(channels))- 1)], nick, args or "GoodBye").encode("UTF-8"))

def commandRun(command):
        command = command.replace("*", "")
        #if command.find("print") or command.find("import") or command.find("=") or command.find("if"):
         #   ircSend("PR", nickname, nickname, "Not allowed!")
        #else:
        print ("command", command)
        try:
            exec(command)
        except:
            print ("ERROR")
#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

connectAndIdentify()

while True:
    recieve()
    
    if command:
        commandRun(command)   

    if command == "*moo":
        irc.send("PRIVMSG {0} :{1}, Mooooo!\r\n".format(chan, nickname).encode("UTF-8"))

    elif command == "*r":
        ircSend("QUIT")
        connectAndIdentify()
        command = None

    elif command == "*m":
        irc.send("PRIVMSG {0} :test\r\n".format(chan).encode("UTF-8"))

    elif command == "*ur_stupid":        
        ircSend("QUIT", None, None, "I know i am... *cries*")

    elif command == "*echo":
        ircSend("PR", chan, nickname)

    try:
      print("next")
    except UnicodeEncodeError:
      pass




    
    
#=========================================================================================#
#=========================================================================================#
#=========================================================================================#
