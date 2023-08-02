# Volume Mixer

## Introduction

Volume Mixer allows you to control the volume of individual applications on your computer using an Arduino with a rotary encoder and an LCD/OLED screen. The utility on the computer side is written in Python and leverages the pycaw and PyQt5 libraries to communicate with the Arduino and control application volumes.

## Features

- View the current volume level of each app on the connected computer through an OLED screen.
- Control the volume of individual applications on your computer using a rotary encoder.

## Requirements

### Hardware Components

- Arduino board (e.g., Arduino Uno, Arduino Nano)
- Rotary Encoder
- LCD/OLED screen (20x2)
- Wires and breadboard for connections

### Software Dependencies

#### Python requirements

- Python 3.x
- `pycaw` library
- `pyqt5` library
- `pyserial` library
- `pywin32` library

#### Arduino requirements

- `Arduino_JSON` library (version 0.1.0)
- `Rotary` library
- `Debounce` library

## Installation

1. Clone the repository to your local machine.
2. Install the required Python dependencies.
3. Connect the hardware components (Arduino, rotary encoder, and OLED screen) as per the provided schematic.
4. Upload the Arduino sketch to your Arduino board using the Arduino IDE.

## Usage

1. Connect the arduino to the computer using a USB cable.
2. Run the utility (`main.py`)
3. The utility should detect the Arduino automatically.
4. Select the port on which the Arduino is connected and click connect.
5. Press the rotary encoder button to enter "app selection mode."
6. Use the rotary encoder to scroll through the list of applications on your computer. The screen shows the name of the selected application and its volume.
7. Press the rotary encoder button again to select the desired application.
8. Use the rotary encoder to adjust the volume for the selected application.
9. Long-press the rotary encoder button for mute/unmute function.
10. You can now adjust the volume of each individual app using the rotary encoder on the Arduino.

