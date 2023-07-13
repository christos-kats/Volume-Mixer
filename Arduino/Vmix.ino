#include <LiquidCrystal.h>
#include <Arduino_JSON.h>
#include <Rotary.h>
#include <Debounce.h>

LiquidCrystal oled(12, 11, 10, 9, 8, 7, 6, 5, 4, A3);
Rotary selector = Rotary(2, 3);
Debounce selectorButton(A2);

const byte deviceId = 1;
boolean screenOn = true;
int serialTimeout = 2000;
int serialTimeoutOffset = 500;
int inputTimeout = 1000;
String idleText = "Volume Mixer";

boolean oldSelectButtonState = false;
unsigned long buttonTime = 0;
int buttonThreshold = 1000;
boolean buttonHold = false;
boolean connectedToSerial = false;
unsigned long timeOut = 0;
String app;
int volume;
boolean mute = false;
boolean volumeAdjust = true;
unsigned long oldSelectorTime = 0;

byte blank[8] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
byte progressBar1[8] = { 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10};
byte progressBar2[8] = { 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18};
byte progressBar3[8] = { 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C};
byte progressBar4[8] = { 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E};
byte progressBar5[8] = { 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F};
byte arrow[] = {0x10, 0x18, 0x1C, 0x1E, 0x1C, 0x18, 0x10, 0x00};

void setup() {
  pinMode(A2, INPUT);
  Serial.begin(115200);
  Serial.setTimeout(20);
  oled.begin(20, 2);
  oled.setRowOffsets(0, 32, 20, 52);
  oled.createChar(1, blank);
  oled.createChar(2, progressBar1);
  oled.createChar(3, progressBar2);
  oled.createChar(4, progressBar3);
  oled.createChar(5, progressBar4);
  oled.createChar(6, progressBar5);
  oled.createChar(7, arrow);
  selector.begin(true);
  PCICR |= (1 << PCIE2);
  PCMSK2 |= (1 << PCINT18) | (1 << PCINT19);
  sei();
  refreshScreen();
}

void loop() {
  receiveSerialData();
  readSelectorButton();
}

void receiveSerialData() {
  if (Serial.available() > 0) {
    String stringInput = Serial.readString();
    JSONVar jsonInput = JSON.parse(stringInput);
    if (JSON.typeof(jsonInput) == "undefined") {
      sendDataLine("*error", "Error parsing JSON data");
    }
    else {
      String jsonKeyString;
      String jsonKeyType;
      byte jsonKeys = jsonInput.keys().length() - 1;
      boolean refresh = false;
      if (jsonKeys > -1) {
        jsonKeyString = jsonInput.keys()[0];
        jsonKeyType = JSON.typeof(jsonInput[jsonKeyString]);
        if (jsonKeyString == "*command") {
          String command;
          command = jsonInput[jsonKeyString];
          if (command == "loadSettings") {
            JSONVar settings;
            settings["*deviceId"] = deviceId;
            settings["screenOn"] = screenOn;
            settings["serialTimeout"] = serialTimeout;
            settings["idleText"] = idleText;
            String settingsString = JSON.stringify(settings);
            Serial.println(settingsString);
          }
          /*else if (command == "volumeAdjust") {
            sendBooleanLine("*volumeAdjust", volumeAdjust);
          }*/
          else if (command == "saveSettings") {
            JSONVar settings;
            settings["*confirm"] = "saveSettings";
            for (byte jsonKeyIndex = 1; jsonKeyIndex <= jsonKeys; jsonKeyIndex++) {
              jsonKeyString = jsonInput.keys()[jsonKeyIndex];
              jsonKeyType = JSON.typeof(jsonInput[jsonKeyString]);
              if (jsonKeyString == "serialTimeout" && jsonKeyType == "number") {
                serialTimeout = jsonInput[jsonKeyString];
                settings["serialTimeout"] = serialTimeout;
              }
              else if (jsonKeyString == "idleText" && jsonKeyType == "string") {
                idleText = jsonInput[jsonKeyString];
                settings["idleText"] = idleText;
                //refresh = !connectedToSerial;
              }
              /*else if (jsonKeyString == "volumeAdjust" && jsonKeyType == "boolean") {
                volumeAdjust = jsonInput[jsonKeyString];
                refresh = connectedToSerial;
              }*/
              else if (jsonKeyString == "screenOn" && jsonKeyType == "boolean") {
                screenOn = jsonInput[jsonKeyString];
                settings["screenOn"] = screenOn;
                //refresh = !connectedToSerial;
              }
              else{
                sendDataLine("*error", "Error in JSON data format");
              }
            }
            String settingsString = JSON.stringify(settings);
            Serial.println(settingsString);
          }
          else{
            sendDataLine("*error", "Error in JSON data format");
          }
        }
        else if (jsonKeyString.charAt(0) != '*' && jsonKeyType == "number") {
          app = jsonKeyString;
          volume = jsonInput[jsonKeyString];
          connectedToSerial = true;
          refresh = true;
          mute = false;
          timeOut = millis() + serialTimeout + serialTimeoutOffset;
          if (jsonInput.hasOwnProperty("*mute")){
            mute = jsonInput["*mute"];
            }
          
        }
        else {
          sendDataLine("*error", "Error in JSON data format");
        }
      }
      if (refresh) {
        refreshScreen();
      }
    }
  }
  else if (millis() > timeOut && connectedToSerial) {
    connectedToSerial = false;
    refreshScreen();
  }
}

