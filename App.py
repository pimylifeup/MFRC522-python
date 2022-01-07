import configuration
from rfid_helper import RfidHelper
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import Button
from platoApi import ApiRequests
import os
from byteconverter import UiConverter


# GPIO
BTN_checkIn = Button(17)
BTN_checkOut = Button(18)


# vars
ACCESS_TOKEN = ''

# SETUP
base_path = os.getcwd()
apiRequests = ApiRequests(base_path)
uiConverter = UiConverter()
config = configuration.ConfigurationIO(base_path)
actionEnum = configuration.ActionEnum()

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

                if responseJSON['IsError'] == True:
                    print(responseJSON['ErrorMsg'])
                    sleep(1)
                    UI = None
                    profileId = None

            # display info

            ## display Name
            ## display Errors
            ## display Time

            # wait for user input
                print('Select button')
                while actionEnum.ButtonSelected == 0:
                    # wait for intput
                    BTN_checkIn.when_activated = actionEnum.ClickCheckIn
                    BTN_checkOut.when_activated = actionEnum.ClickCheckOut

                # send user input
                responseJSON = apiRequests.SendTimestamp(
                    actionEnum.GetActionName(),
                    responseJSON['ProfileId'],
                    responseJSON['CardId'],
                    responseJSON['TokenTimeStamp'],
                    responseJSON['TokenTimeStamp'])

                # check response
                if responseJSON['Success'] == True:
                    # display ok for 3 sec
                    
                    print('Success POST Timestamp')
                    sleep(3)

                else:
                    # display error for 3 sec

                    print("ERROR posting timestamp")
                    sleep(3)


                # reset to normality
                actionEnum.Reset()

                # clear display


            else:
                # display ERROR
                print("Error on Authentication")
                sleep(10)

            sleep(2)
            print("Hold a card")
            profileId = None
            UI = None


        # update time on the monitor




except KeyboardInterrupt:
    raise


