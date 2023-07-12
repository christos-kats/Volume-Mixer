#include <LiquidCrystal.h>
#include <Arduino_JSON.h>
#include <Rotary.h>
#include <Debounce.h>

LiquidCrystal oled(12, 11, 10, 9, 8, 7, 6, 5, 4, A3);
Rotary selector = Rotary(2, 3);
Debounce selectorButton(A2);

boolean oldSelectButtonState = false;
unsigned long buttonTime = 0;
int buttonThreshold = 1000;
boolean buttonHold = false;

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
      sendError("Error parsing JSON data");
    }
    else {
      byte lines = jsonInput.keys().length() - 1;
      for (byte line = 0; line <= lines; line++) {
        String positionString;
        positionString = jsonInput.keys()[line];
        int lineIndex;
        if (isDigit(positionString.charAt(0)) && !isDigit(positionString.charAt(1)) && positionString.length() == 2) {
          lineIndex = String(positionString.charAt(0)).toInt();
          String horizontalPosition = String(positionString.charAt(1));
          boolean center = false;
          boolean progressBar = false;
          if (horizontalPosition == "c") {
            center = true;
          }
          else if (horizontalPosition == "p") {
            progressBar = true;
          }
          else if (horizontalPosition != "l") {
            sendError("Error in JSON data format");
          }
          String text;
          text = jsonInput[positionString];
          printOledLine(lineIndex, progressBar, text);
        }
        else {
          sendError("Error in JSON data format");
        }
      }
    }
  }
}
void sendCommand(String command) {
  sendDataLine("command", command);
}

void sendError(String errorString) {
  sendDataLine("error", errorString);
}

void sendDataLine(String key, String text) {
  JSONVar data;
  data[key] = text;
  String dataString = JSON.stringify(data);
  Serial.println(dataString);
}
void printOledLine(byte line, boolean showProgressBar, String text) {
  if (showProgressBar) {
    progressBar(text.toInt(), line);
  }
  else {
    oled.setCursor(0, line);
    oled.print(text);
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
      sendCommand("stigmiaio");
    }
  }
  else if (selectButtonState) {
    if (buttonTime + buttonThreshold < millis() and !buttonHold) {
      buttonHold = true;
      sendCommand("hold");
    }
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

ISR(PCINT2_vect) {
  unsigned char selectorResult = selector.process();
  if (selectorResult == DIR_CW) {
    sendCommand("right");
  }
  else if (selectorResult == DIR_CCW) {
    sendCommand("left");
  }
}
