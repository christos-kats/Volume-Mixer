from PyQt5 import QtWidgets
import sys
import tray
import mainwindow
import settings

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    volumeSetings = settings.VolumeMixerSettings()
    volumeMixerWindow = mainwindow.VolumeMixerWindow(volumeSetings)
    volumeMixerTray = tray.VolumeMixerTray(app, volumeMixerWindow)
    volumeMixerTray.show()
    volumeMixerWindow.init()
    sys.exit(app.exec_())
