from base64 import b64encode
import socket
import ssl

def connectAndIdentify():

    server = "chat.freenode.net"
    port = 6697
    channels = ["##BWBellairs", "##powder-bots", "#botters-test"]
    botnick = "BWBellairs[Bot]"
    realname = "BWBellairs[Bot]"
    ident = "BWBellairs[Bot]"
    use_ssl = True
    use_sasl = True
    password = raw_input("Enter password")
    username = "BWBellairs[Bot]"
    command = "$None$"
    nickname = "BWBellairs[Bot]"

    global irc

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
        irc.send("CAP END\r\n".encode("UTF-8"))
    else:
        irc.send("USER {0} {1} blah :{2}\r\n".format(
                ident, botnick, realname).encode("UTF-8"))  # user authentication
        irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))  # sets nick
        irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                username, password).encode("UTF-8"))  # auth

    irc.send("JOIN {0}\r\n".format(",".join(channels)).encode("UTF-8"))  # join the channel(s)