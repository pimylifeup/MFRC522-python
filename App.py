import configuration
from rfid_helper import RfidHelper
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import Button
from platoApi import ApiRequests
import os
from byteconverter import UiConverter


# GPIO
BTN_checkIn = Button(3)
BTN_checkOut = Button(4)

# helpers
def btnPressCheckIn():
    actionSelected = 1
    buttonSelected = 1

def btnPressCheckOut():
    actionSelected = 2
    buttonSelected = 1

# vars
ACCESS_TOKEN = ''

# SETUP
apiRequests = ApiRequests(os.getcwd())
uiConverter = UiConverter()
config = configuration.ConfigurationIO()

## check for access token
ACCESS_TOKEN = apiRequests.RequestToken()

# MIFARE Blocks
PROFILEID_BLOCK = config.read_config()['MifareBlockUserId']

# global vars
buttonSelected = 0
actionSelected = 0   # 1 = checkIn  2 = checkOut

print ("Start reading RFID Tag")
readerClass = RfidHelper()

print("Hold a card")

try:
    while True:
        UI, profileId = readerClass.read_block(PROFILEID_BLOCK)

        while profileId != None:
            print("ID: %s" % (UI))
            UI_string = uiConverter.to_UI_string(UI)
            print("ID HEX: "+ UI_string)
            print("TEXT: %s" % (profileId))

            # start request
            responseJSON = apiRequests.AuthorizeProfile(UI_string, int(profileId))

            if responseJSON != None:
                sleep(1)

            # display info

            ## display Name
            ## display Errors
            ## display Time

            # wait for user input
                while buttonSelected == 0:
                    # wait for intput
                    BTN_checkIn.when_released = btnPressCheckIn
                    BTN_checkOut.when_released = btnPressCheckOut

                # send user input
                responseJSON = apiRequests.SendTimestamp(
                    actionSelected,
                    responseJSON['ProfileId'],
                    responseJSON['CardId'],
                    responseJSON['TokenTimeStamp'],
                    responseJSON['TokenTimeStamp'])

                # check response
                if responseJSON['Success'] == True:
                    # display ok for 3 sec
                    
                    sleep(3)

                else:
                    # display error for 3 sec

                    sleep(3)


                # reset to normality
                actionSelected = 0
                buttonSelected = 0

                # clear display


            else:
                # display ERROR
                sleep(10)

            sleep(2)
            print("Hold a card")
            profileId = None
            UI = None


        # update time on the monitor




except KeyboardInterrupt:
    raise


