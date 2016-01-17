#!/usr/bin/python3

from __future__ import print_function
from base64 import b64encode
from time import sleep, time
from fnmatch import fnmatch
import socket
import ssl
from random import *
import os
import sys
import threading
import hashlib
import urllib.request

startTime = time()
messagesSeen = 0
commandCharacter = "*"
botnick = "BWBellairs[Bot]"
nickname = "0"

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
            "list channels": commandCharacter + "list channels | List the channels the bot is in",
            "list": commandCharacter + "list | Lists the commands it has :P",
            }
    adminCommands = {
            "join": commandCharacter + "join <chan> | Makes the bot join the specified channel",
            "leave": commandCharacter + "leave <chan> | Makes the bot leave the specified channel",
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
        "permissions": commandCharacter + "permissions <user> = <lvl> | Sets perms flags to the user specified",
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

owners = []

admins = []

ignores = []

def perms(write = False):
    global owners, admins, ignores

    if not write:
        with open("admins.txt", "r+") as perms1:
            perms11 = perms1.read()
            perms11 = perms11.strip(" \n")
            admins = perms11.split("\n")
            perms1.close()

        with open("owners.txt", "r+") as perms1:
            perms11 = perms1.read()
            perms11 = perms11.strip(" \n")
            owners = perms11.split("\n")
            perms1.close()

        with open("ignores.txt", "r+") as perms1:
            perms11 = perms1.read()
            perms11 = perms11.strip(" \n")
            ignores = perms11.split("\n")
            perms1.close()

    if write:
        with open("admins.txt", "w") as perms2:
            for i in admins:
                perms2.write(i + "\n")
            perms2.close()

        with open("owners.txt", "w") as perms2:
            for i in owners:
                perms2.write(i + "\n")
            perms2.close()

        with open("ignores.txt", "w") as perms2:
            for i in ignores:
                perms2.write(i + "\n")
            perms2.close()

perms()

def isOwner(mask):
    for i in owners:
        isowner = fnmatch(mask, i)
        if isowner:
            return True
    return False

def isAdmin(mask):
    isowner = isOwner(mask)
    if isowner:
        return True
    for i in admins:
        isadmin = fnmatch(mask, i)
        if isadmin:
            return True
    return False

def isIgnored(mask):
    for i in ignores:
        isignored = fnmatch(mask, i)
        if isignored:
            return True
    return False

def connectAndIdentify(botnick = botnick):

    global irc, channels

    with open("password.txt", "r+") as passwordFile:
        password = passwordFile.readline()
        password = password.strip(" \n")
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
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)  # defines the socket
    if use_ssl:
        irc = ssl.wrap_socket(sock)
    else:
        irc = sock

    print("connecting to: " + server)
    irc.connect((server, port))  # connects to the server

    if use_sasl:
        saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                        username, password).encode("UTF-8"))
        saslstring = saslstring.decode("UTF-8")
        irc.send("CAP REQ :sasl\r\n".encode("UTF-8"))
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
            irc.send("QUIT\r\n".encode("UTF-8"))
            irc.shutdown(2)
            exit()
    else:
        irc.send("USER {0} {1} blah :{2}\r\n".format(
                ident, botnick, realname).encode("UTF-8"))  # user authentication
        irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))  # sets nick
        irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                username, password).encode("UTF-8"))  # auth

    irc.send("JOIN {0}\r\n".format(",".join(channels)).encode("UTF-8"))  # join the channel(s)

def update():

    while True:
        """
        Downloads new source code for this IRC bot and runs it. Make sure you're 
        sending new code over HTTPS from a trusted vendor. The URL of the source is
        specified inside the relaybox configuration. Also make sure that the config
        you have right now will match the config that the new code supports.
        """
        urllib.request.urlretrieve("https://raw.githubusercontent.com/BWBellairs/BWBellairsBot/master/main.py", 'main[Online].py')
        with open("main.py", "rb") as oldFile:
            data = oldFile.read()
            oldHash = hashlib.md5(data)
            oldHash = oldHash.hexdigest()
            oldFile.close()

        with open("main[Online].py", "rb") as newFile:
            data = newFile.read()
            newHash = hashlib.md5(data)
            newHash = newHash.hexdigest()
            newFile.close()

        print("[Updater] Checking for updates")
        if oldHash != newHash:
            print("[Updater] Updates found")
            print("[Updater] Updating...")
            with open("main.py", "w") as writeToFile:
                with open("main[Online].py", "r") as newFile:
                    writeToFile.write(newFile.read())
                    newFile.close()
                    writeToFile.close()
            for i in channels:
                irc.send("PRIVMSG {0} :[Updater] Update has been found and applied Update URL - [{1}]\r\n".format(i, updateUrl).encode("UTF-8"))
            print("[Updater] Updates completed")
            print("[Updater] Restarting...")
            irc.send("QUIT :Updating\r\n".encode("UTF-8"))
            os.execv(sys.executable, [sys.executable] + sys.argv)
        sleep(10)

