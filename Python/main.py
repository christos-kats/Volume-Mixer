from PyQt5 import QtCore, QtGui, QtWidgets
from comtypes import CoInitialize, CoUninitialize

class connectThread(QtCore.QThread):
    connectionFinished = QtCore.pyqtSignal()
    connectionError = QtCore.pyqtSignal(tuple)
    def __init__(self,volumeMixer, port, parent = None):
        super().__init__(parent=parent)
        self.volumeMixer = volumeMixer
        self.port = port

    def run(self):
        try:
            self.volumeMixer.connect(self.port, 115200)
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
        volumeMixerWindow.setFixedSize(331, 355)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        volumeMixerWindow.setWindowIcon(self.icon)
        volumeMixerWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        volumeMixerWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.centralwidget = QtWidgets.QWidget(volumeMixerWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.usbSettingsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.usbSettingsGroupBox.setGeometry(QtCore.QRect(10, 10, 311, 111))
        self.usbSettingsGroupBox.setObjectName("usbSettingsGroupBox")
        self.portComboBox = QtWidgets.QComboBox(self.usbSettingsGroupBox)
        self.portComboBox.setGeometry(QtCore.QRect(10, 40, 191, 28))
        self.portComboBox.setObjectName("portComboBox")
        self.portLabel = QtWidgets.QLabel(self.usbSettingsGroupBox)
        self.portLabel.setGeometry(QtCore.QRect(10, 20, 55, 16))
        self.portLabel.setObjectName("portLabel")
        self.connectButton = QtWidgets.QPushButton(self.usbSettingsGroupBox)
        self.connectButton.setGeometry(QtCore.QRect(209, 39, 93, 30))
        self.connectButton.setObjectName("connectButton")
        self.connectOnStartup = QtWidgets.QCheckBox(self.usbSettingsGroupBox)
        self.connectOnStartup.setGeometry(QtCore.QRect(10, 80, 141, 20))
        self.connectOnStartup.setObjectName("connectOnStartup")
        self.hardwareSettingsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.hardwareSettingsGroupBox.setGeometry(QtCore.QRect(10, 130, 311, 191))
        self.hardwareSettingsGroupBox.setObjectName("hardwareSettingsGroupBox")
        self.updateIntervalLabel = QtWidgets.QLabel(self.hardwareSettingsGroupBox)
        self.updateIntervalLabel.setGeometry(QtCore.QRect(10, 30, 101, 21))
        self.updateIntervalLabel.setObjectName("updateIntervalLabel")
        self.secondsLabel = QtWidgets.QLabel(self.hardwareSettingsGroupBox)
        self.secondsLabel.setGeometry(QtCore.QRect(170, 30, 55, 21))
        self.secondsLabel.setObjectName("secondsLabel")
        self.screenOnCheckBox = QtWidgets.QCheckBox(self.hardwareSettingsGroupBox)
        self.screenOnCheckBox.setGeometry(QtCore.QRect(10, 60, 171, 21))
        self.screenOnCheckBox.setObjectName("screenOnCheckBox")
        self.screenTextLabel = QtWidgets.QLabel(self.hardwareSettingsGroupBox)
        self.screenTextLabel.setGeometry(QtCore.QRect(10, 90, 121, 21))
        self.screenTextLabel.setObjectName("screenTextLabel")
        self.screenTextLineEdit = QtWidgets.QLineEdit(self.hardwareSettingsGroupBox)
        self.screenTextLineEdit.setGeometry(QtCore.QRect(10, 110, 291, 22))
        self.screenTextLineEdit.setMaxLength(18)
        self.screenTextLineEdit.setObjectName("screenTextLineEdit")
        self.applyButton = QtWidgets.QPushButton(self.hardwareSettingsGroupBox)
        self.applyButton.setGeometry(QtCore.QRect(10, 150, 93, 28))
        self.applyButton.setObjectName("applyButton")
        self.defaultsButton = QtWidgets.QPushButton(self.hardwareSettingsGroupBox)
        self.defaultsButton.setGeometry(QtCore.QRect(110, 150, 93, 28))
        self.defaultsButton.setObjectName("defaultsButton")
        self.updateIntervalSpinBox = QtWidgets.QDoubleSpinBox(self.hardwareSettingsGroupBox)
        self.updateIntervalSpinBox.setGeometry(QtCore.QRect(110, 30, 51, 22))
        self.updateIntervalSpinBox.setDecimals(1)
        self.updateIntervalSpinBox.setMinimum(0.5)
        self.updateIntervalSpinBox.setMaximum(20.0)
        self.updateIntervalSpinBox.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.updateIntervalSpinBox.setProperty("value", 2.0)
        self.updateIntervalSpinBox.setObjectName("updateIntervalSpinBox")
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
        self.connectOnStartup.setText(_translate("volumeMixerWindow", "Connect on startup"))
        self.hardwareSettingsGroupBox.setTitle(_translate("volumeMixerWindow", "Hardware Settings"))
        self.updateIntervalLabel.setText(_translate("volumeMixerWindow", "Update Interval:"))
        self.secondsLabel.setText(_translate("volumeMixerWindow", "seconds"))
        self.screenOnCheckBox.setText(_translate("volumeMixerWindow", "Screen on when idling"))
        self.screenTextLabel.setText(_translate("volumeMixerWindow", "Screen text on idle:"))
        self.applyButton.setText(_translate("volumeMixerWindow", "Apply"))
        self.defaultsButton.setText(_translate("volumeMixerWindow", "Load defaults"))
        self.actionConnect.setText(_translate("volumeMixerWindow", "Connect"))
    
    def init(self):
        self.volumeMixer = volumemixer.volumeMixer([1])
        self.updateAvailablePortsTimer = QtCore.QTimer()
        self.oldPorts = []
        self.getAvailablePorts()
        self.hardwareSettingsGroupBox.setEnabled(False)
        self.applyButton.clicked.connect(self.updateSettings)
        self.connectButton.clicked.connect(self.connectButtonAction)
        self.defaultsButton.clicked.connect(self.updateSettingsInUi)
        self.updateAvailablePortsTimer.timeout.connect(self.getAvailablePorts)
        self.updateIntervalSpinBox.valueChanged.connect(self.enableButtons)
        self.screenTextLineEdit.textEdited.connect(self.enableButtons)
        self.screenOnCheckBox.clicked.connect(self.enableButtons)
        self.updateAvailablePortsTimer.setInterval(500)
        self.updateAvailablePortsTimer.start()
        
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
        self.connectionThread = connectThread(self.volumeMixer, port)
        self.connectionThread.connectionFinished.connect(self.connectionFinished)
        self.connectionThread.connectionError.connect(self.errorHandler)
        self.connectionThread.start()
    
    def connectionFinished(self):
        self.updateAvailablePortsTimer.stop()
        self.updateSettingsInUi()
        self.connectButton.setText("Disconnect")
        self.statusBar.showMessage("Connected")
        self.portComboBox.setEnabled(False)
        self.hardwareSettingsGroupBox.setEnabled(True)
        self.updateThread = updateThread(self.volumeMixer)
        self.updateThread.updateError.connect(self.errorHandler)
        self.updateThread.disconnectSignal.connect(lambda: self.disconnect(False))
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
        


if __name__ == "__main__":
    import sys
    import volumemixer
    app = QtWidgets.QApplication(sys.argv)
    volumeMixerWindow = QtWidgets.QMainWindow()
    ui = Ui_volumeMixerWindow()
    ui.setupUi(volumeMixerWindow)
    ui.init()
    volumeMixerWindow.show()
    sys.exit(app.exec_())
