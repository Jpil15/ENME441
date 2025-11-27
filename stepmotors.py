import RPi.GPIO as GPIO
import time

# Use BCM mode
GPIO.setmode(GPIO.BCM)

# Define pins
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22
pins = [IN1, IN2, IN3, IN4]

# Setup pins as outputs
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Basic half-step sequence
sequence = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]

def step(delay=0.002):
    for pattern in sequence:
        for pin, state in zip(pins, pattern):
            GPIO.output(pin, state)
        time.sleep(delay)

try:
    print("Spinning... Ctrl+C to stop")
    while True:
        step()

except KeyboardInterrupt:
    GPIO.cleanup()
