import time
import RPi.GPIO as GPIO
from shifter import ShifterClass
from bug import Bug

serialPin, latchPin, clockPin = 23, 24, 25
onCatch, speedCatch, wrapCatch = 13, 19, 26
onState, wrapState, speedState = False, False, False

shift = Shifter(serialPin, clockPin, latchPin)
bugout = Bug(shift)

GPIO.setmode(GPIO.BCM)
GPIO.setup(serialPin, GPIO.OUT)
GPIO.setup(latchPin, GPIO.OUT, initial = 0)
GPIO.setup(clockPin, GPIO.OUT, initial = 0)

GPIO.setup(onCatch, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(wrapCatch, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(speedCatch, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def onCallback(pin):
	global onState
	onState = not onState
	print(f"on/off toggled to {onState}")

def wrapCallback(pin):
	global wrapState
	wrapState = not wrapState
	print(f"wrap toggled to {wrapState}")

def speedUpCallback(pin):
	global speedState
	speedState = not speedState
	print(f"speed toggled to {speedState}")

def run():
	global bugout, wrapOn, speed, wrapState, speedState, onState, shift
	
	if wrapState == True:
		wrapOn = True
	else:
		wrapOn = False
	if speedState == True:
		speed = 0.03
	else:
		speed = 0.1
		
	bugout.timestep = speed
	bugout.isWrapOn = wrapOn 
	
	if onState == True:
		bugout.start()
	else:
		bugout.stop()

GPIO.add_event_detect(onCatch, GPIO.BOTH, callback = onCallback, bouncetime = 100)
GPIO.add_event_detect(wrapCatch, GPIO.BOTH, callback = wrapCallback, bouncetime = 100)
GPIO.add_event_detect(speedCatch, GPIO.BOTH, callback = speedUpCallback, bouncetime = 100)

try:
	while 1:
		run()
except KeyboardInterrupt:
	print("Exiting")
	bugout.stop()

	GPIO.cleanup()




