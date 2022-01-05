from rfid_helper import RfidHelper
import RPi.GPIO
from time import sleep
from gpiozero import Button
from platoApi import ApiRequests
import os

# vars
ACCESS_TOKEN = ''

# SETUP
apiRequests = ApiRequests(os.getcwd())

## check for access token
ACCESS_TOKEN = apiRequests.RequestToken()




print ("Start reading RFID Tag")
readerClass = RfidHelper()

print("Hold a card")

try:
    while True:
        UI, text = readerClass.read_block(2)

        while text != None:
            print("ID: %s" % (UI))
            print("TEXT: %s" % (text))
            sleep(2)
            print("Hold a card")
            text = None



except KeyboardInterrupt:
    raise


