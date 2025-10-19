import random as random
import time
import RPi.GPIO as GPIO
from shifter import ShifterClass

class BugClass:
	def __init__(self, __shifter, timestep = 0.1, x = 3, isWrapOn = False):
		self.timestep = timestep
		self.x = x
		self.isWrapOn = isWrapOn
		self.__shifter = __shifter
		self.pattern = [1,2,4,8,16,32,64,128]
	
	def __walk(self):
		rand = random.choice([-1,1])
		self.x = self.x + rand
		if self.isWrapOn == False:
			if self.x < 0:
				self.x = 0
			if self.x > 7:
				self.x = 7
		elif self.isWrapOn == True:
			if self.x < 0:
				self.x = 7
			if self.x > 7:
				self.x = 0
		
		return self.x
		
	def start(self):
		self.__shifter.shiftByte(self.pattern[self.x])
		self.__walk()
		time.sleep(self.timestep)
		
	def stop(self):
		self.__shifter.shiftByte(0)
