def mainR(module = None):
    if module == None:
        print "No module to reload!"

    else:
        exec("reload(" + module + ")")
