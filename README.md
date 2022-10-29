# mfrc522

A python library to read/write RFID tags via the budget MFRC522 RFID module.

This code was published in relation to a [blog post](https://pimylifeup.com/raspberry-pi-rfid-rc522/) and you can find out more about how to hook up your MFRC reader to a Raspberry Pi there.

## Installation

Until the package is on PyPi, clone this repository and run `python setup.py install` in the top level directory.

<img src = "https://miro.medium.com/max/720/0*VsaGvGskvJa20hZa.png">

RFID Module | Spalte 2
-------- | --------
SDA   | Pin 24
SCK   | Pin 23
MOSI  | Pin 19
MISO  | Pin 21
GND   | Pin 6
RST   | Pin 22
3.3v  | Pin 1

## Example Code

The following code will read a tag from the MFRC522

```python
from time import sleep
import sys
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

try:
    while True:
        print("Hold a tag near the reader")
        id, text = reader.read()
        print("ID: %s\nText: %s" % (id,text))
        sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
```
