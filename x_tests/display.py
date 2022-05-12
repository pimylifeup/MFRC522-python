from time import time
from rpi_lcd import LCD
from time import sleep

lcd = LCD()

lcd.text("Test", 1)
lcd.text("ist da ok", 2)

sleep(10)