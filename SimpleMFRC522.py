#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Code by Simon Monk https://github.com/simonmonk/


import MFRC522
import RPi.GPIO as GPIO
  
class SimpleMFRC522:

  READER = None;
  
  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  #BLOCK_ADDRS = [8,9,10]
  
  def __init__(self):
    self.READER = MFRC522.MFRC522()
  
  def read(self, authblockaddrs, datablockaddrs):
      id, text = self.read_no_block(authblockaddrs, datablockaddrs)
      while not id:
          id, text = self.read_no_block(authblockaddrs, datablockaddrs)
      return id, text

  def read_id(self):
      id = self.read_id_no_block()
      while not id:
          id = self.read_id_no_block()
      return id

  def read_id_no_block(self):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None
      return self.uid_to_num(uid)
  
  def read_no_block(self, authblockaddrs, datablockaddrs):
    (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
    if status != self.READER.MI_OK:
        return None, None
    (status, uid) = self.READER.MFRC522_Anticoll()
    if status != self.READER.MI_OK:
        return None, None
    id = self.uid_to_num(uid)
    self.READER.MFRC522_SelectTag(uid)
    status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, authblockaddrs, self.KEY, uid)
    data = []
    text_read = ''
    if status == self.READER.MI_OK:
        for block_num in datablockaddrs:
            block = self.READER.MFRC522_Read(block_num) 
            if block:
            		data += block
        if data:
             text_read = ''.join(chr(i) for i in data)
    self.READER.MFRC522_StopCrypto1()
    return id, text_read
    

    
  def write(self, text, authblockaddrs, datablockaddrs):
      id, text_in = self.write_no_block(text, authblockaddrs, datablockaddrs)
      while not id:
          id, text_in = self.write_no_block(text, authblockaddrs, datablockaddrs)
      return id, text_in


  def write_no_block(self, text, authblockaddrs, datablockaddrs):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, authblockaddrs, self.KEY, uid)
      self.READER.MFRC522_Read(authblockaddrs)
      if status == self.READER.MI_OK:
          data = bytearray()
          data.extend(bytearray(text.ljust(len(datablockaddrs) * 16).encode('utf-8')))
          i = 0
          for block_num in datablockaddrs:
            self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
            i += 1
      self.READER.MFRC522_StopCrypto1()
      return id, text[0:(len(datablockaddrs) * 16)]
      
  def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n
