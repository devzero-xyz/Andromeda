from __future__ import print_function
from base64 import b64encode
from time import sleep, time
import socket
import ssl
from random import *

startTime = time()
messagesSeen = 0
commandCharacter = "*"
botnick = "BWBellairs[Bot]"

def setupCommands(char = commandCharacter):
    global userCommands, adminCommands, ownerCommands, commandCharacter

    commandCharacter = char

    userCommands = {
            "status": commandCharacter + "status | Displays infomation :P",
            "perm level": commandCharacter + "perm level | Displays the users permissions level",
            botnick + " char": botnick + ", char | returns the current command character",
            "moo": commandCharacter + "moo | prints 'moo' [PONG]",
            "time": commandCharacter + "time | Displays system time",
            "echo": commandCharacter + "echo [+<colour>] +i|Italic +u|Underline +b|Bold [text]",
            "bug": commandCharacter + "bug <text> | reports a bug to the owner of the bot",
            "list admins": commandCharacter + "list admins | Displays a list of current admins",
            "calc": commandCharacter + "calc int/float/other */-/+/% int/float/other returns MATHS",
            "list channels": commandCharacter + "lists channels | List the channels the bot is in",
            }
    adminCommands = {
            "join": commandCharacter + "join <chan> | Makes the bot join the specified channel",
            "leave": commandCharacter + "leave <chan> | Makes the bot leave the specified channel",
            "permissions": commandCharacter + "permissions <user> = <lvl> | Sets perms flags to the user specified",
            "kick": commandCharacter + "kick <user> | kicks the user from the current channel",
            "op": commandCharacter + "op <user> | ops the user on the current channel",
            "deop": commandCharacter + "deop <user> | deops the user on the current channel",
            "sop": commandCharacter + "sop | ops the bot via services",
            "sdeop": commandCharacter + "sdeop | deops the bot via services",
            "ban": commandCharacter + "ban <user> | bans the user from the current channel",
            "unban": commandCharacter + "unban <user> | unbans the user from the current channel",
            "kban": commandCharacter + "kban <user> | bans then kicks the user from the current channel",
            "action": commandCharacter + "action [text] | for third person messages | Bot moo's",
            "voice": commandCharacter + "voice <user> | voices the user in the channel",
            "devoice": commandCharacter + "devoice <user> | devoices the user in the channel",
            "quiet": commandCharacter + "quiet <user> | quiets the user in the current channel",
            "unquiet": commandCharacter + "unquiet <user> | unquiets the user in the current channel",
            }

    ownerCommands = {
        "r": commandCharacter + "r | Restarts the bot",
        "quit": commandCharacter + "quit [Message] | makes the bot quit irc displaying the message specified or '[nick] told me to'",
        "commandChar": commandCharacter + "commandChar | changes the bot's command character",
        }

    return
    
setupCommands()

modules = {
    "last": True,
    } #Module = True/imported

channelLinks = {
    }

bans = {
    }

startup = False

stats = {
    }
def perms(write = False):
    global stats

    if write == False:
        with open("admins.txt", "r+") as perms1:
            for i in perms1.read().replace(" ", "").split():
                stats[i] = "1"
            perms1.close()

        with open("owners.txt", "r+") as perms1:
            for i in perms1.read().replace(" ", "").split():
                stats[i] = "2"
            perms1.close()

    if write == True:
        with open("admins.txt", "w") as perms2:
            for i in stats:
                perms2.write(i + "\n")
            perms2.close()

    if write == True:
        with open("owners.txt", "w") as perms2:
            for i in stats:
                if stats[i] == "2":
                    perms2.write(i + "\n")
            perms2.close()

perms()

def connectAndIdentify(botnick = botnick):

    global irc, channels

    with open("password.txt", "r+") as passwordFile:
        password = passwordFile.readline()
        passwordFile.close()

    server = "chat.freenode.net"
    port = 6697
    channels = ["##BWBellairs", "##powder-bots", "#botters-test", "##BWBellairs-bots", "#U_U"]
    botnick = "BWBellairs[Bot]"
    realname = "BWBellairs[Bot]"
    ident = "BWBellairs[Bot]"
    use_ssl = True
    use_sasl = True
    username = "BWBellairs[Bot]"
    command = "$None$"

    irc = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # defines the socket
    if use_ssl:
        irc = ssl.wrap_socket(sock)
    else:
        irc = sock

    print("connecting to: " + server)
    irc.connect((server, port))  # connects to the server

    if use_sasl:
        saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                	username, password).encode("UTF-8")) 
        irc.send("CAP REQ :sasl\r\n".format("UTF-8"))
        irc.send("USER {0} {1} blah :{2}\r\n".format(
                ident, botnick, realname).encode("UTF-8"))
        irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))
        irc.send("AUTHENTICATE PLAIN\r\n".encode("UTF-8"))
        irc.send("AUTHENTICATE {0}\r\n".format(saslstring).encode(
                "UTF-8"))
        authed = confirmsasl()
        if authed:
            irc.send("CAP END\r\n".encode("UTF-8"))
        else:
            print("SASL aborted. exiting.")
            irc.send("QUIT\r\n")
            irc.shutdown(2)
            exit()
    else:
        irc.send("USER {0} {1} blah :{2}\r\n".format(
                ident, botnick, realname).encode("UTF-8"))  # user authentication
        irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))  # sets nick
        irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                username, password).encode("UTF-8"))  # auth

    irc.send("JOIN {0}\r\n".format(",".join(channels)).encode("UTF-8"))  # join the channel(s)

