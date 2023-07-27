import os
import shutil
import winreg as reg

class StartupHandler:
    def __init__(self):
        startupFolder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcutName = "Volume Mixer.lnk"
        self.sourcePath = "main.py"
        self.targetPath = os.path.join(startupFolder, shortcutName)

    def addToStartup(self):
        shutil.copy(self.sourcePath, self.targetPath)
        print("addToStartup function called")

    def removeFromStartup(self):
        os.remove(self.targetPath)
        print("removeFromStartup function called")

    def isOnStartup(self):
        print("isOnStartup function called and returned")
        return os.path.exists(self.targetPath)