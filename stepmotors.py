import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# ---- PINS YOU CONNECTED TO THE 74HC595 ----
DATA_PIN  = 17   # SER / DS
CLOCK_PIN = 27   # SH_CP / SRCLK
LATCH_PIN = 22   # ST_CP / RCLK

GPIO.setup(DATA_PIN,  GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(LATCH_PIN, GPIO.OUT)

GPIO.output(DATA_PIN,  0)
GPIO.output(CLOCK_PIN, 0)
GPIO.output(LATCH_PIN, 0)

def shift_out(byte):
    """
    Send one 8-bit value to the 74HC595.
    This version sends LSB first: bit0 -> Q0, bit1 -> Q1, etc.
    """
    GPIO.output(LATCH_PIN, 0)  # latch low: start shifting

    for i in range(8):         # 8 bits
        bit = (byte >> i) & 0x01   # LSB first

        GPIO.output(CLOCK_PIN, 0)
        GPIO.output(DATA_PIN, bit)
        GPIO.output(CLOCK_PIN, 1)  # capture bit on rising edge

    GPIO.output(LATCH_PIN, 1)  # latch high: update outputs

try:
    print("Testing shift register: one coil at a time...")
    # full-step: one coil ON at a time
    test_sequence = [
        0b0001,  # Q0 -> IN1
        0b0010,  # Q1 -> IN2
        0b0100,  # Q2 -> IN3
        0b1000   # Q3 -> IN4
    ]

    while True:
        for pattern in test_sequence:
            shift_out(pattern)
            time.sleep(0.2)   # slow so you can feel each move

except KeyboardInterrupt:
    # turn everything off
    shift_out(0)
    GPIO.cleanup()
