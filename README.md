# Volume Mixer

## Introduction

Volume Mixer allows you to control the volume of individual applications on your computer using an Arduino with a rotary encoder and an LCD/OLED screen.

## Features

- View the current volume level of each app on the connected computer through an OLED screen.
- Control the volume of individual applications on your computer using a rotary encoder.

## Requirements

### Hardware Components

- Arduino board (using Arduino Uno R3)
- Rotary Encoder (using WaveShare Rotation Sensor)
- 20x2 LCD/OLED screen (using UC-2002ASWAS10)

### Software Dependencies

#### Python requirements

- Python 3.x
- `pycaw` library
- `pyqt5` library
- `pyserial` library
- `pywin32` library

#### Arduino requirements

- `Arduino_JSON` library (version 0.1.0, installation using the Arduino library manager)
- [`Rotary`](https://github.com/brianlow/Rotary) library
- [`Debounce`](https://github.com/wkoch/Debounce) library

## Installation

1. Clone the repository to your local machine.
2. Install the required Python dependencies.
3. Connect the hardware components (Arduino, rotary encoder, and OLED screen) as per the table in [connections](#connections):
4. Upload the Arduino sketch to your Arduino board using the Arduino IDE.

## Connections

This table shows the connections between Arduino pins and the corresponding components (OLED and Rotary Encoder). It may vary if using different hardware.

| Arduino Pin | Connection                  |
|-------------|-----------------------------|
| 5V          | OLED VCC, Rotary 5V         |
| GND         | OLED GND, OLED RW, Rotary GND|
| 2           | Rotary SIA                  |
| 3           | Rotary SIB                  |
| 4           | OLED D6                     |
| 5           | OLED D5                     |
| 6           | OLED D4                     |
| 7           | OLED D3                     |
| 8           | OLED D2                     |
| 9           | OLED D1                     |
| 10          | OLED D0                     |
| 11          | OLED ENABLE                 |
| 12          | OLED RS                     |
| A2          | Rotary SW                   |
| A3          | OLED D7                     |

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

