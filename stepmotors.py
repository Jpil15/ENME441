import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

DATA  = 17
CLOCK = 27
LATCH = 22

GPIO.setup(DATA,  GPIO.OUT)
GPIO.setup(CLOCK, GPIO.OUT)
GPIO.setup(LATCH, GPIO.OUT)

def shift_out(byte):
    GPIO.output(LATCH, 0)
    for i in range(8):
        bit = (byte >> i) & 1
        GPIO.output(CLOCK, 0)
        GPIO.output(DATA, bit)
        GPIO.output(CLOCK, 1)
    GPIO.output(LATCH, 1)

print("Testing Q1… toggling every second")

try:
    while True:
        shift_out(0b00000010)  # ONLY Q1 = HIGH
        time.sleep(1)
        shift_out(0b00000000)  # ALL LOW
        time.sleep(1)

except KeyboardInterrupt:
    shift_out(0)
    GPIO.cleanup()
