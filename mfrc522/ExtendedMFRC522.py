#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# code by Lurkars https://github.com/Lurkars

__name__ = "ExtendedMFRC522"

from . import SimpleMFRC522

class ExtendedMFRC522(SimpleMFRC522):

    def __init__(self, start_section=1, sections=0, blocks_per_section=4, block_size=16, encoding='utf8'):
        self.START_SECTION = start_section
        self.SECTIONS = sections
        self.BLOCKS_PER_SECTIONS = blocks_per_section
        self.DATA_BLOCKS = self.BLOCKS_PER_SECTIONS - 1
        self.BLOCK_SIZE = block_size
        self.ENCODING = encoding
        if self.START_SECTION < 1:
            self.START_SECTION = 1
        super().__init__()

    def read_no_block(self):
        (status, size) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None, None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.READER.MFRC522_SelectTag(uid)
        data = bytearray()
        text_read = ''

        start_section = self.START_SECTION
        if start_section > size:
            start_section = size - 1

        sections = size - start_section
        if self.SECTIONS > 0 and self.SECTIONS <= sections:
            sections = self.SECTIONS

        for section in range(start_section, start_section + sections):
            trailer_block = section * self.BLOCKS_PER_SECTIONS + self.DATA_BLOCKS
            status = self.READER.MFRC522_Auth(
                self.READER.PICC_AUTHENT1A, trailer_block, self.KEY, uid)
            if status == self.READER.MI_OK:
                for i in range(self.DATA_BLOCKS):
                    block_addr = section * self.BLOCKS_PER_SECTIONS + i
                    block = self.READER.MFRC522_Read(block_addr)
                    if block:
                        data.extend(bytearray(block))

                if data:
                    text_read = data.decode(self.ENCODING)
        self.READER.MFRC522_StopCrypto1()
        return id, text_read

    def write_no_block(self, text):
        (status, size) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None, None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.READER.MFRC522_SelectTag(uid)

        start_section = self.START_SECTION
        if start_section > size:
            start_section = size - 1

        sections = size - start_section
        if self.SECTIONS > 0 and self.SECTIONS <= sections:
            sections = self.SECTIONS

        data = text.encode(self.ENCODING)
        data_sections = [data[i:i + self.BLOCK_SIZE * self.DATA_BLOCKS]
                         for i in range(0, len(data), self.BLOCK_SIZE * self.DATA_BLOCKS)]

        for section in range(start_section, start_section + sections):
            trailer_block = section * self.BLOCKS_PER_SECTIONS + self.DATA_BLOCKS
            status = self.READER.MFRC522_Auth(
                self.READER.PICC_AUTHENT1A, trailer_block, self.KEY, uid)
            self.READER.MFRC522_Read(trailer_block)

            section_data = bytearray(self.DATA_BLOCKS * self.BLOCK_SIZE)
            if len(data_sections) > (section - start_section):
                section_data = bytearray(
                    data_sections[section - start_section])
                section_data.extend(
                    bytearray(self.DATA_BLOCKS * self.BLOCK_SIZE - len(section_data)))

            if status == self.READER.MI_OK:
                for i in range(self.DATA_BLOCKS):
                    block_addr = section * self.BLOCKS_PER_SECTIONS + i
                    block_data = section_data[(
                        i*self.BLOCK_SIZE):(i+1)*self.BLOCK_SIZE]
                    self.READER.MFRC522_Write(
                        block_addr, block_data)
        self.READER.MFRC522_StopCrypto1()
        return id, data[0:(len(self.BLOCK_ADDRS) * self.BLOCK_SIZE * sections)].decode(self.ENCODING)
