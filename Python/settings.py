import json

class VolumeMixerSettings:
    def __init__(self):
        self.settingsFile = "settings.txt"
        self.settings = {
            "supportedHardwareIds": [1],
            "connectionPort": "",
            "baudRate": 115200,
            "startInTray": False,
            "inputTimeout": 0.5,
            "volumeUpdateInterval": 0.2
        }
    def loadSettings(self):
        try:
            with open(self.settingsFile, "r") as file:
                fileSettings = json.load(file)
                self.settings.update(fileSettings)
        except FileNotFoundError:
            return self.settings
        except json.JSONDecodeError:
            raise Exception("Error decoding settings file.")
        except Exception as e:
            raise Exception(f"Error loading settings: {str(e)}")

    def saveSettings(self):
        try:
            with open(self.settingsFile, "w") as file:
                json.dump(self.settings, file, indent=4)
        except Exception as e:
            raise Exception(f"Error saving settings: {str(e)}")
    