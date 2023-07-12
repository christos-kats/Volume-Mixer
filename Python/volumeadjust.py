from ctypes import cast, POINTER
from typing import MutableMapping
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume

class volumeAdjust():
    def __init__(self):
        self.masterVolume = None

    def initMasterAudio(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.masterVolume = cast(interface, POINTER(IAudioEndpointVolume))

    def getMasterVolume(self):
        currentVolume = round(self.masterVolume.GetMasterVolumeLevelScalar()*100)
        mute = self.masterVolume.GetMute()
        return currentVolume, mute

    def setMasterVolume(self, volume, mute):
        self.masterVolume.SetMasterVolumeLevelScalar(volume/100, None)
        self.masterVolume.SetMute(mute,None)

    def getAllAppVolume(self):
        appList = {}
        muteList = {}
        sessionList = {}
        duplicateApps = {}
        audioSessions = AudioUtilities.GetAllSessions()
        for audioSession in audioSessions:
            volume = audioSession._ctl.QueryInterface(ISimpleAudioVolume)
            if audioSession.Process:
                appName = audioSession.Process.name()[:-4].title()
                mute = volume.GetMute()
                appVolume = round(volume.GetMasterVolume()*100)
                if appName in appList:
                    appList.update({appName + " (1)" : appList[appName]})
                    appList.pop(appName)
                    muteList.update({appName + " (1)" : muteList[appName]})
                    muteList.pop(appName)
                    sessionList.update({appName + " (1)" : sessionList[appName]})
                    sessionList.pop(appName)
                    duplicateApps[appName] = 1
                if appName in duplicateApps:
                    duplicateApps[appName] += 1
                    appName = appName + " (" + str(duplicateApps[appName]) + ")"
                appList.update({appName : appVolume})
                muteList.update({appName: mute})
                sessionList.update({appName: volume})
        return appList, muteList, sessionList

    def setAppVolume(self, session, volume, mute):
        session.SetMasterVolume(volume/100, None)
        session.SetMute(mute,None)