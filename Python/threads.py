from PyQt5 import QtCore
from comtypes import CoInitialize, CoUninitialize

class connectThread(QtCore.QThread):
    connectionFinished = QtCore.pyqtSignal()
    connectionError = QtCore.pyqtSignal(tuple)
    def __init__(self,volumeMixer, port, baudRate, parent = None):
        super().__init__(parent=parent)
        self.volumeMixer = volumeMixer
        self.port = port
        self.baudRate = baudRate
        
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