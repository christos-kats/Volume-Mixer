class StartupHandler:
    def addToStartup(self):
        print("addToStartup function called")

    def removeFromStartup(self):
        print("removeFromStartup function called")

    def isOnStartup(self):
        value = True
        print("isOnStartup function called and returned", value)
        return value