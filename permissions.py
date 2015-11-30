perms = {#1
    "##BWBellairs": ["BWBellairs", "1"],
    }

def permsSetup():
    for i in channels:
        irc.send("NAMES {0}\r\n".format(i).encode("UTF-8"))

        for users in Message:
            if perms[users] == "1" or perms[users] == "2" or perms[users] == "3":
                pass
            else:
                perms[i] = [users, "3"]

        print (perms)