updateCall = threading.Thread(target=update)
updateCall.setDaemon(True)
updateCall.start()

def confirmsasl():
    while True:
        ircmsg = irc.recv(2048)
        ircmsg = ircmsg.decode("UTF-8")
        ircmsg = ircmsg.split()
        print(ircmsg)
        ircmsg = " ".join(ircmsg)
        success = ":SASL authentication successful"
        failure = ":SASL authentication failed"
        aborted = ":SASL authentication aborted"
        if success in ircmsg: 
            return True
        elif failure in ircmsg:
            return False
        elif aborted in ircmsg:
            return False

def recieve(commandNone = False):

    global t, nickname, hostmask, msg_type, chan, message, command, args
    
    binary_data = irc.recv(1024)
    # Decode data from UTF-8
    data = binary_data.decode("UTF-8")
    # Split data by spaces
    t = data.strip(":")#.split()
    t = t.split()

    print (t)
    # Listen for PING
    hostmask = ""
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

        if message and message[0].startswith(":"+commandCharacter):
            command = " ".join(message).split()
            command[0] = command[0].strip(":")
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

def isHostmask(mask):
    if "!" in mask and "@" in mask:
        return True
    else:
        return False

def gethostmask(nick):
    irc.send("WHO {0}\r\n".format(nick).encode("UTF-8"))
    ircmsg = irc.recv(2048)
    ircmsg = ircmsg.decode("UTF-8")
    ircmsg = ircmsg.strip("\r\n")
    ircmsg = ircmsg.strip(":")
    ircmsg = ircmsg.split()
    print(ircmsg)
    if ircmsg[1] == "352":
        user = ircmsg[4]
        host = ircmsg[5]
        hm = "{0}!{1}@{2}".format(nick, user, host)
        return hm
    else:
        return False

def banmask(nick):
    mask = gethostmask(nick)
    if not mask:
        return False
    nick = mask.split("!")[0]
    user = mask.split("!")[1].split("@")[0]
    host = mask.split("@")[1]
    if host.startswith("gateway/"):
        if "/irccloud.com/" in host:
            uid = user[1:]
            host = host.split("/")
            host = "/".join(host[:-1])
            bm = "*!*{0}@{1}/*".format(uid, host)
            return bm
        elif "/ip." in host:
            host = host.split("/ip.")
            host = host[1]
            bm = "*!*@*{0}".format(host)
            return bm
        else:
            host = host.split("/")
            host = "/".join(host[:-1])
            bm = "*!{0}@{1}/*".format(user, host)
            return bm
    elif host.startswith("nat/"):
        host = host.split("/")
        host = "/".join(host[:-1])
        bm = "*!{0}@{1}/*".format(user, host)
        return bm
    elif "/" in host:
        bm = "*!*@{0}".format(host)
        return bm
    elif user.startswith("~"):
        bm = "*!*@{0}".format(host)
        return bm
    else:
        bm = "*!{0}@{1}".join(user, host)
        return bm

#=========================================================================================#
#=========================================================================================#
#=========================================================================================#

ircSend("QUIT") #In case of the bot being reloaded
connectAndIdentify()

