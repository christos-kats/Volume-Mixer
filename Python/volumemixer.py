import time
import serialcom
import volumeadjust
import json

class volumeMixer():
    def __init__(self, suppordedHardwareIds, hardwareModuleName = "Hardware Module", hardwareModuleUpdateInterval = 2, volumeUpdateInterval = 0.2, inputTimeout = 0.5, masterVolumeIdentifier = "Master Volume"):
        self.supportedHardwareIds = suppordedHardwareIds
        self.hardwareModuleName = hardwareModuleName
        self.hardwareModuleUpdateInterval = hardwareModuleUpdateInterval
        self.volumeUpdateInterval = volumeUpdateInterval
        self.inputTimeout = inputTimeout
        self.masterVolumeIdentifier = masterVolumeIdentifier
        self.connected = False
        self.volumeList = {}
        self.muteList = {}
        self.sessionList = {}
        self.currentApp = masterVolumeIdentifier
        self.oldApp = None
        self.oldVolume = 0
        self.oldMute = 0
        self.lastUpdate = 0
        self.lastInput = 0
        self.hardwareInput = False
        self.hardwareModule = None
        self.hardwareModuleSettings = {}
        self.confirmationList = []
        self.confirmationCheckInterval = 0.01
        self.deviceIdIdentifier = "*deviceId"
        self.hardwareModuleUpdateIntervalIdentifier = "serialTimeout"
        self.muteIdentifier = "*mute"
        self.commandIdentifier = "*command"
        self.confirmationIdentifier = "*confirm"
        self.errorIdentifier = "*error"
        self.loadSettingsCommand = "loadSettings"
        self.saveSettingsCommand = "saveSettings"
        self.nextAppCommand = "nextApp"
        self.previousAppcommand = "previousApp"
        self.volumeAdjust = volumeadjust.volumeAdjust()
        
    
    def getAvailablePorts(self):
        try:
            ports = serialcom.getAvailablePorts()
        except:
            raise Exception("Error getting available ports.")
        return ports

    def connect(self, port, baudRate, waitAfterConnection = 5):
        try:
            self.hardwareModule = serialcom.serialCommunication(port, baudRate, self.volumeUpdateInterval)
            self.hardwareModule.connect()
            loadSettingsCommand = {self.commandIdentifier:self.loadSettingsCommand}
            loadSettingsCommandString = json.dumps(loadSettingsCommand)
            time.sleep(waitAfterConnection)
            self.hardwareModule.serialWrite(loadSettingsCommandString)
            hardwareModuleSettingsString = self.hardwareModule.serialRead()[:-2]
            hardwareModuleSettings = json.loads(hardwareModuleSettingsString)
            deviceId = hardwareModuleSettings.pop(self.deviceIdIdentifier)
        except:
            raise Exception(f"Error connecting to {self.hardwareModuleName} on port {port}.")
        if deviceId in self.supportedHardwareIds:
            self.connected = True
            self.hardwareModuleSettings.update(hardwareModuleSettings)
            try:
                self.hardwareModuleUpdateInterval = self.hardwareModuleSettings[self.hardwareModuleUpdateIntervalIdentifier]/1000
            except:
                raise Exception(f"Error loading settings from {self.hardwareModuleName}.")
        else:
            raise Exception(f"Unsupported device (device ID: {deviceId}).")

    def isConnected(self):
        return self.connected

    def initAudioDevice(self):
        try:
            self.volumeAdjust.initMasterAudio()
        except:
            raise Exception("Error initializing volume control.")
    
    def readHardwareModuleData(self):
        hardwareModuleDataString = None
        try:
            hardwareModuleDataString = self.hardwareModule.serialRead()[:-2]
        except:
            if self.connected:
                try:
                    self.disconnect()
                except:
                    pass
                raise Exception(f"{self.hardwareModuleName} disconnected.")     
        if hardwareModuleDataString:
            hardwareModuleError = None
            try:
                hardwareModuleData = json.loads(hardwareModuleDataString)
                firstKey = list(hardwareModuleData.keys())[0]
                if firstKey == self.commandIdentifier:
                    self.handleCommand(hardwareModuleData)
                elif firstKey == self.confirmationIdentifier:
                    self.handleConfirmation(hardwareModuleData)
                elif firstKey == self.errorIdentifier:
                    hardwareModuleError = hardwareModuleData[firstKey]
                    raise
                else:
                    self.handleVolumeControl(hardwareModuleData)
            except:
                if hardwareModuleError:
                    raise Exception(f"Error in {self.hardwareModuleName}: {hardwareModuleError}")
                raise Exception(f"Error in {self.hardwareModuleName} data format.")
    
    def updateAudioData(self):
        try:
            self.updateAudioLists()
        except:
            raise Exception("Failed to update application list.")
        if  not (self.currentApp in self.volumeList):
            self.currentApp = self.masterVolumeIdentifier
        if not (self.currentApp == self.oldApp) or ((not(self.volumeList[self.currentApp] == self.oldVolume) or not(self.muteList[self.currentApp] == self.oldMute) 
        or self.hardwareInput or (time.time() >self.lastUpdate + self.hardwareModuleUpdateInterval)) and (time.time() > self.lastInput + self.inputTimeout)):
            try: 
                self.sendAudioData(self.currentApp)
            except:
                raise Exception(f"Error sending audio data to {self.hardwareModuleName}.")

    def disconnect(self):
        try:
            self.hardwareModule.disconnect()
            self.connected = False
        except:
            raise Exception(f"Error while disconnecting {self.hardwareModuleName}.")

    def sendAudioData(self, app):
        data = {app:self.volumeList[app]}
        if self.muteList[app]:
            data.update({self.muteIdentifier:bool(self.muteList[app])})
        dataStr = json.dumps(data)
        self.hardwareModule.serialWrite(dataStr)
        self.lastUpdate = time.time() 
        self.oldApp = self.currentApp
        self.oldVolume = self.volumeList[self.currentApp]
        self.oldMute = self.muteList[self.currentApp]
        self.hardwareInput = False
    
    def updateAudioLists(self):
        appVolumeList, appMuteList, self.sessionList = self.volumeAdjust.getAllAppVolume()
        masterVolume, masterMute = self.volumeAdjust.getMasterVolume()
        self.volumeList = {self.masterVolumeIdentifier : masterVolume}
        self.muteList = {self.masterVolumeIdentifier : masterMute}
        self.volumeList.update(appVolumeList)
        self.muteList.update(appMuteList)
    
    def handleVolumeControl(self, hardwareModuleData):
        app = list(hardwareModuleData.keys())[0]
        mute = False
        self.lastInput = time.time()
        self.hardwareInput = True
        if self.muteIdentifier in hardwareModuleData:
                mute = hardwareModuleData[self.muteIdentifier]    
        if app == self.masterVolumeIdentifier:
            self.volumeAdjust.setMasterVolume(hardwareModuleData[app], mute)
        elif app in self.volumeList:
            self.volumeAdjust.setAppVolume(self.sessionList[app], hardwareModuleData[app], mute)
        else:
            raise
    
    def handleCommand(self, hardwareModuleData):
        apps = list(self.volumeList)
        if len(apps) > 1:
            appIndex = apps.index(self.currentApp)
            if hardwareModuleData[self.commandIdentifier] == self.nextAppCommand:
                if appIndex == len(apps) -1:
                    appIndex = 0
                else:
                    appIndex += 1
            elif hardwareModuleData[self.commandIdentifier] == self.previousAppcommand:
                if appIndex == 0:
                    appIndex = len(apps) -1
                else:
                    appIndex -= 1
            else:
                raise
            self.currentApp = apps[appIndex]
    
    def handleConfirmation(self, hardWareModuleData):
        hardWareModuleData.pop(self.confirmationIdentifier)
        self.confirmationList.append(hardWareModuleData)
    
    def saveHardwareModuleSettings(self, settings):
        for setting in settings:
            if setting not in self.hardwareModuleSettings:
                raise Exception(f'Invalid setting "{setting}".')
            if setting == self.hardwareModuleUpdateIntervalIdentifier:
                self.hardwareModuleUpdateInterval = settings[setting]/1000
        try:
            data = {self.commandIdentifier:self.saveSettingsCommand}
            data.update(settings)
            dataStr = json.dumps(data)
            self.hardwareModule.serialWrite(dataStr)
            timeout = self.volumeUpdateInterval + time.time()
            while time.time() < timeout:
                if settings in self.confirmationList:
                    self.confirmationList.remove(settings)
                    self.hardwareModuleSettings.update(settings)
                    return
                time.sleep(self.confirmationCheckInterval)
        except:
            raise Exception("Error confirming setting update.")
        raise Exception("Setting update not confirmed (timed out).")

    def getHardwareModuleSettings(self):
        return self.hardwareModuleSettings