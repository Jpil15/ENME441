import RPi.GPIO as GPIO
from time import sleep
import time
import math


GPIO.setmode(GPIO.BCM)

p = 4

GPIO.setup(p, GPIO.OUT) 

#GPIO.output(p,1)

pwm = GPIO.PWM(p, 500)

f = 0.2

try: 
	while True: 
		t = time.time()
		brightness = (math.sin(2 * math.pi * f * t))**2
		duty = brightness * 100
		pwm.ChangeDutyCycle(duty)


except KeyboardInterrupt: 
	pass


pwm.stop()
GPIO.cleanup()