while True:
    recieve()
    channelLink()
    last(None, "refresh")

    if isIgnored(hostmask):
        continue

    try:
        if t[3] == botnick + "," and t[4] == "char" or t[3] == botnick + ":" and t[4] == "char":
            irc.send("PRIVMSG {0} :{1}, My current command character is: {2}\r\n".format(chan, nickname, commandCharacter).encode("UTF-8"))            
    
        if t[1] == "KICK" and t[3] == botnick:
            irc.send("JOIN {0}\r\n".format(t[2]).encode("UTF-8"))
    except:
        pass
    

    if len(command) >= 1:
        if command[0] == "list" and len(command) == 1:
            if len(command) >= 2 and command[1] in ["-0", "-1", "-2"] or len(command) >= 2:
                command[1] = command[1].replace("-","")
                if command[1] not in ["0", "1", "2"]:
                    irc.send("PRIVMSG {0} :{1}, That permission lvl doesn't exist [1-2]\r\n".format(chan, nickname).encode("UTF-8"))
                
                elif int(command[1]) == 0:
                    irc.send("PRIVMSG {0} :{1}, Commands: {2} {3} {4}\r\n".format(chan, nickname, "\x0303" + ", ".join(userCommands)  + ",", "\x0304" + ", ".join(adminCommands) + ",", "\x0304" + ", ".join(ownerCommands)).encode("UTF-8"))

                elif int(command[1]) == 1:
                    irc.send("PRIVMSG {0} :{1}, Commands: {2} {3} {4}\r\n".format(chan, nickname, "\x0303" + ", ".join(userCommands)  + ",", "\x0303" + ", ".join(adminCommands) + ",", "\x0304" + ", ".join(ownerCommands)).encode("UTF-8"))
                    
                elif int(command[1]) == 2:
                    irc.send("PRIVMSG {0} :{1}, Commands: {2} {3} {4}\r\n".format(chan, nickname, "\x0303" + ", ".join(userCommands)  + ",", "\x0303" + ", ".join(adminCommands) + ",", "\x0303" + ", ".join(ownerCommands)).encode("UTF-8"))

            else:
                textToAdd = "\x0303" + ", ".join(userCommands)  + ", " 
                if isAdmin(hostmask):
                    textToAdd = textToAdd + "\x0303"
                else:
                    textToAdd = textToAdd + "\x0304"
                textToAdd = textToAdd + ", ".join(adminCommands)

                if isOwner(hostmask):
                    textToAdd = textToAdd + "\x0303"
                else:
                    textToAdd = textToAdd + "\x0304"
                textToAdd = textToAdd + ", " + ", ".join(ownerCommands)
                irc.send("PRIVMSG {0} : {1}, Commands: {2}\r\n".format(chan, nickname, textToAdd).encode("UTF-8"))

        elif command[0] == "status":
            irc.send("PRIVMSG {0} :I have been awake {1} minutes and have seen {2} messages.\r\n".format(chan, (int(time()) - int(startTime)) / 60, messagesSeen).encode("UTF-8"))
                

        elif len(command) >= 2 and command[0] == "perm" and  command[1] == "level":
            if isOwner(hostmask):
                irc.send("PRIVMSG {0} :{1}, your permissions lvl is: 2\r\n".format(chan, nickname).encode("UTF-8"))
            elif isAdmin(hostmask):
                irc.send("PRIVMSG {0} :{1}, your permissions lvl is: 1\r\n".format(chan, nickname).encode("UTF-8"))
            elif isIgnored(hostmask):
                irc.send("PRIVMSG {0} :{1}, your permissions lvl is: -1\r\n".format(chan, nickname).encode("UTF-8"))
            else:
                irc.send("PRIVMSG {0} :{1}, your permissions lvl is: 0\r\n".format(chan, nickname).encode("UTF-8"))

        elif len(command) >= 2 and command[0] == "list" and command[1] == "channels":
            irc.send("PRIVMSG {0} :Channel(s) I'm in: {1}\r\n".format(nickname, ", ".join(channels)).encode("UTF-8"))

        elif command[0] == "help":
            if len(command) == 1:
                irc.send("PRIVMSG {0} :{1}, try {2}list for a command listing\r\n".format(chan, nickname, commandCharacter).encode("UTF-8"))

            elif command[1] in userCommands:
                irc.send("PRIVMSG {0} :{1}, Help on this command: {2}\r\n".format(chan, nickname, userCommands[" ".join(command[1:])]).encode("UTF-8"))
            elif command[1] in adminCommands:
                irc.send("PRIVMSG {0} :{1}, Help on this command: {2}\r\n".format(chan, nickname, adminCommands[" ".join(command[1:])]).encode("UTF-8"))
            elif command[1] in ownerCommands:
                irc.send("PRIVMSG {0} :{1}, Help on this command: {2}\r\n".format(chan, nickname, ownerCommands[" ".join(command[1:])]).encode("UTF-8"))

                    
        elif command[0] == "moo":
            irc.send("PRIVMSG {0} :{1}, Mooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo!\r\n".format(chan, nickname).encode("UTF-8"))

        elif command[0] == "last":
            last(nickname, command[1])

        if command[0] == "time":
            irc.send("PRIVMSG {0} :{1}, {2}\r\n".format(chan, nickname, time()).encode("UTF-8"))

        elif command[0] == "echo":
            irc.send("PRIVMSG {0} :\u200B{1}\r\n".format(chan, " ".join(command[1:]).replace("+i ", "\x1D").replace("+b ", "\x02").replace("+u ", "\x1F").replace("+yellow ", "\x0308").replace("+purple ", "\x0306").replace("+orange ", "\x0307").replace("+reset ", "\x0F").replace("+gray ", "\x0300").replace("+black ", "\x0301").replace("+blue ", "\x0302").replace("+green " , "\x0303").replace("+red ", "\x0304").replace("+brown ", "\x0305")).encode("UTF-8"))

        elif command[0] == "bug":
            if len(command) >= 2:
                bugs = open("Bugs.txt", "a")
                bugs.write(nickname + " :" + " ".join(command[1:]) + "\n")
                irc.send("PRIVMSG {0} :{1}, Bug has been reported\r\n".format(chan, nickname).encode("UTF-8"))
                bugs.close()
            else:
                irc.send("PRIVMSG {0} :{1}, No bug to report\r\n".format(chan, nickname).encode("UTF-8"))

        # For now, this isn't going to work
        #elif len(command) >= 2 and command[0] == "list" and command[1] == "admins":
        #    irc.send("PRIVMSG {0} :Bot admins are: {1}\r\n".format(nickname, " ".join(stats)).encode("UTF-8"))

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

    if isAdmin(hostmask):
        if command[0] == "join" and command[1]:
            irc.send("JOIN {0}\r\n".format(command[1]).encode("UTF-8"))
            channels.append(command[1])
            
        elif command[0] == "commandChar"  and len(command) >= 2:
            if commandCharacter == command[1]:
                irc.send("PRIVMSG {0} :{1}, That command character is already in use!\r\n".format(chan, nickname).encode("UTF-8"))
            else:
                irc.send("PRIVMSG {0} :My command character has been changed to: {1}\r\n".format(chan, command[1]).encode("UTF-8"))
                setupCommands(command[1])
                
        elif command[0] == "leave" and len(command) >= 2:
            irc.send("PART {0}\r\n".format(command[1]).encode("UTF-8"))
            channels.remove(command[1])

        elif command[0] == "kick" and len(command) >= 2:
            if command[1]:
                irc.send("KICK {0} {1} :{2}\r\n".format(chan, command[1], " ".join(command[2:]) or command[1]).encode("UTF-8"))

            else:
                irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *kick <nickname> [reason]\r\n".format(chan, nickname).encode("UTF-8"))

        elif command[0] == "op" and len(command) >= 1:
            if len(command) == 1:
                irc.send("MODE {0} +o {1}\r\n".format(chan, nickname).encode("UTF-8"))

            else:
                irc.send("MODE {0} +o {1}\r\n".format(chan, command[1]).encode("UTF-8"))

        elif command[0] == "deop" and len(command) >= 1:
            if len(command) == 1:
                irc.send("MODE {0} -o {1}\r\n".format(chan, nickname).encode("UTF-8"))

            else:
                irc.send("MODE {0} -o {1}\r\n".format(chan, command[1]).encode("UTF-8"))

        elif command[0] == "sop" and len(command) >= 1:
            if len(command) == 1:
                irc.send("PRIVMSG ChanServ :OP {0}\r\n".format(chan).encode("UTF-8"))

            else:
                irc.send("PRIVMSG ChanServ :OP {0} {1}\r\n".format(chan, command[1]).encode("UTF-8"))

        elif command[0] == "sdeop" and len(command) >= 1:
            if len(command) == 1:
                irc.send("PRIVMSG ChanServ :DEOP {0}\r\n".format(chan).encode("UTF-8"))

            else:
                irc.send("PRIVMSG ChanServ :DEOP {0} {1}\r\n".format(chan, command[1]).encode("UTF-8"))

        elif command[0] == "ban" and len(command) >= 2:
            if isHostmask(command[1]):
                mask = command[1]
            else:
                mask = banmask(command[1])
                if not mask:
                    irc.send("PRIVMSG {0} :{1}, ERROR: No such nick\r\n".format(chan, nickname).encode("UTF-8"))
                    continue
            irc.send("MODE {0} +b {1}\r\n".format(chan, mask).encode("UTF-8"))
            bans[command[1]] = mask

        elif command[0] == "unban" and len(command) >= 2:
            try:
                irc.send("MODE {0} -b {1}\r\n".format(chan, bans[command[1]]).encode("UTF-8"))
                del bans[command[1]]
            except:
                pass

        elif command[0] == "kban" and len(command) >= 2:
            if isHostmask(command[1]):
                mask = command[1]
            else:
                mask = banmask(command[1])
                if not mask:
                    irc.send("PRIVMSG {0} :{1}, ERROR: No such nick\r\n".format(chan, nickname).encode("UTF-8"))
                    continue
            irc.send("MODE {0} +b {1}\r\n".format(chan, mask).encode("UTF-8"))
            irc.send("KICK {0} {1} :{2}\r\n".format(chan, t[7], " ".join(command[2:]) or "Kicked/moo", nickname).encode("UTF-8"))
            bans[command[1]] = mask

        elif command[0] == "channel" and command[1] == "links":
            channelLink(command[2], command[3], command[4])

        elif command[0] == "action" and len(command) >= 2:
                irc.send("PRIVMSG {0} :\x01ACTION {1}\x01\r\n".format(chan, " ".join(command[1:])).encode("UTF-8"))

        elif command[0] == "voice" and len(command) >= 2:
            irc.send("MODE {0} +v {1}\r\n".format(chan, command[1]).encode("UTF-8"))
            
        elif command[0] == "devoice" and len(command) >= 2:
            irc.send("MODE {0} -v {1}\r\n".format(chan, command[1]).encode("UTF-8"))

        elif command[0] == "quiet" and len(command) >= 2:
            if isHostmask(command[1]):
                mask = command[1]
            else:
                mask = banmask(command[1])
                if not mask:
                    irc.send("PRIVMSG {0} :{1}, ERROR: No such nick\r\n".format(chan, nickname).encode("UTF-8"))
                    continue
            irc.send("MODE {0} +q {1}\r\n".format(chan, mask).encode("UTF-8"))

        elif command[0] == "unquiet" and len(command) >= 2:
            if isHostmask(command[1]):
                mask = command[1]
            else:
                mask = banmask(command[1])
                if not mask:
                    irc.send("PRIVMSG {0} :{1}, ERROR: No such nick\r\n".format(chan, nickname).encode("UTF-8"))
                    continue
            irc.send("MODE {0} -q {1}\r\n".format(chan, mask).encode("UTF-8"))

    if isOwner(hostmask):
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
            os.execv(sys.executable, [sys.executable] + sys.argv)
                
        elif len(command) >= 2 and command[0] == "permissions" and command[2] == "=":
            try:
                if command[3] == "1" or command[3] == "0" or command[3] == "2" or command[3] == "-1":
                    if isHostmask(command[1]):
                        mask = command[1]
                    else:
                        mask = banmask(command[1])
                        if not mask:
                            irc.send("PRIVMSG {0} :{1}, ERROR: No such nick\r\n".format(chan, nickname))
                            continue
                    if command[3] == "-1":
                        try:
                            if mask in admins:
                                admins.remove(mask)
                            if mask in owners:
                                owners.remove(mask)
                            if not mask in ignores:
                                ignores.append(mask)
                            perms(True)
                            irc.send("PRIVMSG {0} :{1}, {2} permissions lvl set to -1\r\n".format(chan, nickname, mask).encode("UTF-8"))
                        except:
                            pass
                    elif command[3] == "0":
                        try:
                            if mask in admins:
                                admins.remove(mask)
                            if mask in owners:
                                owners.remove(mask)
                            if mask in ignores:
                                ignores.remove(mask)
                            perms(True)
                            irc.send("PRIVMSG {0} :{1}, {2} permissions lvl set to 0\r\n".format(chan, nickname, mask).encode("UTF-8"))
                        except:
                            pass
                    elif command[3] == "1" or command[3] == "2":
                        if command[3] == "1":
                            if mask in owners:
                                owners.remove(mask)
                            if mask in ignores:
                                ignores.remove(mask)
                            if not mask in admins:
                                admins.append(mask)
                        if command[3] == "2":
                            if mask in admins:
                                admins.remove(mask)
                            if mask in ignores:
                                ignores.remove(mask)
                            if not mask in owners:
                                owners.append(mask)
                        perms(True)
                        irc.send("PRIVMSG {0} :{1}, {2} permissions lvl set to {3}\r\n".format(chan, nickname, mask, command[3]).encode("UTF-8"))
                    else:
                        irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *permissions = 0/1\r\n".format(chan, nickname).encode("UTF-8"))
            except:
                irc.send("PRIVMSG {0} :{1}, INVALID: syntax. USAGE: *permissions = 0/1\r\n".format(chan, nickname).encode("UTF-8"))

    #except:
     #   pass

    messagesSeen += 1

#=========================================================================================#
#=========================================================================================#
#=========================================================================================#


