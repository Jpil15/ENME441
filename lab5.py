import RPi.GPIO as GPIO
import time
import math



p = 4
p2 = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(p, GPIO.OUT) 
GPIO.setup(p2, GPIO.OUT)


pwm = GPIO.PWM(p, 500)
pwm2 = GPIO.PWM(p2, 500) 

f = 0.2

try: 
	pwm.start(0)
	pwm2.start(100)
	while True: 
		t = time.time()
		brightness = (math.sin(2 * math.pi * f * t))**2
		duty = brightness * 100
		pwm.ChangeDutyCycle(duty)

		brightness2 = (math.sin((2 * math.pi * f * t) - 0.285))**2
		duty2 = brightness2 * 100
		pwm2.ChangeDutyCycle(duty2)


except KeyboardInterrupt: 
	print('\nExiting')
	


pwm.stop()
GPIO.cleanup()

