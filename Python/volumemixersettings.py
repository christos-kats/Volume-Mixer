import json

class VolumeMixerSettings:
    def __init__(self):
        self.settingsFile = "settings.txt"
        self.defaultSettings = {
            "supportedHardwareIds": [1],
            "connectionPort": "",
            "baudRate": 115200,
            "autoConnect": False,
            "onStartup": False,
            "startInTray": False,
            "inputTimeout": 0.5,
            "volumeUpdateInterval": 0.2
        }

    def loadSettings(self):
        try:
            with open(self.settingsFile, "r") as file:
                settings = self.defaultSettings
                fileSettings = json.load(file)
                settings.update(fileSettings)
                return settings
        except FileNotFoundError:
            return self.defaultSettings
        except json.JSONDecodeError:
            raise Exception("Error decoding settings file.")
        except Exception as e:
            raise Exception(f"Error loading settings: {str(e)}")

    def saveSettings(self, settings):
        try:
            with open(self.settingsFile, "w") as file:
                json.dump(settings, file, indent=4)
        except Exception as e:
            raise Exception(f"Error saving settings: {str(e)}")