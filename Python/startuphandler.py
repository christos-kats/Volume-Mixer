import os
import pythoncom
import pywintypes
from win32com.shell import shell, shellcon

class StartupHandler:
    def __init__(self):
        startupFolder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        self.currentFolder = os.getcwd()
        shortcutName = "Volume Mixer.lnk"
        startName = "main.py"
        self.sourcePath = os.path.join(self.currentFolder,startName)
        self.targetPath = os.path.join(startupFolder, shortcutName)

    def addToStartup(self):
        self.createShortcut(self.sourcePath, self.targetPath, self.currentFolder)

    def removeFromStartup(self):
        os.remove(self.targetPath)

    def isOnStartup(self):
        return os.path.exists(self.targetPath)
    
    def createShortcut(self, sourcePath, targetPath, startIn):
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
        )
        shortcut.SetPath(sourcePath)
        shortcut.SetWorkingDirectory(startIn)
        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(targetPath, 0)