def confirmsasl():
    while True:
        ircmsg = irc.recv(2048)
        ircmsg = ircmsg.split()
        print(ircmsg)
        ircmsg = " ".join(ircmsg)
        success = ":SASL authentication successful"
        failure = ":SASL authentication aborted"
        if success in ircmsg: 
                return True
        elif failure in ircmsg:
                return False

def recieve(commandNone = False):

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

    if commandNone == False:
        command = "$None%"

    if t[0] == "PING":
        # Respond with PONG
        irc.send("PONG\r\n".encode("UTF-8"))

    elif "!" in t[0]:
        nickname = t[0].split("!")[0]
        nickname = nickname.replace(":", "")
        hostmask = t[0]
        msg_type = t[1]
        if len(t) >= 2:
            if t[2] and t[2].startswith("#"):
                chan = t[2]
            else:
                chan = nickname

            message = t[3:]

        if message and message[0].startswith(commandCharacter):
            command = " ".join(message).split()
            command[0] = command[0].replace(commandCharacter, "")
            print("cmd", command)
    
def ircSend(typeM, chan = None, nickname = None, *args):
    try:
        if typeM == "PR":
            irc.send("PRIVMSG {0} :{1} {2}\r\n".format(chan, nickname or args, args or "").encode("UTF-8"))

        elif typeM == "QUIT":
            irc.send("QUIT {0} :{1}\r\n".format(chan, nickname, args or "GoodBye").encode("UTF-8"))

        elif typeM == "topic":
            pass
    except:
        pass

def channelLink(cmd = None, channelA = None, channelB = None):
    if cmd == "add":
        try:
            channelLinks[channelA] = channelB
            irc.send("PRIVMSG {0} :Channels [{0}] and {1} successfully linked\r\n".format(i, channelLinks[i], nickname, message).encode("UTF-8"))

        except:
            irc.send("PRIVMSG {0} :Channels [{0}] and [{1}] have failed to link\r\n".format(i, channelLinks[i], nickname, message).encode("UTF-8"))

    elif cmd == "remove":
        try:
            del channelLinks[channelA]
            irc.send("PRIVMSG {0} :Channels [{0}] and [{1}] successfully are now unlinked\r\n".format(i, channelLinks[i], nickname, message).encode("UTF-8"))
        except:
            irc.send("PRIVMSG {0} :Channels [{0}] and [{1}] have failed to unlink\r\n".format(i, channelLinks[i], nickname, message).encode("UTF-8"))

    else:
        for i in channelLinks:
            if i == chan:
                irc.send("PRIVMSG {0} :[{1}] {2}: {3}\r\n".format(channelLinks[i], i, nickname, " ".join(message)).encode("UTF-8"))
            elif channelLinks[i] == chan:
                irc.send("PRIVMSG {0} :[{1}] {2}: {3}\r\n".format(i, channelLinks[i], nickname, " ".join(message)).encode("UTF-8"))

def last(nickname = None, cmd = False):
    nicks = {}

    if cmd == "help":
        irc.send("PRIVMSG {0} :{1} Sends a memo to the nickname containg msgs sent by other nicks highlighting them. This will be sent when the user types *last send\r\n".format(chan, nickname).encode("UTF-8"))

    if cmd == "add":
        nicks[nickname] == []

    if cmd == "send":
        irc.send("MemoServ SEND :{0} {1}\r\n".format(nickname, nicks[nickname]).encode("UTF-8"))

    if cmd == "refresh":
        for i in nicks:
            if i in message:
                nicks[i].append[message] + " "

#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

ircSend("QUIT") #In case of the bot being reloaded
connectAndIdentify()

