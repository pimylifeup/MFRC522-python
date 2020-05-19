# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import RPi.GPIO as GPIO


class SimpleMFRC522:
    DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    _mfrc522 = MFRC522()
    _key = None

    def __init__(self, key=None):
        if key is None:
            key = SimpleMFRC522.DEFAULT_KEY
        self._key = key

    def read_id(self):
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        (status, TagType) = self._mfrc522.MFRC522_Request(
            self._mfrc522.PICC_REQIDL)
        if status != self._mfrc522.MI_OK:
            return None
        (status, uid) = self._mfrc522.MFRC522_Anticoll()
        if status != self._mfrc522.MI_OK:
            return None
        return self.uid_to_num(uid)

    def read(self, trailer=11, blocks=(8, 9, 10)):
        id, text = self.read_no_block(trailer=trailer, blocks=blocks)
        while not id:
            id, text = self.read_no_block(trailer=trailer, blocks=blocks)
        return id, text

    def read_no_block(self, trailer=11, blocks=(8, 9, 10)):
        (status, TagType) = self._mfrc522.MFRC522_Request(
            self._mfrc522.PICC_REQIDL)
        if status != self._mfrc522.MI_OK:
            return None, None
        (status, uid) = self._mfrc522.MFRC522_Anticoll()
        if status != self._mfrc522.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self._mfrc522.MFRC522_SelectTag(uid)
        status = self._mfrc522.MFRC522_Auth(self._mfrc522.PICC_AUTHENT1A,
                                            trailer, self._key, uid)
        data = []
        text_read = ''
        if status == self._mfrc522.MI_OK:
            for block_num in blocks:
                block = self._mfrc522.MFRC522_Read(block_num)
                if block:
                    data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
        self._mfrc522.MFRC522_StopCrypto1()
        return id, text_read

    def write(self, text, trailer=11, blocks=(8, 9, 10)):
        id, text_in = self.write_no_block(
            text, trailer=trailer, blocks=blocks)
        while not id:
            id, text_in = self.write_no_block(
                text, trailer=trailer, blocks=blocks)
        return id, text_in

    def write_no_block(self, text, trailer=11, blocks=(8, 9, 10)):
        (status, TagType) = self._mfrc522.MFRC522_Request(
            self._mfrc522.PICC_REQIDL)
        if status != self._mfrc522.MI_OK:
            return None, None
        (status, uid) = self._mfrc522.MFRC522_Anticoll()
        if status != self._mfrc522.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self._mfrc522.MFRC522_SelectTag(uid)
        status = self._mfrc522.MFRC522_Auth(
            self._mfrc522.PICC_AUTHENT1A, trailer, self._key, uid)
        self._mfrc522.MFRC522_Read(trailer)
        if status == self._mfrc522.MI_OK:
            data = bytearray()
            data.extend(bytearray(text.ljust(len(blocks) * 16).encode('ascii')))
            i = 0
            for block_num in blocks:
                self._mfrc522.MFRC522_Write(block_num,
                                            data[(i * 16):(i + 1) * 16])
                i += 1
        self._mfrc522.MFRC522_StopCrypto1()
        return id, text[0:(len(blocks) * 16)]

    def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n
