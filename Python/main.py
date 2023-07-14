from PyQt5 import QtCore, QtGui, QtWidgets
from comtypes import CoInitialize, CoUninitialize

class connectThread(QtCore.QThread):
    connectionFinished = QtCore.pyqtSignal()
    connectionError = QtCore.pyqtSignal(tuple)
    def __init__(self,volumeMixer, port, baudRate, parent = None):
        super().__init__(parent=parent)
        self.volumeMixer = volumeMixer
        self.port = port
        self.baudRate = baudRate
    # den kanei error an einai me lathos baud rate
    def run(self):
        try:
            self.volumeMixer.connect(self.port, self.baudRate)
        except Exception as error:
            self.connectionError.emit((True, "Connection Error", str(error)))
            return
        self.connectionFinished.emit()

class updateThread(QtCore.QThread):
    updateError = QtCore.pyqtSignal(tuple)
    disconnectSignal = QtCore.pyqtSignal()
    def __init__(self, volumeMixer, parent= None):
        super().__init__(parent=parent)
        self.VolumeMixer = volumeMixer
    def run(self):
        CoInitialize()
        maxError = 3
        readErrorCount = 0
        updateErrorCount = 0
        try:
            self.VolumeMixer.initAudioDevice()
        except Exception as error:
            self.updateError.emit((True,"Audio Initialization Error", str(error)))
            self.disconnectSignal.emit()
            return
        while self.VolumeMixer.isConnected():
            try:
                self.VolumeMixer.readHardwareModuleData()
                readErrorCount = 0
            except Exception as error:
                if self.VolumeMixer.isConnected():
                    readErrorCount+=1
                    self.updateError.emit((bool(readErrorCount >= maxError),"Read Error", str(error)))
                else:
                    self.updateError.emit((False,"Hardware Error", str(error)))
                    self.disconnectSignal.emit()
                    return
            try:
                self.VolumeMixer.updateAudioData()
                updateErrorCount = 0
            except Exception as error:
                updateErrorCount+=1
                self.updateError.emit((bool(updateErrorCount >= maxError), "Update Error", str(error)))
            if readErrorCount >= maxError or updateErrorCount >= maxError:
                self.disconnectSignal.emit()
                break
        CoUninitialize()

class settingUpdateThread(QtCore.QThread):
    settingUpdateFinished = QtCore.pyqtSignal()
    settingError = QtCore.pyqtSignal(tuple)
    def __init__(self, volumeMixer, settings, parent= None):
        super().__init__(parent=parent)
        self.volumeMixer = volumeMixer
        self.settings = settings
    def run(self):
        try:
            self.volumeMixer.saveHardwareModuleSettings(self.settings)
        except Exception as error:
            self.settingError.emit((True, "Setting update error", str(error)))
            return
        self.settingUpdateFinished.emit()
        

