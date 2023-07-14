from PyQt5 import QtCore, QtGui, QtWidgets
from comtypes import CoInitialize, CoUninitialize
import volumemixersettings

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
        

class Ui_volumeMixerWindow(object):
    def setupUi(self, volumeMixerWindow):
        volumeMixerWindow.setObjectName("volumeMixerWindow")
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        volumeMixerWindow.setWindowIcon(self.icon)
        volumeMixerWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        volumeMixerWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        volumeMixerWindow.resize(331, 355)
        self.centralwidget = QtWidgets.QWidget(volumeMixerWindow)
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
        volumeMixerWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(volumeMixerWindow)
        self.statusBar.setObjectName("statusbar")
        volumeMixerWindow.setStatusBar(self.statusBar)
        self.actionConnect = QtWidgets.QAction(volumeMixerWindow)
        self.actionConnect.setObjectName("actionConnect")
        self.retranslateUi(volumeMixerWindow)
        QtCore.QMetaObject.connectSlotsByName(volumeMixerWindow)

    def retranslateUi(self, volumeMixerWindow):
        _translate = QtCore.QCoreApplication.translate
        volumeMixerWindow.setWindowTitle(_translate("volumeMixerWindow", "Volume Mixer"))
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
        # messagebox if not
        self.WindowsVolumeMixerSettings = volumemixersettings.VolumeMixerSettings()
        self.windowsSettings = self.WindowsVolumeMixerSettings.loadSettings()
        self.applyWindowsSettings()
        self.volumeMixer = volumemixer.volumeMixer(self.windowsSettings["supportedHardwareIds"], volumeUpdateInterval=self.windowsSettings["volumeUpdateInterval"], inputTimeout=self.windowsSettings["inputTimeout"])
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
        self.connectOnStartupCheckBox.clicked.connect(self.updateWindowsSettings)
        self.startOnTrayCheckBox.clicked.connect(self.updateWindowsSettings)
        self.startOnStartupCheckBox.clicked.connect(self.updateWindowsSettings)
        self.updateAvailablePortsTimer.setInterval(500)
        self.updateAvailablePortsTimer.start()
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
        self.connectionThread = connectThread(self.volumeMixer, port, self.windowsSettings["baudRate"])
        self.connectionThread.connectionFinished.connect(self.connectionFinished)
        self.connectionThread.connectionError.connect(self.errorHandler)
        self.connectionThread.finished.connect(self.connectionThread.deleteLater)
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
        #update?
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
        if error[0]:
            errorBox = QtWidgets.QMessageBox()
            errorBox.setWindowIcon(self.icon)
            errorBox.setIcon(QtWidgets.QMessageBox.Warning)
            errorBox.setText(error[2])
            errorBox.setWindowTitle(error[1])
            errorBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorBox.exec()

    def applyWindowsSettings(self):
        self.connectOnStartupCheckBox.setChecked(self.windowsSettings["autoConnect"])
        self.startOnStartupCheckBox.setChecked(self.windowsSettings["onStartup"])
        self.startOnTrayCheckBox.setChecked(self.windowsSettings["startInTray"])

    def updateWindowsSettings(self):
        updatedWindowsSettings = {}
        updatedWindowsSettings["autoConnect"] = self.connectOnStartupCheckBox.isChecked()
        updatedWindowsSettings["onStartup"] = self.startOnStartupCheckBox.isChecked()
        updatedWindowsSettings["startInTray"] = self.startOnTrayCheckBox.isChecked()
        self.windowsSettings.update(updatedWindowsSettings)
        #msgbox
        self.WindowsVolumeMixerSettings.saveSettings(self.windowsSettings)

class VolumeMixerTray(QtWidgets.QSystemTrayIcon):
    def __init__(self, mainWindow):
        super(VolumeMixerTray, self).__init__()
        self.mainWindow = mainWindow
        self.setIcon(QtGui.QIcon("icon.png"))
        self.menu = QtWidgets.QMenu()
        self.showAction = QtWidgets.QAction("Show Window", self)
        self.showAction.triggered.connect(self.showWindow)
        self.menu.addAction(self.showAction)

        self.quitAction = QtWidgets.QAction("Quit", self)
        self.quitAction.triggered.connect(self.quitApp)
        self.menu.addAction(self.quitAction)

        self.setContextMenu(self.menu)

        self.activated.connect(self.showWindow)

    def showWindow(self):
        self.mainWindow.show()

    def quitApp(self):
        QApplication.quit()

    #def on_tray_activated(self, reason):
    #    if reason == QSystemTrayIcon.Trigger:
    #        main_window.show()

if __name__ == "__main__":
    import sys
    import volumemixer
    app = QtWidgets.QApplication(sys.argv)
    volumeMixerWindow = QtWidgets.QMainWindow()
    ui = Ui_volumeMixerWindow()
    ui.setupUi(volumeMixerWindow)
    ui.init()
    trayApp = VolumeMixerTray(volumeMixerWindow)
    trayApp.show()
    #volumeMixerWindow.show()
    sys.exit(app.exec_())
