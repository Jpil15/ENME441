import RPi.GPIO as GPIO
import time

class ShifterClass:
  def __init__(self, serialPin, clockPin, latchPin):
    self.serialPin = serialPin
    self.clockPin = clockPin
    self.latchPin = latchPin 
    
  GPIO.setmode(GPIO.BCM)
  
  def __ping(self, p):
    GPIO.output(p,1)
    time.sleep(0)
    GPIO.output(p,0)
  
  def shiftByte(self, b):
    for i in range(8):
      GPIO.output(self.serialPin, b & (1<<i))
      self.__ping(self.clockPin)
    self.__ping(self.latchPin)
