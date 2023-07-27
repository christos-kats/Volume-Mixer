from PyQt5 import QtGui, QtWidgets

class VolumeMixerTray(QtWidgets.QSystemTrayIcon):
    def __init__(self,app, mainWindow):
        super(VolumeMixerTray, self).__init__()
        self.app = app
        self.mainWindow = mainWindow
        self.setIcon(QtGui.QIcon("icon.png"))
        self.menu = QtWidgets.QMenu()
        self.showAction = QtWidgets.QAction("Show Window", self)
        self.showAction.triggered.connect(self.showHideWindow)
        self.menu.addAction(self.showAction)

        self.quitAction = QtWidgets.QAction("Quit", self)
        self.quitAction.triggered.connect(self.quitApp)
        self.menu.addAction(self.quitAction)

        self.setContextMenu(self.menu)

        self.activated.connect(self.onTrayActivated)
        self.mainWindow.visibilityChanged.connect(self.visibilityChanged)
        self.mainWindow.errorToTray.connect(self.handleError)

    def showHideWindow(self):
        if self.mainWindow.isVisible():
            self.mainWindow.hide()
        else:
            self.mainWindow.show()
        self.visibilityChanged()
    
    def onTrayActivated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.showHideWindow()

    def quitApp(self):
        self.mainWindow.close()
        self.hide()
        self.app.quit()

    def visibilityChanged(self):
        if self.mainWindow.isVisible():
            self.showAction.setText("Hide window")
            return
        self.showAction.setText("Show window")
    
    def handleError(self, error):
        if error[0]:
            self.showMessage(error[1], error[2], QtWidgets.QSystemTrayIcon.Warning, 5000)
