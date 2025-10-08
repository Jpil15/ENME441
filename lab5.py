import RPi.GPIO as GPIO
import time
import math



p = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(p, GPIO.OUT) 


pwm = GPIO.PWM(p, 500)

f = 0.2


try: 
	while True: 
		t = time.time()
		brightness = (math.sin(2 * math.pi * f * t))**2
		duty = brightness * 100
		pwm.start(duty)
		pwm.ChangeDutyCycle(duty)


except KeyboardInterrupt: 
	print('\nExiting')
	pass


pwm.stop()
GPIO.cleanup()
