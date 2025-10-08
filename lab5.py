import RPi.GPIO as GPIO
import time
import math



p = 4
p2 = 17
p3 = 27
p4 = 22
p5 = 10 
p6 = 9
p7 = 11
p8 = 26
p9 = 19
p10 = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(p, GPIO.OUT) 
GPIO.setup(p2, GPIO.OUT)
GPIO.setup(p3, GPIO.OUT)
GPIO.setup(p4, GPIO.OUT)
GPIO.setup(p5, GPIO.OUT)
GPIO.setup(p6, GPIO.OUT)
GPIO.setup(p7, GPIO.OUT)
GPIO.setup(p8, GPIO.OUT)
GPIO.setup(p9, GPIO.OUT)
GPIO.setup(p10, GPIO.OUT)

button = 21
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

pwm = GPIO.PWM(p, 500)
pwm2 = GPIO.PWM(p2, 500) 
pwm3 = GPIO.PWM(p3, 500)
pwm4 = GPIO.PWM(p4, 500)
pwm5 = GPIO.PWM(p5, 500)
pwm6 = GPIO.PWM(p6, 500)
pwm7 = GPIO.PWM(p7, 500)
pwm8 = GPIO.PWM(p8, 500)
pwm9 = GPIO.PWM(p9, 500)
pwm10 = GPIO.PWM(p10, 500)

f = 0.2

try: 
	pwm.start(0)
	pwm2.start(0)
	pwm3.start(0)
	pwm4.start(0)
	pwm5.start(0)
	pwm6.start(0)
	pwm7.start(0)
	pwm8.start(0)
	pwm9.start(0)
	pwm10.start(0)

	d = 1

	def myCallback(button):
		print("switch direction")
		d = d * (-1)


	gpio.add_event_detect(button, gpio.RISING, callback=myCallback, bouncetime = 100)


	while True: 
		t = time.time()
		brightness = (math.sin(2 * math.pi * f * t * d))**2
		duty = brightness * 100
		pwm.ChangeDutyCycle(duty)

		brightness2 = (math.sin((2 * math.pi * f * t) - 0.285* d))**2
		duty2 = brightness2 * 100
		pwm2.ChangeDutyCycle(duty2)

		brightness3 = (math.sin((2 * math.pi * f * t) - 0.572 * d))**2
		duty3 = brightness3 * 100
		pwm3.ChangeDutyCycle(duty3)

		brightness4 = (math.sin((2 * math.pi * f * t) - 0.857 * d))**2
		duty4 = brightness4 * 100
		pwm4.ChangeDutyCycle(duty4)

		brightness5 = (math.sin((2 * math.pi * f * t) - 1.142 * d))**2
		duty5 = brightness5 * 100
		pwm5.ChangeDutyCycle(duty5)

		brightness6 = (math.sin((2 * math.pi * f * t) - 1.428 * d))**2
		duty6 = brightness6 * 100
		pwm6.ChangeDutyCycle(duty6)

		brightness7 = (math.sin((2 * math.pi * f * t) - 1.713 * d))**2
		duty7 = brightness7 * 100
		pwm7.ChangeDutyCycle(duty7)

		brightness8 = (math.sin((2 * math.pi * f * t) - 1.999))**2
		duty8 = brightness8 * 100
		pwm8.ChangeDutyCycle(duty8)

		brightness9 = (math.sin((2 * math.pi * f * t) - 2.285 * d))**2
		duty9 = brightness9 * 100
		pwm9.ChangeDutyCycle(duty9)

		brightness10 = (math.sin((2 * math.pi * f * t) - 2.57 * d))**2
		duty10 = brightness10 * 100
		pwm10.ChangeDutyCycle(duty10)











except KeyboardInterrupt: 
	print('\nExiting')
	


pwm.stop()
GPIO.cleanup()
