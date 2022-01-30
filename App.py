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
import logging
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
logging.basicConfig(filename='app.log', filemode='a', encoding='utf-8', level=logging.DEBUG)

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


# helper functions
def log(msg):
    d = datetime.datetime.now()
    logging.debug(d + " : " + msg)

def log_UID(list):
    content = ''
    for a in list:
        content += hex(a)+" "
    logging.debug("UID "+content)

print("Hold a card")

try:
    while True:
        UI, profileId = readerClass.read_block(PROFILEID_BLOCK)

        while profileId != None:
            # output to display
            lcd.clear()
            lcd.text("Working", 1, align='center')

            log_UID(UI)

            # try convert profileId to number
            UI_string = None
            try:
                UI_string = uiConverter.to_UI_string(UI)
            except:
                lcd.clear()
                lcd.text("ERROR Card", 1, align='center')
                lcd.text("try again", 2, align='center')

                # log
                log("Error card")
                e = sys.exc_info()[0]
                log(e)

                sleep(3)
                UI = None
                profileId = None
                readerClass = RfidHelper()

            # debug output
            print("ID: %s" % (UI))
            print("ID HEX: "+ UI_string)
            print("TEXT: %s" % (profileId))

            # start request
            responseJSON = None
            try:
                responseJSON = apiRequests.AuthorizeProfile(UI_string, int(profileId))
            except:
                lcd.clear()
                lcd.text("Error api", 1, align='center')
                lcd.text("Try again", 2, align='center')
                
                # log
                log("Error API")
                e = sys.exc_info()[0]
                log(e)

                sleep(3)
                UI=None
                profileId = None
                readerClass = RfidHelper()

            # process with response
            if responseJSON != None:

                if responseJSON['IsError'] == True:
                    print(responseJSON['ErrorMsg'])
                    lcd.clear()
                    lcd.text("Error", 1, align='center')

                    # log
                    log("Api response error")
                    log(responseJSON['ErrorMsg'])

                    sleep(2)
                    UI = None
                    profileId = None
                    readerClass = RfidHelper()


            # wait for user input
                print('Select button')
                lcd.clear()
                lcd.text(responseJSON['ProfileName'], 1)


                # reset button status
                actionEnum.Reset()
                while actionEnum.ButtonSelected == 0:
                    # wait for intput
                    BTN_checkIn.when_activated = actionEnum.ClickCheckIn
                    BTN_checkOut.when_activated = actionEnum.ClickCheckOut

                lcd.text(actionEnum.GetActionName(), 2, align='center')
                print(actionEnum.GetActionName())
                
                # log
                log(actionEnum.GetActionName())
                
                sleep(1)

                # send user input
                try:
                    responseJSON = apiRequests.SendTimestamp(
                        actionEnum.GetActionName(),
                        responseJSON['ProfileId'],
                        responseJSON['CardId'],
                        responseJSON['TokenTimeStamp'],
                        responseJSON['TokenTimeStamp'])
                except:
                    lcd.clear()
                    lcd.text("Error api", 1, align='center')
                    lcd.text("Try again", 2, align='center')

                    # log
                    log("Error on api")
                    e = sys.exc_info()[0]
                    log(e)
                    
                    sleep(3)
                    UI=None
                    profileId = None
                    readerClass = RfidHelper()

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
                    lcd.text("Not valid",2, align='center')
                    print("ERROR posting timestamp")
                    
                    # log
                    log("Error posting timestamp")

                    sleep(5)


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

                # log
                log("Card not valid")

                sleep(10)


            print("Hold a card")
            profileId = None
            UI = None
            
            # reset reader class to prevent problems
            readerClass = RfidHelper()


        # update time on the monitor
        x = datetime.datetime.now()

        lcd.text(x.strftime("%H:%M:%S"),1)
        lcd.text("Hold a Card", 2, align='center')




except KeyboardInterrupt:
    print("Exit")

except: 
    # log
    e = sys.exc_info()[0]
    log(e)


