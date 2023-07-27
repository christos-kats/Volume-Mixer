import os
import pythoncom
import pywintypes
from win32com.shell import shell, shellcon

class StartupHandler:
    def __init__(self):
        startupFolder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcutName = "Volume Mixer.lnk"
        self.sourcePath = "main.py"
        self.targetPath = os.path.join(startupFolder, shortcutName)

    def addToStartup(self):
        self.createShortcut(self.sourcePath, self.targetPath)
        print("addToStartup function called")

    def removeFromStartup(self):
        os.remove(self.targetPath)
        print("removeFromStartup function called")

    def isOnStartup(self):
        print("isOnStartup function called and returned")
        return os.path.exists(self.targetPath)
    
    def createShortcut(self, sourcePath, targetPath):
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
        )
        shortcut.SetPath(sourcePath)

        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(targetPath, 0)