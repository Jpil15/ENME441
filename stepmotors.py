import RPi.GPIO as GPIO
import time

# Use BCM numbering
GPIO.setmode(GPIO.BCM)

# Define pins
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22
pins = [IN1, IN2, IN3, IN4]

# Setup pins
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Half-step sequence
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

def step(dir=1, delay=0.005):
    """
    dir = +1 → CW
    dir = -1 → CCW
    """
    if dir not in (1, -1):
        raise ValueError("Direction must be +1 or -1")

    # Choose order based on direction
    seq = sequence if dir == 1 else reversed(sequence)

    for pattern in seq:
        for pin, state in zip(pins, pattern):
            GPIO.output(pin, state)
        time.sleep(delay)

try:
    print("CW then CCW… Ctrl+C to stop")
    while True:
        step(+1)   # one full sequence CW
        step(-1)   # one full sequence CCW

except KeyboardInterrupt:
    GPIO.cleanup()
