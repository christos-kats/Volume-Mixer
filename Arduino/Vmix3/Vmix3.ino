#include <LiquidCrystal.h>
#include <Arduino_JSON.h>
#include <Rotary.h>
#include <Debounce.h>

LiquidCrystal oled(12, 11, 10, 9, 8, 7, 6, 5, 4, A3);
Rotary selector = Rotary(2, 3);
Debounce selectorButton(A2);

const byte chars = 20;
const byte rows = 2;
boolean screenOn = true;
int serialTimeout = 20000;
String idleText = "Volume Mixer";

boolean oldSelectButtonState = false;
unsigned long buttonTime = 0;
int buttonThreshold = 1000;
boolean buttonHold = false;
boolean connectedToSerial = false;
unsigned long lastSerial = 0;
String app;
int volume;
boolean mute = false;
boolean volumeAdjust = true;

unsigned long oldSelectorTime = 0;

void setup() {
  pinMode(A2, INPUT);
  Serial.begin(115200);
  Serial.setTimeout(200);
  oled.begin(20, 2);
  oled.setRowOffsets(0, 32, 20, 52);
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
      sendDataLine("error", "Error parsing JSON data");
    }
    else {
      String jsonKeyString;
      String jsonKeyType;
      byte jsonKeys = jsonInput.keys().length() - 1;
      boolean refresh = false;
      for (byte jsonKeyIndex = 0; jsonKeyIndex <= jsonKeys; jsonKeyIndex++) {
        jsonKeyString = jsonInput.keys()[jsonKeyIndex];
        jsonKeyType = JSON.typeof(jsonInput[jsonKeyString]);
        if (jsonKeyString == "*command") {
          String command;
          command = jsonInput[jsonKeyString];
          if (command == "loadSettings") {
            JSONVar settings;
            settings["chars"] = chars;
            settings["rows"] = rows;
            settings["screenOn"] = screenOn;
            settings["serialTimeout"] = serialTimeout;
            settings["idleText"] = idleText;
            String settingsString = JSON.stringify(settings);
            Serial.println(settingsString);
          }
          else if (command == "volumeAdjust"){
            sendBooleanLine("volumeAdjust", volumeAdjust);
          }
        }
        else if (jsonKeyString == "*serialTimeout" && jsonKeyType == "number") {
          serialTimeout = jsonInput[jsonKeyString];
          sendNumberLine("serialTimeout", serialTimeout);
        }
        else if (jsonKeyString == "*idleText" && jsonKeyType == "string") {
          idleText = jsonInput[jsonKeyString];
          sendDataLine("idleText", idleText);
          refresh = !connectedToSerial;
        }
        else if (jsonKeyString == "*mute" && jsonKeyType == "boolean") {
          mute = jsonInput[jsonKeyString];
          refresh = connectedToSerial;
        }
        else if (jsonKeyString == "*volumeAdjust" && jsonKeyType == "boolean") {
          volumeAdjust = jsonInput[jsonKeyString];
          refresh = connectedToSerial;
          sendBooleanLine("volumeAdjust", volumeAdjust);
        }
        else if (jsonKeyString.charAt(0) != '*' && jsonKeyType == "number") {
          app = jsonKeyString;
          volume = jsonInput[jsonKeyString];
          connectedToSerial = true;
          lastSerial = millis();
          mute = false;
          refresh = true;
        }
        else {
          sendDataLine("error", "Error in JSON data format");
        }
      }
      if (refresh) {
        refreshScreen();
      }
    }
  }
  else if (millis() > lastSerial + serialTimeout && connectedToSerial) {
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
        sendBooleanLine("volumeAdjust", volumeAdjust);
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
        refreshScreen();
      }
      else if (!volumeAdjust) {
        sendDataLine("command", "nextApp");
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
        refreshScreen();
      }
      else if (!volumeAdjust) {
        sendDataLine("command", "previousApp");
      }
    }
  }
}

void muteApp() {
  mute = !mute;
  JSONVar data;
  data[app] = volume;
  data["mute"] = mute;
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
  byte specialCharArray[] = {0x00, 0x04, 0x06, 0x07, 0x07, 0x06, 0x04, 0x00};
    oled.createChar(7, specialCharArray);
  oled.setCursor(0, row);
  if (specialChar){
    oled.write(7);
  }
  else{
    oled.print(" ");
  }
  for (byte i = !(text.length() % 2) ; i <= (screenWidth - text.length()) / 2 -1; i++) {
    fillString = fillString + " ";
  }
  oled.print(fillString+ text + fillString);
  if (!(text.length() % 2)){
    oled.print(" ");
  }
}

void progressBar(byte percentage, byte row) {
  byte filledBlocks = percentage / 5;
  byte lastBlock = percentage % 5;
  byte bar0[8] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  byte bar1[8] = { 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10};
  byte bar2[8] = { 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18};
  byte bar3[8] = { 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C};
  byte bar4[8] = { 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E};
  byte bar5[8] = { 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F};
  oled.createChar(1, bar0);
  oled.createChar(2, bar1);
  oled.createChar(3, bar2);
  oled.createChar(4, bar3);
  oled.createChar(5, bar4);
  oled.createChar(6, bar5);
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
