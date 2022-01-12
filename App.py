import configuration
from rfid_helper import RfidHelper
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import Button
from platoApi import ApiRequests
import os
from byteconverter import UiConverter
from rpi_lcd import LCD
import datetime


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
lcd = LCD(width=16)

## check for access token
ACCESS_TOKEN = apiRequests.RequestToken()

# MIFARE Blocks
PROFILEID_BLOCK = config.read_config()['MifareBlockUserId']

# global vars
buttonSelected = 0
actionSelected = 0   # 1 = checkIn  2 = checkOut

lcd.clear()
lcd.text("Loading ...",1)
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

                if responseJSON['IsError'] == True:
                    print(responseJSON['ErrorMsg'])
                    lcd.clear()
                    lcd.text("Error", 1, align='center')
                    sleep(2)
                    UI = None
                    profileId = None

            # display info

            ## display Name
            ## display Errors
            ## display Time

            # wait for user input
                print('Select button')
                lcd.clear()
                lcd.text(responseJSON['ProfileName'], 1)
                while actionEnum.ButtonSelected == 0:
                    # wait for intput
                    BTN_checkIn.when_activated = actionEnum.ClickCheckIn
                    BTN_checkOut.when_activated = actionEnum.ClickCheckOut

                lcd.text(actionEnum.GetActionName(), 2, align='center')
                sleep(1)

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
                    lcd.clear()
                    lcd.text("OK", 1, align='center')
                    print('Success POST Timestamp')
                    sleep(3)

                else:
                    # display error for 3 sec
                    lcd.clear()
                    lcd.text("ERROR", 1, align='center')
                    lcd.text("API NOT READY",2, align='center')
                    print("ERROR posting timestamp")
                    sleep(10)


                # reset to normality
                actionEnum.Reset()

                # clear display
                lcd.clear()


            else:
                # display ERROR
                print("Error on Authentication")
                lcd.clear()
                lcd.text("ERROR", 1, align='center')
                lcd.text("CARD NOT VALID", 2, align='center')

                sleep(10)


            print("Hold a card")
            profileId = None
            UI = None


        # update time on the monitor
        x = datetime.datetime.now()

        lcd.text(x.strftime("%H:%M:%S"),1)
        lcd.text("Hold a Card", 2, align='center')



except KeyboardInterrupt:
    print("Exit")


