from . import MFRC522
import RPi.GPIO as GPIO
import string

class RfidHelper:

    READER = None
    KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    SECTOR_AUTH_BLOCK = [3,3,3,3,7,7,7,7,11,11,11,11,15,15,15,15]

    def __init__(self) -> None:
        self.READER = MFRC522()

    def setAuthCode(self, authKey)-> None: 
        self.KEY = authKey

    def read_id(self):
        (status, Tag) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None

        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None

        return uid

    def read_block(self, block_num: int):
        if block_num > len(self.SECTOR_AUTH_BLOCK):
            return (None, None)

        # init
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return (None, None)
        
        # read id
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return (None, None)

        # auth
        self.READER.MFRC522_SelectTag(uid)
        status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, self.SECTOR_AUTH_BLOCK[block_num], self.KEY, uid)

        # read block
        data = [] # output data holder
        output_text = ''

        if status == self.READER.MI_OK:
            block = self.READER.MFRC522_Read(block_num)
            print(block)
            if block:
                data += block

            if data:
                #output_text = ''.join(hex(i) for i in data)
                for i in data:
                    if i != 0:
                        char = chr(i)
                        output_text += char


        self.READER.MFRC522_StopCrypto1()

        return uid, output_text

        # return