while True:
    recieve()
    channelLink()
    last(None, "refresh")

    try:
        if t[3] == botnick + "," and t[4] == "char" or t[3] == botnick + ":" and t[4] == "char":
            irc.send("PRIVMSG {0} :{1}, My current command character is: {2}\r\n".format(chan, nickname, commandCharacter).encode("UTF-8"))            
    
        if t[1] == "KICK" and t[3] == "BWBellairs[Bot]":
            irc.send("JOIN {0}\r\n".format(t[2]).encode("UTF-8"))
    except:
        pass
    
    try:
        if command[0]:

            if command[0] == "commands":
                if stats[nickname] == "1":
                    irc.send("PRIVMSG {0} :{1}, Commands available for you are: {2} {3}\r\n".format(chan, nickname, ", ".join(userCommands), ", ".join(adminCommands)).encode("UTF-8"))

                elif stats[nickname] == "2":
                    irc.send("PRIVMSG {0} :{1}, Commands available for you are: {2} {3} {4}\r\n".format(chan, nickname, ", ".join(userCommands), ", ".join(adminCommands), ", ".join(ownerCommands)).encode("UTF-8"))

                elif nickname not in stats:
                    irc.send("PRIVMSG {0} :{1}, Commands available for you are: {2}\r\n".format(chan, nickname, ", ".join(userCommands)).encode("UTF-8"))

            elif command[0] == "status":
                irc.send("PRIVMSG {0} :I have been awake {1} minutes and have seen {2} messages.\r\n".format(chan, (int(time()) - int(startTime)) / 60, messagesSeen).encode("UTF-8"))
                

            elif command[0] == "perm" and  command[1] == "level":
                if nickname in stats:
                    irc.send("PRIVMSG {0} :{1} your permissions lvl is: {2}\r\n".format(chan, nickname, stats[nickname]).encode("UTF-8"))

                else:
                    irc.send("PRIVMSG {0} :{1} your permissions lvl is: 0\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "list" and command[1] == "channels":
                irc.send("PRIVMSG {0} :Channel(s) I'm in: {1}\r\n".format(nickname, ", ".join(channels)).encode("UTF-8"))

            elif command[0] == "help":
                if len(command) == 1:
                    irc.send("PRIVMSG {0} :{1}, try {2}commands for a command listing\r\n".format(chan, nickname, commandCharacter).encode("UTF-8"))

                elif command[1] in userCommands:
                    irc.send("PRIVMSG {0} :{1}, Help on this command: {2}\r\n".format(chan, nickname, userCommands[" ".join(command[1:])]).encode("UTF-8"))
                elif command[1] in adminCommands:
                    irc.send("PRIVMSG {0} :{1}, Help on this command: {2}\r\n".format(chan, nickname, adminCommands[" ".join(command[1:])]).encode("UTF-8"))
                elif command[1] in ownerCommands:
                    irc.send("PRIVMSG {0} :{1}, Help on this command: {2}\r\n".format(chan, nickname, ownerCommands[" ".join(command[1:])]).encode("UTF-8"))

                    
            elif command[0] == "moo":
                irc.send("PRIVMSG {0} :{1}, Mooooo!\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "last":
                last(nickname, command[1])

            if command[0] == "time":
                irc.send("PRIVMSG {0} :{1}, {2}\r\n".format(chan, nickname, time()).encode("UTF-8"))

            elif command[0] == "echo":
                irc.send("PRIVMSG {0} :\017{1}\r\n".format(chan, " ".join(command[1:]).replace("+i ", "").replace("+b ", "").replace("+u ", "").replace("+yellow ", "08").replace("+purple ", "06").replace("+orange ", "07").replace("+reset ", "").replace("+gray ", "00").replace("+black ", "01").replace("+blue ", "02").replace("+green " , "03").replace("+red ", "04").replace("+brown ", "05").encode("UTF-8")))

            elif command[0] == "bug":
                if len(command) >= 2:
                    bugs = open("Bugs.txt", "a")
                    bugs.write(nickname + " :" + " ".join(command[1:]) + "\n")
                    irc.send("PRIVMSG {0} :{1}, Bug has been reported\r\n".format(chan, nickname).encode("UTF-8"))
                    bugs.close()
                else:
                    irc.send("PRIVMSG {0} :{1}, No bug to report\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "list" and command[1] == "admins":
                irc.send("PRIVMSG {0} :Bot admins are: {1}\r\n".format(nickname, " ".join(stats)).encode("UTF-8"))

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
            
        if stats[nickname] == "1" or stats[nickname] == "2":
            if command[0] == "join" and command[1]:
                irc.send("JOIN {0}\r\n".format(command[1]).encode("UTF-8"))
                channels = channels.append(command[1])

            elif command[0] == "commandChar":
                if commandCharacter == command[1]:
                    irc.send("PRIVMSG {0} :{1}, That command character is already in use!\r\n".format(chan, nickname).encode("UTF-8"))
                else:
                    irc.send("PRIVMSG {0} :My command character has been changed to: {1}\r\n".format(", ".join(channels), commandCharacter).encode("UTF-8"))
                    setupCommands(command[1])
                
            elif command[0] == "leave" and command[1]:
                irc.send("PART {0}\r\n".format(command[1]).encode("UTF-8"))
                channels = channels.remove(command[1])

            elif command[0] == "kick":
                if command[1]:
                    irc.send("KICK {0} {1} :{2}\r\n".format(chan, command[1], " ".join(command[2:]) or command[1]).encode("UTF-8"))

                else:
                    irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *kick <nickname> [reason]\r\n".format(chan, nickname).encode("UTF-8"))

            elif command[0] == "op":
                if len(command) == 1:
                    irc.send("MODE {0} +o {1}\r\n".format(chan, nickname).encode("UTF-8"))

                else:
                    irc.send("MODE {0} +o {1}\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "deop":
                if len(command) == 1:
                    irc.send("MODE {0} -o {1}\r\n".format(chan, nickname).encode("UTF-8"))

                else:
                    irc.send("MODE {0} -o {1}\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "sop":
                if len(command) == 1:
                    irc.send("PRIVMSG ChanServ :OP {0}\r\n".format(chan).encode("UTF-8"))

                else:
                    irc.send("PRIVMSG ChanServ :OP {0} {1}\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "sdeop":
                if len(command) == 1:
                    irc.send("PRIVMSG ChanServ :DEOP {0}\r\n".format(chan).encode("UTF-8"))

                else:
                    irc.send("PRIVMSG ChanServ :DEOP {0} {1}\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "ban":
                irc.send("WHO {0}\r\n".format(command[1]).encode("UTF-8"))
                recieve(True)
                irc.send("MODE {0} +b {1}\r\n".format(chan, t[5]).encode("UTF-8"))
                bans[command[1]] = t[5]

            elif command[0] == "unban":
                try:
                    irc.send("MODE {0} -b {1}\r\n".format(chan, bans[command[1]]).encode("UTF-8"))
                    del bans[command[1]]
                except:
                    pass

            elif command[0] == "kban":
                irc.send("WHO {0}\r\n".format(command[1]).encode("UTF-8"))
                recieve(True)
                irc.send("MODE {0} +b {1}\r\n".format(chan, t[5]).encode("UTF-8"))
                irc.send("KICK {0} {1} :{2}\r\n".format(chan, t[7], " ".join(command[2:]) or "Kicked/moo", nickname).encode("UTF-8"))
                bans[command[1]] = t[5]

            elif command[0] == "channel" and command[1] == "links":
                channelLink(command[2], command[3], command[4])

            elif command[0] == "action":
                irc.send("PRIVMSG {0} :\x01ACTION {1}\x01\r\n".format(chan, " ".join(command[1:])).encode("UTF-8"))

            elif command[0] == "voice":
                irc.send("MODE {0} +v {1}\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "devoice":
                irc.send("MODE {0} -v {1}\r\n".format(chan, command[1]).encode("UTF-8"))

            elif command[0] == "quiet":
                irc.send("WHO {0}\r\n".format(command[1]).encode("UTF-8"))
                recieve(True)
                irc.send("MODE {0} +q {1}\r\n".format(chan, t[5]).encode("UTF-8"))

            elif command[0] == "unquiet":
                irc.send("WHO {0}\r\n".format(command[1]).encode("UTF-8"))
                recieve(True)
                irc.send("MODE {0} +q {1}\r\n".format(chan, t[5]).encode("UTF-8"))

        if stats[nickname] == "2":
            if command[0] == "quit":
                perms(True)
                if len(command) > 1:
                    irc.send("QUIT :{0}\r\n".format(" ".join(command[1:])).encode("UTF-8"))

                else:
                    irc.send("QUIT :{0}\r\n".format(nickname + " told me to").encode("UTF-8"))

                quit()
            
            elif command[0] == "r":
                perms(True)
                irc.send("QUIT :Restarting\r\n".encode("UTF-8"))
                startfile("main.py")
                quit()
                
            elif command[0] == "permissions" and command[2] == "=":
                try:
                    if command[3] == "1" or command[3] == "0" or command[3] == "2":
                        if command[3] == "0":
                            del stats[command[1]]
                        elif command[3] == "1" or command[3] == "2":
                            stats[command[1]] = command[3]
                        irc.send("PRIVMSG {0} :{1}, {2} permissions lvl set to {3}\r\n".format(chan, nickname, command[1], command[3]).encode("UTF-8"))
                    else:
                        irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *permissions = 0/1\r\n".format(chan, nickname).encode("UTF-8"))
                except:
                    irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *permissions = 0/1\r\n".format(chan, nickname).encode("UTF-8"))

    except:
        pass

    messagesSeen += 1

#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

