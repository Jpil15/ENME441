import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22
pins = [IN1, IN2, IN3, IN4]

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

current_step = 0  # index into 'sequence'

def step(dir=1, delay=0.002):
    """
    dir = +1 → CW
    dir = -1 → CCW
    """
    global current_step

    if dir not in (1, -1):
        raise ValueError("Direction must be +1 or -1")

    # advance index
    current_step = (current_step + dir) % len(sequence)

    pattern = sequence[current_step]

    # set outputs
    for pin, state in zip(pins, pattern):
        GPIO.output(pin, state)

    time.sleep(delay)

try:
    print("Spinning CW... Ctrl+C to stop")
    while True:
        step(+1)   # keep direction constant for continuous motion

except KeyboardInterrupt:
    GPIO.cleanup()
