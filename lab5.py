import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

p = 4

GPIO.setup(p, GPIO.OUT) 

#GPIO.output(p,1)

pwm = GPIO.PWM(p, 500)
