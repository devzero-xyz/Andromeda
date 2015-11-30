from __future__ import print_function
from time import sleep
import socket
from random import *

modules = {
    } #Module = True/imported

stats = {
    "BWBellairs[Bot]": "1",
    "BWBellairs": "1",
    }

def connectAndIdentify():

    server = "chat.freenode.net"
    port = 6667
    channels = ["##BWBellairs", "##powder-bots", "#botters-test"]
    botnick = "BWBellairs[Bot]"
    realname = "BWBellairs[Bot]"
    ident = "BWBellairs[Bot]"
    password = raw_input("Enter password")
    username = "BWBellairs[Bot]"
    command = "$None$"
    nickname = "BWBellairs[Bot]"

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

    command = "$None%"

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

        if message and message[0].startswith("*"):
            command = " ".join(message).split()
            command[0] = command[0].replace("*", "")
            print("cmd", command)
    
def ircSend(type, chan = None, nickname = None, *args):
    try:
        if type == "PR":
            irc.send("PRIVMSG {0} :{1} {2}\r\n".format(chan, nickname or args, args or "").encode("UTF-8"))

        elif type == "QUIT":
            irc.send("QUIT {0} :{1}\r\n".format(chan or channels[randint(0,(len(channels))- 1)], nickname, args or "GoodBye").encode("UTF-8"))
    except:
        pass

#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

ircSend("QUIT") #In case of the bot being reloaded
connectAndIdentify()

while True:
    recieve()

    try:
        if stats[nickname] == "0" or stats[nickname] == "1":
            if command[0] == "moo":
                irc.send("PRIVMSG {0} :{1}, Mooooo!\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "echo":
                irc.send("PRIVMSG {0} :{1}\r\n".format(chan, " ".join(command[1:])).encode("UTF-8"))

            elif command[0] == "calc":
                try:

                    result = 0

                    if command[2] == "+":
                        result = str(float(command[1]) + float(command[3]))

                    if command[2] == "-":
                        result = str(float(command[1]) - float(command[3]))

                    if command[2] == "/":
                        result = str(float(command[1]) / float(command[3]))
                            
                    if command[2] == "*":
                        result = str(float(command[1]) * float(command[3]))

                    if result.endswith('.0'):
                        result = result[:-2]

                    if result == "":
                        result = 0

                    irc.send("PRIVMSG {0} :{1}, {2}\r\n".format(chan, nickname, result).encode("UTF-8")) 

                except:
                    irc.send("PRIVMSG {0} :{1}, INVALID: arguments. USAGE: *calc <var> <operator> <var>\r\n".format(chan, nickname).encode("UTF-8"))    
            
        if stats[nickname] == "1":
            if command[0] == "join":
                irc.send("JOIN {0}\r\n".format(command[1]).encode("UTF-8"))

            elif command[0] == "leave":
                irc.send("PART {0}\r\n".format(command[1]).encode("UTF-8"))

            elif command[0] == "quit":        
                ircSend("QUIT", None, None, "")
                import sys; sys.exit() 

            elif command[0] == "permissions" and command[2] == "=":
                try:
                    if command[3] == "1" or command[3] == "0":
                        stats[command[1]] = command[3]
                        irc.send("PRIVMSG {0} :{1}, {2} permissions lvl set to {3}\r\n".format(chan, nickname, command[1], command[3]).encode("UTF-8"))
                    else:
                        irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *permissions = 0/1\r\n".format(chan, nickname).encode("UTF-8"))
                except:
                    irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *permissions = 0/1/\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "kick":
                if command[1]:
                    irc.send("KICK {0} {1} :{2}\r\n".format(chan, command[1], " ".join(command[2:]) or command[1]).encode("UTF-8"))

                else:
                    irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *kick <nickname> [reason]\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "op":
                if not command[1]:
                    irc.send("MODE {0} +o {1} :\r\n".format(chan, nickname).encode("UTF-8"))

                elif command[1]:
                    irc.send("MODE {0} +o {1} :\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "deop":
                if not command[1]:
                    irc.send("MODE {0} -o {1} :\r\n".format(chan, nickname).encode("UTF-8"))

                elif command[1]:
                    irc.send("MODE {0} -o {1} :\r\n".format(chan, command[1] or nickname).encode("UTF-8"))

    except:
        pass
#=========================================================================================#
#=========================================================================================#
#=========================================================================================#
