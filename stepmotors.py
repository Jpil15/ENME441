import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# --- Shift register pins (change if needed) ---
DATA_PIN  = 17   # SER / DS
CLOCK_PIN = 27   # SRCLK / SH_CP
LATCH_PIN = 22   # RCLK / ST_CP

GPIO.setup(DATA_PIN,  GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(LATCH_PIN, GPIO.OUT)

GPIO.output(DATA_PIN,  0)
GPIO.output(CLOCK_PIN, 0)
GPIO.output(LATCH_PIN, 0)

# --- Stepper half-step sequence as 4 low bits: Q0=IN1, Q1=IN2, Q2=IN3, Q3=IN4 ---
# Same pattern as before: [IN1, IN2, IN3, IN4]
sequence_bits = [
    0b0001,  # IN1
    0b0011,  # IN1+IN2
    0b0010,  # IN2
    0b0110,  # IN2+IN3
    0b0100,  # IN3
    0b1100,  # IN3+IN4
    0b1000,  # IN4
    0b1001   # IN4+IN1
]

current_step = 0  # index into sequence_bits


def shift_out(byte):
    """
    Send one 8-bit value to the 74HC595.
    We send LSB first so bit0 -> Q0, bit1 -> Q1, etc.
    """
    GPIO.output(LATCH_PIN, 0)  # begin update (latch low)

    for i in range(8):         # 8 bits
        bit = (byte >> i) & 0x01  # LSB first

        GPIO.output(CLOCK_PIN, 0)
        GPIO.output(DATA_PIN, bit)
        GPIO.output(CLOCK_PIN, 1)  # data captured on rising edge

    GPIO.output(LATCH_PIN, 1)  # output new data on Q0..Q7


def step(direction=1, delay=0.002):
    """
    direction = +1 → CW
    direction = -1 → CCW
    """
    global current_step

    if direction not in (1, -1):
        raise ValueError("Direction must be +1 or -1")

    # advance index and wrap around
    current_step = (current_step + direction) % len(sequence_bits)

    # get bit pattern for this microstep, send to shift register
    pattern = sequence_bits[current_step]
    shift_out(pattern)

    time.sleep(delay)


try:
    print("Spinning CW via 74HC595... Ctrl+C to stop")
    while True:
        step(+1)      # change to -1 for CCW

except KeyboardInterrupt:
    GPIO.cleanup()