void readSelectorButton() {
  boolean selectButtonState = !selectorButton.read();
  if (selectButtonState and !oldSelectButtonState) {
    buttonTime = millis();
    oldSelectButtonState = true;
  }
  else if (!selectButtonState and oldSelectButtonState) {
    oldSelectButtonState = false;
    buttonHold = false;
    if (buttonTime + buttonThreshold > millis()) {
      if (connectedToSerial) {
        volumeAdjust = !volumeAdjust;
        //sendBooleanLine("*volumeAdjust", volumeAdjust);
        refreshScreen();
      }
    }
  }
  else if (selectButtonState) {
    if (buttonTime + buttonThreshold < millis() and !buttonHold) {
      buttonHold = true;
      if (connectedToSerial) {
        muteApp();
        refreshScreen();
      }
      else {
        screenOn = !screenOn;
        refreshScreen();
      }
    }
  }
}

ISR(PCINT2_vect) {
  if (connectedToSerial) {
    unsigned char selectorResult = selector.process();
    if (selectorResult == DIR_CW) {
      if (volumeAdjust && volume < 100) {
        volume += selectorSpeed();
        if (volume > 100) {
          volume = 100;
        }
        mute = false;
        sendNumberLine(app, volume);
        timeOut = millis() + inputTimeout;
        refreshScreen();
      }
      else if (!volumeAdjust) {
        sendDataLine("*command", "nextApp");
      }
    }
    else if (selectorResult == DIR_CCW) {
      if (volumeAdjust && volume > 0) {
        volume -= selectorSpeed();
        if (volume < 0) {
          volume = 0;
        }
        mute = false;
        sendNumberLine(app, volume);
        timeOut = millis() + inputTimeout;
        refreshScreen();
      }
      else if (!volumeAdjust) {
        sendDataLine("*command", "previousApp");
      }
    }
  }
}

void muteApp() {
  mute = !mute;
  timeOut = millis() + inputTimeout;
  JSONVar data;
  data[app] = volume;
  data["*mute"] = mute;
  String dataString = JSON.stringify(data);
  Serial.println(dataString);
}
void refreshScreen() {
  if (connectedToSerial) {
    centerOnScreen(app, !volumeAdjust, 0, 20);
    if (mute) {
      centerOnScreen("Mute", false, 1, 20);
    }
    else {
      progressBar(volume, 1);
    }
  }
  else {
    oled.clear();
    if (screenOn) {
      centerOnScreen(idleText, false, 0, 20);
    }
  }
}

void centerOnScreen(String text, boolean specialChar, byte row, byte screenWidth) {
  String fillString = "";
  oled.setCursor(0, row);
  if (specialChar) {
    oled.write(7);
  }
  else {
    oled.print(" ");
  }
  for (byte i = !(text.length() % 2) ; i <= (screenWidth - text.length()) / 2 - 1; i++) {
    fillString = fillString + " ";
  }
  oled.print(fillString + text + fillString);
  if (!(text.length() % 2)) {
    oled.print(" ");
  }
}

void progressBar(byte percentage, byte row) {
  byte filledBlocks = percentage / 5;
  byte lastBlock = percentage % 5;
  oled.setCursor(0, row);
  for (int i = 0; i < filledBlocks; i++) {
    oled.write(6);
  }
  if (lastBlock) {
    oled.write(lastBlock + 1);
  }
  for (int i = filledBlocks; i < 20; i++) {
    oled.write(1);
  }
}

void sendDataLine(String key, String text) {
  JSONVar data;
  data[key] = text;
  String dataString = JSON.stringify(data);
  Serial.println(dataString);
}

void sendNumberLine(String key, int number) {
  JSONVar data;
  data[key] = number;
  String dataString = JSON.stringify(data);
  Serial.println(dataString);
}
void sendBooleanLine(String key, boolean boolValue) {
  JSONVar data;
  data[key] = boolValue;
  String dataString = JSON.stringify(data);
  Serial.println(dataString);
}

byte selectorSpeed() {
  unsigned long newSelectorTime = millis();
  byte selSpeed;
  int timeDifference = newSelectorTime - oldSelectorTime;
  if (timeDifference < 50) {
    selSpeed = 3;
  }
  else {
    selSpeed = 1;
  }
  oldSelectorTime = newSelectorTime;
  return selSpeed;
}
