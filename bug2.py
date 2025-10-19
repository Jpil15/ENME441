import time
import RPi.GPIO as GPIO
from bug import bug   # <-- your Bug class from the previous step

# ---------- Use BCM numbering (set once, before any GPIO.setup) ----------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# ---------- Shifter pins (BCM) ----------
DATA_PIN   = 23   # SER
CLOCK_PIN  = 25   # SRCLK
LATCH_PIN  = 24   # RCLK

# ---------- Switch pins (BCM) ----------
S1_PIN     = 13   # on/off switch
S2_PIN     = 19   # wrap toggle (flip on any state change)
S3_PIN     = 26   # speed boost (3× faster while on)

# Inputs with pull-ups so buttons read LOW when pressed
GPIO.setup(S1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ---------- Instantiate Bug with defaults: timestep=0.1, x=3, isWrapOn=False ----------
bug = Bug(DATA_PIN, CLOCK_PIN, LATCH_PIN)

try:
    # Track s2’s previous state to detect toggles (press OR release)
    prev_s2 = GPIO.input(S2_PIN)

    while True:
        # a/b) s1 controls ON/OFF (pressed == LOW)
        if GPIO.input(S1_PIN) == GPIO.LOW:
            bug.start()
        else:
            bug.stop()

        # c) s2 flips wrapping whenever its state changes
        s2_now = GPIO.input(S2_PIN)
        if s2_now != prev_s2:
            bug.isWrapOn = not bug.isWrapOn
        prev_s2 = s2_now

        # d) s3 speeds up by 3× while pressed
        bug.timestep = (0.1 / 3.0) if (GPIO.input(S3_PIN) == GPIO.LOW) else 0.1

        # small poll/debounce delay
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    # stop movement, turn LEDs off, and release GPIO exactly once
    bug.shutdown()

