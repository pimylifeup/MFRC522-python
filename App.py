import configuration
from rfid_helper import RfidHelper
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import Button
from platoApi import ApiRequests
import os
from loggingLogic import DebugHelper
from byteconverter import UiConverter
from rpi_lcd import LCD
import datetime
import sys


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
debug = DebugHelper(True)

# start lcd
lcd.clear()
lcd.text("Loading ...",1)

## check for access token
debug.log("Request Token // loading ...")
ACCESS_TOKEN = apiRequests.RequestToken()

# MIFARE Blocks
PROFILEID_BLOCK = config.read_config()['MifareBlockUserId']

# global vars
buttonSelected = 0
actionSelected = 0   # 1 = checkIn  2 = checkOut

debug.log("Start reading RFID Tag + init RfidHelper Class")
readerClass = RfidHelper()


debug.log("Hold a card")

try:
    while True:
        UI, profileId = readerClass.read_block(PROFILEID_BLOCK)

        while profileId != None:
            # output to display
            lcd.clear()
            lcd.text("Working", 1, align='center')

            debug.log("a card was read")
            debug.log_UID(UI)

            # try convert profileId to number
            UI_string = None
            try:
                UI_string = uiConverter.to_UI_string(UI)
            except:
                lcd.clear()
                lcd.text("ERROR Card", 1, align='center')
                lcd.text("try again", 2, align='center')

                # log
                debug.log("Error card - reading UI - converting to string")
                e = sys.exc_info()[0]
                debug.log(e)

                sleep(3)
                UI = None
                profileId = None
                readerClass = RfidHelper()

            # debug output
            debug.log("ID: %s" % (UI))
            debug.log("ID HEX: "+ UI_string)
            debug.log("TEXT: %s" % (profileId))

            # start request
            debug.log("Start authorize api ...")
            responseJSON = None
            try:
                responseJSON = apiRequests.AuthorizeProfile(UI_string, int(profileId))
            except:
                lcd.clear()
                lcd.text("Error api", 1, align='center')
                lcd.text("Try again", 2, align='center')
                
                # log
                debug.log("Error API")
                e = sys.exc_info()[0]
                debug.log(e)

                sleep(3)
                UI=None
                profileId = None
                readerClass = RfidHelper()


            debug.log("Api request OK - parse JSON ...")
            # process with response
            if responseJSON != None:

                if responseJSON['IsError'] == True:
                    lcd.clear()
                    lcd.text("Error", 1, align='center')

                    # log
                    debug.log("Response error")
                    debug.log(responseJSON['ErrorMsg'])

                    sleep(2)
                    UI = None
                    profileId = None
                    readerClass = RfidHelper()


            # wait for user input
                debug.log('Select button')
                lcd.clear()
                lcd.text(responseJSON['ProfileName'], 1)


                # reset button status
                actionEnum.Reset()
                while actionEnum.ButtonSelected == 0:
                    # wait for intput
                    BTN_checkIn.when_activated = actionEnum.ClickCheckIn
                    BTN_checkOut.when_activated = actionEnum.ClickCheckOut

                lcd.text(actionEnum.GetActionName(), 2, align='center')

                # log
                debug.log("pressed: " + actionEnum.GetActionName())
                
                sleep(1)

                # send user input
                debug.log("Start POST api button pressed")
                try:
                    responseJSON = apiRequests.SendTimestamp(
                        actionEnum.GetActionName(),
                        responseJSON['ProfileId'],
                        responseJSON['CardId'],
                        responseJSON['TokenTimeStamp'],
                        datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S"))
                except:
                    lcd.clear()
                    lcd.text("Error api", 1, align='center')
                    lcd.text("Try again", 2, align='center')

                    # log
                    debug.log("Error on api")
                    e = sys.exc_info()[0]
                    debug.log(e)
                    
                    sleep(3)
                    UI=None
                    profileId = None
                    readerClass = RfidHelper()

                # check response
                if responseJSON['Success'] == True:
                    # display ok for 3 sec
                    lcd.clear()
                    lcd.text("OK", 1, align='center')
                    debug.log('Success POST Timestamp')
                    sleep(3)

                else:
                    # display error for 3 sec
                    lcd.clear()
                    lcd.text("ERROR", 1, align='center')
                    lcd.text("Not valid",2, align='center')
                    
                    # log
                    debug.log("ERROR posting timestamp")

                    sleep(3)


                # reset to normality
                actionEnum.Reset()

                # clear display
                lcd.clear()


            else:
                # display ERROR
                lcd.clear()
                lcd.text("ERROR", 1, align='center')
                lcd.text("AUTH NOT VALID", 2, align='center')

                # log
                debug.log("Error on Authentication")

                sleep(5)


            debug.log("Hold a card")
            profileId = None
            UI = None
            
            # reset reader class to prevent problems
            readerClass = RfidHelper()


        # update time on the monitor
        x = datetime.datetime.now()

        lcd.text(x.strftime("%H:%M:%S"),1)
        lcd.text("Hold a Card", 2, align='center')




except KeyboardInterrupt:
    debug.log("Exit: pressed CTRL+C")

except: 
    # log
    e = sys.exc_info()[0]
    debug.log(e)


