from time import strftime

#banTime = "193028"

#while True:
 #   time =  strftime("%H%M%S")
  #  print time

    #if time >= banTime:
     #   print "Done"
      #  quit()


bans = {
    "hostmask": ["##powder-bots", "193028"],
    }

def createBan(hostmask, chan, banTime):
    time =  strftime("%H%M%S")
    banTime = str(float(banTime / 60))

    banTimeLen = len(banTime)
    NbanTime = time[:-(len(banTime)) - 1]

    banTime = banTime.replace(".0", "")
    
    banTime = NbanTime + banTime

    print banTime

    bans[hostmask] = [chan, "m3"]

def refreshBan(bans = bans):
    for i in bans:
        if time:
            pass

createBan("stuff", "##BWBellairs", 1)

print str(float(10 / 5)).remove()
