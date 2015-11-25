from socketS import *
from botCommands import *

t = returndata()[0]
nickname = returndata()[1]
hotmask = returndata()[2]
msg_type = returndata()[3]
chan = returndata()[4]
message = returndata()[5]
command = returndata()[6]
args = returndata()[7]

def command(command):
    if command:
        command = command.replace("*", "")
        if command.find("print") or command.find("import") or command.find("=") or command.find("if"):
            ircSend("PR", nickname, nickname, "Not allowed!")
        else:
            try:
                exec(command)
            except:
                print "ERROR"
    command = None
