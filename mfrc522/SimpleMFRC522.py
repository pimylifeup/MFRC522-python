# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import RPi.GPIO as GPIO
import datetime

class SimpleMFRC522:

    READER = None

    KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    BLOCK_ADDRS = [8, 9, 10]

    def __init__(self):
        self.READER = MFRC522()

    def read(self, **kwargs):
        '''
            read method accepting a timeout expressed as integer in seconds. For example
            read(timeout = 5) will enter the read mode for 5 sec. 
        '''
        idnum, text = self.read_no_block()

        #Log the current date and time and add timeout to the current time stamp in case entering the while loop
        if not kwargs: #If timeout keyword hasn't been provided read for infinity
            while not idnum:
                idnum, text = self.read_no_block()
        else:
            timeoutTime = datetime.datetime.now() + datetime.timedelta(kwargs['timeout'])
        
            while not idnum:
                if datetime.datetime.now() <= timeoutTime:
                    idnum, text = self.read_no_block()
        return idnum, text

    def read_id(self):
        idnum = self.read_id_no_block()
        while not idnum:
            idnum = self.read_id_no_block()
        return idnum

    def read_id_no_block(self):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None
        return self.uid_to_num(uid)

    def read_no_block(self):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None, None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None, None
        idnum = self.uid_to_num(uid)
        self.READER.MFRC522_SelectTag(uid)
        status = self.READER.MFRC522_Auth(
            self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
        data = []
        text_read = ''
        if status == self.READER.MI_OK:
            for block_num in self.BLOCK_ADDRS:
                block = self.READER.MFRC522_Read(block_num)
                if block:
                    data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
        self.READER.MFRC522_StopCrypto1()
        return idnum, text_read

    def write(self, text):
        idnum, text_in = self.write_no_block(text)
        while not idnum:
            idnum, text_in = self.write_no_block(text)
        return idnum, text_in

    def write_no_block(self, text):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None, None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None, None
        idnum = self.uid_to_num(uid)
        self.READER.MFRC522_SelectTag(uid)
        status = self.READER.MFRC522_Auth(
            self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
        self.READER.MFRC522_Read(11)
        if status == self.READER.MI_OK:
            data = bytearray()
            data.extend(bytearray(text.ljust(
                len(self.BLOCK_ADDRS) * 16).encode('ascii')))
            i = 0
            for block_num in self.BLOCK_ADDRS:
                self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
                i += 1
        self.READER.MFRC522_StopCrypto1()
        return idnum, text[0:(len(self.BLOCK_ADDRS) * 16)]

    def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n