class VolumeMixerWindow(QtWidgets.QMainWindow):
    visibilityChanged = QtCore.pyqtSignal()
    errorToTray = QtCore.pyqtSignal(tuple)
    def __init__(self, windowsVolumeMixerSettings):
        super(VolumeMixerWindow, self).__init__()
        self.windowsVolumeMixerSettings = windowsVolumeMixerSettings
        self.setupUi()
        self.retranslateUi()
        #self.init()
    def setupUi(self):
        self.setObjectName("volumeMixerWindow")
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.resize(331, 355)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.usbSettingsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.usbSettingsGroupBox.setObjectName("usbSettingsGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.usbSettingsGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.portLabel = QtWidgets.QLabel(self.usbSettingsGroupBox)
        self.portLabel.setObjectName("portLabel")
        self.verticalLayout_2.addWidget(self.portLabel)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.portComboBox = QtWidgets.QComboBox(self.usbSettingsGroupBox)
        self.portComboBox.setObjectName("portComboBox")
        self.horizontalLayout_3.addWidget(self.portComboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.connectButton = QtWidgets.QPushButton(self.usbSettingsGroupBox)
        self.connectButton.setObjectName("connectButton")
        self.horizontalLayout_3.addWidget(self.connectButton)
        self.connectOnStartupCheckBox = QtWidgets.QCheckBox(self.usbSettingsGroupBox)
        self.connectOnStartupCheckBox.setObjectName("connectOnStartupCheckBox")
        self.verticalLayout_2.addWidget(self.connectOnStartupCheckBox)
        self.verticalLayout.addWidget(self.usbSettingsGroupBox)
        self.hardwareSettingsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.hardwareSettingsGroupBox.setObjectName("hardwareSettingsGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.hardwareSettingsGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.updateIntervalLabel = QtWidgets.QLabel(self.hardwareSettingsGroupBox)
        self.updateIntervalLabel.setObjectName("updateIntervalLabel")
        self.horizontalLayout.addWidget(self.updateIntervalLabel)
        self.updateIntervalSpinBox = QtWidgets.QDoubleSpinBox(self.hardwareSettingsGroupBox)
        self.updateIntervalSpinBox.setDecimals(1)
        self.updateIntervalSpinBox.setMinimum(0.5)
        self.updateIntervalSpinBox.setMaximum(20.0)
        self.updateIntervalSpinBox.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.updateIntervalSpinBox.setProperty("value", 2.0)
        self.updateIntervalSpinBox.setObjectName("updateIntervalSpinBox")
        self.horizontalLayout.addWidget(self.updateIntervalSpinBox)
        self.secondsLabel = QtWidgets.QLabel(self.hardwareSettingsGroupBox)
        self.secondsLabel.setObjectName("secondsLabel")
        self.horizontalLayout.addWidget(self.secondsLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.screenOnCheckBox = QtWidgets.QCheckBox(self.hardwareSettingsGroupBox)
        self.screenOnCheckBox.setObjectName("screenOnCheckBox")
        self.verticalLayout_3.addWidget(self.screenOnCheckBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.screenTextLabel = QtWidgets.QLabel(self.hardwareSettingsGroupBox)
        self.screenTextLabel.setObjectName("screenTextLabel")
        self.horizontalLayout_2.addWidget(self.screenTextLabel)
        self.screenTextLineEdit = QtWidgets.QLineEdit(self.hardwareSettingsGroupBox)
        self.screenTextLineEdit.setMaxLength(18)
        self.screenTextLineEdit.setObjectName("screenTextLineEdit")
        self.horizontalLayout_2.addWidget(self.screenTextLineEdit)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.applyButton = QtWidgets.QPushButton(self.hardwareSettingsGroupBox)
        self.applyButton.setObjectName("applyButton")
        self.buttonLayout.addWidget(self.applyButton)
        self.defaultsButton = QtWidgets.QPushButton(self.hardwareSettingsGroupBox)
        self.defaultsButton.setObjectName("defaultsButton")
        self.buttonLayout.addWidget(self.defaultsButton)
        self.verticalLayout_3.addLayout(self.buttonLayout)
        self.verticalLayout.addWidget(self.hardwareSettingsGroupBox)
        self.windowsSettingsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.windowsSettingsGroupBox.setObjectName("windowsSettingsGroupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.windowsSettingsGroupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.startOnStartupCheckBox = QtWidgets.QCheckBox(self.windowsSettingsGroupBox)
        self.startOnStartupCheckBox.setObjectName("startOnStartupCheckBox")
        self.verticalLayout_4.addWidget(self.startOnStartupCheckBox)
        self.startOnTrayCheckBox = QtWidgets.QCheckBox(self.windowsSettingsGroupBox)
        self.startOnTrayCheckBox.setObjectName("startOnTrayCheckBox")
        self.verticalLayout_4.addWidget(self.startOnTrayCheckBox)
        self.verticalLayout.addWidget(self.windowsSettingsGroupBox)
        self.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName("statusbar")
        self.setStatusBar(self.statusBar)
        self.actionConnect = QtWidgets.QAction(self)
        self.actionConnect.setObjectName("actionConnect")
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("volumeMixerWindow", "Volume Mixer"))
        self.usbSettingsGroupBox.setTitle(_translate("volumeMixerWindow", "USB Settings"))
        self.portLabel.setText(_translate("volumeMixerWindow", "Port:"))
        self.connectButton.setText(_translate("volumeMixerWindow", "Connect"))
        self.connectOnStartupCheckBox.setText(_translate("volumeMixerWindow", "Connect on startup"))
        self.hardwareSettingsGroupBox.setTitle(_translate("volumeMixerWindow", "Hardware Settings"))
        self.updateIntervalLabel.setText(_translate("volumeMixerWindow", "Update Interval:"))
        self.secondsLabel.setText(_translate("volumeMixerWindow", "seconds"))
        self.screenOnCheckBox.setText(_translate("volumeMixerWindow", "Screen on when idling"))
        self.screenTextLabel.setText(_translate("volumeMixerWindow", "Screen text on idle:"))
        self.applyButton.setText(_translate("volumeMixerWindow", "Apply"))
        self.defaultsButton.setText(_translate("volumeMixerWindow", "Load defaults"))
        self.windowsSettingsGroupBox.setTitle(_translate("volumeMixerWindow", "Windows Settings"))
        self.startOnStartupCheckBox.setText(_translate("volumeMixerWindow", "Start on Windows startup"))
        self.startOnTrayCheckBox.setText(_translate("volumeMixerWindow", "Start minimized"))
        self.actionConnect.setText(_translate("volumeMixerWindow", "Connect"))     

    def init(self):
        self.startupHandler = startuphandler.StartupHandler()
        self.loadWindowsSettings()
        self.applyWindowsSettings()
        self.volumeMixer = volumemixer.volumeMixer(self.windowsVolumeMixerSettings.settings["supportedHardwareIds"], volumeUpdateInterval=self.windowsVolumeMixerSettings.settings["volumeUpdateInterval"], inputTimeout=self.windowsVolumeMixerSettings.settings["inputTimeout"])
        self.updateAvailablePortsTimer = QtCore.QTimer()
        self.oldPorts = []
        self.connectButton.setEnabled(False)
        self.getAvailablePorts()
        self.hardwareSettingsGroupBox.setEnabled(False)
        self.connectOnStartupCheckBox.setEnabled(False)
        self.applyButton.clicked.connect(self.updateSettings)
        self.connectButton.clicked.connect(self.connectButtonAction)
        self.defaultsButton.clicked.connect(self.updateSettingsInUi)
        self.updateAvailablePortsTimer.timeout.connect(self.getAvailablePorts)
        self.updateIntervalSpinBox.valueChanged.connect(self.enableButtons)
        self.screenTextLineEdit.textEdited.connect(self.enableButtons)
        self.screenOnCheckBox.clicked.connect(self.enableButtons)
        #self.connectOnStartupCheckBox.clicked.connect(self.startOnTrayChanged)
        self.startOnTrayCheckBox.clicked.connect(self.startOnTrayChanged)
        self.startOnStartupCheckBox.clicked.connect(self.startOnStartupChanged)
        self.updateAvailablePortsTimer.setInterval(500)
        self.updateAvailablePortsTimer.start()
        if not self.windowsVolumeMixerSettings.settings["startInTray"]:
            self.show()
            self.visibilityChanged.emit()
        #auto-connect
        
    def getAvailablePorts(self):
        if not(self.volumeMixer.isConnected()):
            ports = self.volumeMixer.getAvailablePorts()
            if not(ports == self.oldPorts):
                self.connectButton.setEnabled(bool(ports))
                self.portComboBox.clear()
                self.portComboBox.addItems(ports)
            self.oldPorts = ports

    def connect(self):
        port = self.portComboBox.currentText()
        self.statusBar.showMessage("Connecting")
        self.connectionThread = connectThread(self.volumeMixer, port, self.windowsVolumeMixerSettings.settings["baudRate"])
        self.connectionThread.connectionFinished.connect(self.connectionFinished)
        self.connectionThread.connectionError.connect(self.errorHandler)
        self.connectionThread.finished.connect(self.connectionThread.deleteLater)
        #finished 
        self.connectionThread.start()
    
    def connectionFinished(self):
        self.updateAvailablePortsTimer.stop()
        self.updateSettingsInUi()
        self.connectButton.setText("Disconnect")
        self.statusBar.showMessage("Connected")
        self.portComboBox.setEnabled(False)
        self.hardwareSettingsGroupBox.setEnabled(True)
        self.connectOnStartupCheckBox.setEnabled(True)
        self.updateThread = updateThread(self.volumeMixer)
        self.updateThread.updateError.connect(self.errorHandler)
        self.updateThread.disconnectSignal.connect(lambda: self.disconnect(False))
        self.updateThread.finished.connect(self.updateThread.deleteLater)
        self.updateThread.start()

    def updateSettingsInUi(self):
        self.updateIntervalSpinBox.blockSignals(True)
        self.updateIntervalSpinBox.setValue(self.volumeMixer.hardwareModuleSettings[self.volumeMixer.hardwareModuleUpdateIntervalIdentifier]/1000)
        self.updateIntervalSpinBox.blockSignals(False)
        self.screenOnCheckBox.setChecked(self.volumeMixer.hardwareModuleSettings["screenOn"])
        self.screenTextLineEdit.setText(self.volumeMixer.hardwareModuleSettings["idleText"])
        self.disableButtons()

    def disableButtons(self):
        self.applyButton.setEnabled(False)
        self.defaultsButton.setEnabled(False)

    def enableButtons(self):
        self.applyButton.setEnabled(True)
        self.defaultsButton.setEnabled(True)

    def disconnect(self, refreshStrtusBar = True):
        if self.volumeMixer.isConnected():
            self.volumeMixer.disconnect()
        if refreshStrtusBar:
            self.statusBar.showMessage("Disconnected")
        self.updateAvailablePortsTimer.start()
        self.connectButton.setText("Connect")
        self.portComboBox.setEnabled(True)
        self.hardwareSettingsGroupBox.setEnabled(False)
        self.connectOnStartupCheckBox.setEnabled(False)
    
    def connectButtonAction(self):
        if self.volumeMixer.isConnected():
            self.disconnect()
        else:
            self.connect()
        
    def updateSettings(self):
        settings = {self.volumeMixer.hardwareModuleUpdateIntervalIdentifier: round(self.updateIntervalSpinBox.value()*1000), "screenOn": bool(self.screenOnCheckBox.checkState()), "idleText":self.screenTextLineEdit.text()}
        self.settingUpdateThread = settingUpdateThread(self.volumeMixer, settings)
        self.settingUpdateThread.settingError.connect(self.errorHandler)
        self.settingUpdateThread.settingUpdateFinished.connect(self.settingUpdateFinished)
        self.settingUpdateThread.finished.connect(self.settingUpdateThread.deleteLater)
        self.settingUpdateThread.start()

    def settingUpdateFinished(self):
        self.disableButtons()
        self.statusBar.showMessage("Settings updated.")
    
    def errorHandler(self, error):
        self.statusBar.showMessage(error[1]+ ": " + error[2])
        if self.isVisible():
            if error[0]:
                errorBox = QtWidgets.QMessageBox()
                errorBox.setWindowIcon(self.icon)
                errorBox.setIcon(QtWidgets.QMessageBox.Warning)
                errorBox.setText(error[2])
                errorBox.setWindowTitle(error[1])
                errorBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                errorBox.exec()
        else:
            self.errorToTray.emit(error)

    def applyWindowsSettings(self):
        self.connectOnStartupCheckBox.setChecked(self.windowsVolumeMixerSettings.settings["connectionPort"].isalnum())# != "")
        self.startOnStartupCheckBox.setChecked(self.startupHandler.isOnStartup())
        self.startOnTrayCheckBox.setChecked(self.windowsVolumeMixerSettings.settings["startInTray"])

    def startOnTrayChanged(self):
        if not self.changeWindowsSetting("startInTray", self.startOnTrayCheckBox.isChecked()):
            self.startOnTrayCheckBox.setChecked(not(self.startOnTrayCheckBox.isChecked()))

    def startOnStartupChanged(self):
        startOnStartupChecked = self.startOnStartupCheckBox.isChecked()
        if startOnStartupChecked:
            try:
                self.startupHandler.addToStartup()
            except: 
                startOnStartupChecked = False
                self.startOnStartupCheckBox.setChecked(startOnStartupChecked)
                self.errorHandler((True, "Startup setting error", "Failed to add to startup."))
        else:
            try:
                self.startupHandler.removeFromStartup()
            except:
                startOnStartupChecked = True
                self.startOnStartupCheckBox.setChecked(startOnStartupChecked) 
                self.errorHandler((True, "Startup setting error", "Failed to remove from startup."))

    def changeWindowsSetting(self, settingName, value):
        try:
            updatedWindowsSettings = {}
            updatedWindowsSettings[settingName] = value
            self.windowsVolumeMixerSettings.settings.update(updatedWindowsSettings)
            self.windowsVolumeMixerSettings.saveSettings()
        except Exception as error:
            self.errorHandler((True, "Setting error", str(error)))
            return False
        return True
    
    def loadWindowsSettings(self):
        try:
            self.windowsVolumeMixerSettings.loadSettings()
        except Exception as error:
            self.errorHandler((True, "Setting error", str(error)))
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.visibilityChanged.emit()

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

if __name__ == "__main__":
    import sys
    import volumemixer
    import volumemixersettings
    import startuphandler

    app = QtWidgets.QApplication(sys.argv)
    volumeSetings = volumemixersettings.VolumeMixerSettings()
    #volumeSetings.loadSettings()
    volumeMixerWindow = VolumeMixerWindow(volumeSetings)
    trayApp = VolumeMixerTray(app, volumeMixerWindow)
    trayApp.show()
    volumeMixerWindow.init()
    sys.exit(app.exec_())
