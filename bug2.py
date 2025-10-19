import time
import RPi.GPIO as GPIO
from bug import Bug   # your Bug class from bug.py (previous step)

# ===== Pin numbers (BCM mode) =====
DATA_PIN   = 23   # SER
CLOCK_PIN  = 25   # SRCLK
LATCH_PIN  = 24   # RCLK

S1_PIN     = 13   # switch 1 (on/off)
S2_PIN     = 19   # switch 2 (wrap toggle)
S3_PIN     = 26   # switch 3 (speed boost)

# ===== Setup =====
GPIO.setmode(GPIO.BCM)
GPIO.setup(S1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ===== Instantiate Bug with defaults =====
bug = Bug(DATA_PIN, CLOCK_PIN, LATCH_PIN)  # timestep=0.1, x=3, wrap=False

# ===== Main loop =====
try:
    prev_s2 = GPIO.input(S2_PIN)  # track previous state for edge detection

    while True:
        # --- S1 controls ON/OFF ---
        if GPIO.input(S1_PIN) == GPIO.LOW:   # pressed
            bug.start()
        else:
            bug.stop()

        # --- S2 toggles wrapping (on state change) ---
        s2_now = GPIO.input(S2_PIN)
        if s2_now != prev_s2:  # edge detected
            bug.isWrapOn = not bug.isWrapOn
        prev_s2 = s2_now

        # --- S3 triples speed if pressed ---
        if GPIO.input(S3_PIN) == GPIO.LOW:
            bug.timestep = 0.1 / 3.0   # 3x faster
        else:
            bug.timestep = 0.1         # back to default

        time.sleep(0.05)  # debounce/poll delay

except KeyboardInterrupt:
    pass
finally:
    bug.stop()
    GPIO.cleanup()