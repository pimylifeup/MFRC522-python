# Code by Simon Monk https://github.com/simonmonk/

import logging
import time

from . import MFRC522
import RPi.GPIO as GPIO
import sys


class SimpleMFRC522:
    DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    _log_verbose = None
    _log = None
    _mfrc522 = None
    _key = None

    def __init__(self, key=None, log_verbose=False, pin_mode=GPIO.BOARD):
        self._log = logging.getLogger(self.__class__.__name__)
        self._log_verbose = log_verbose
        if log_verbose:
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)

        if key is None:
            key = SimpleMFRC522.DEFAULT_KEY
        self._key = key
        self._mfrc522 = MFRC522(log_verbose=log_verbose, pin_mode=pin_mode)

    def read_id(self, attempts=sys.maxsize):
        id = self.read_id_no_block()
        tries = 1
        while not id and tries < attempts:
            id = self.read_id_no_block()
            tries += 1
        return id, tries

    def read_id_no_block(self):
        (status, TagType) = self._mfrc522.MFRC522_Request(
            self._mfrc522.PICC_REQIDL)
        if status != self._mfrc522.MI_OK:
            return None
        (status, uid) = self._mfrc522.MFRC522_Anticoll()
        if status != self._mfrc522.MI_OK:
            return None
        return self.uid_to_num(uid)

    def read(self, trailer=11, blocks=(8, 9, 10), attempts=sys.maxsize):
        id, text = self.read_no_block(trailer=trailer, blocks=blocks)
        tries = 1
        while not id and tries < attempts:
            id, text = self.read_no_block(trailer=trailer, blocks=blocks)
            tries += 1
        return id, text, tries

    def log_time(self, action, start):
        end = time.time()
        self._log.debug({
            'action': action,
            'start': f'{start:.5f}',
            'end': f'{end:.5f}',
            'duration': f'{end - start:.5f}',
        })

    def log_error_with_time(self, error, status, start):
        if self._log_verbose:
            end = time.time()
            self._log.error({
                'error': error,
                'status': status,
                'start': f'{start:.5f}',
                'end': f'{end:.5f}',
                'duration': f'{end - start:.5f}',
            })

    def read_no_block(self, trailer=11, blocks=(8, 9, 10)):
        start = time.time()
        status, _ = self._mfrc522.MFRC522_Request(
            self._mfrc522.PICC_REQIDL)
        if status != self._mfrc522.MI_OK:
            self.log_error_with_time('MFRC522_Request', status, start)
            return None, None
        self.log_time('MFRC522_Request', start)

        start = time.time()
        status, uid = self._mfrc522.MFRC522_Anticoll()
        if status != self._mfrc522.MI_OK:
            self.log_error_with_time('MFRC522_Anticoll', status, start)
            return None, None
        self.log_time('MFRC522_Anticoll', start)

        start = time.time()
        status, _ = self._mfrc522.MFRC522_SelectTag(uid)
        if status != self._mfrc522.MI_OK:
            self.log_error_with_time('MFRC522_SelectTag', status, start)
            return None, None
        self.log_time('MFRC522_SelectTag', start)

        start = time.time()
        status = self._mfrc522.MFRC522_Auth(self._mfrc522.PICC_AUTHENT1A,
                                            trailer, self._key, uid)
        if status != self._mfrc522.MI_OK:
            self.log_error_with_time('MFRC522_Auth', status, start)
            return None, None
        self.log_time('MFRC522_Auth', start)

        data = []
        text_read = ''
        if status == self._mfrc522.MI_OK:
            for block_num in blocks:
                start = time.time()
                block = self._mfrc522.MFRC522_Read(block_num)
                self.log_time('MFRC522_Read', start)
                if block:
                    data += block
            if data:
                text_read = ''.join(chr(i) for i in data)

        start = time.time()
        self._mfrc522.MFRC522_StopCrypto1()
        self.log_time('MFRC522_StopCrypto1', start)

        id = self.uid_to_num(uid)
        return id, text_read

    def write(self, text, trailer=11, blocks=(8, 9, 10), attempts=sys.maxsize):
        id, text_out = self.write_no_block(
            text, trailer=trailer, blocks=blocks)
        tries = 1
        while not id and tries < attempts:
            id, text_out = self.write_no_block(
                text, trailer=trailer, blocks=blocks)
            tries += 1
        return id, text_out, tries

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
