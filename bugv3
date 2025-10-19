# bug.py  — DRIVER that satisfies Step 6 using callbacks + edge detection
# If your Bug class is still in bug.py (class file), this will import it.
# If you moved it to bug_class.py, the fallback import will work.

import time
import RPi.GPIO as GPIO

try:
    # Case 1: class is in bug.py (same name) — typical for your current setup
    from bug import Bug  # <-- will work only if this file is NOT named bug.py too
except Exception:
    # Case 2: you moved the class to bug_class.py (recommended)
    from bug_class import Bug

# ---------- GPIO setup ----------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # use BCM numbering

# Shifter pins (BCM)
DATA_PIN   = 23
CLOCK_PIN  = 25
LATCH_PIN  = 24

# Switch pins (BCM)
S1_PIN     = 13   # on/off
S2_PIN     = 19   # wrap toggle
S3_PIN     = 26   # 3× speed

# Inputs with pull-ups (buttons read LOW when pressed)
GPIO.setup(S1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ---------- Instantiate Bug with defaults (timestep=0.1, x=3, isWrapOn=False) ----------
bug = Bug(DATA_PIN, CLOCK_PIN, LATCH_PIN)

# ---------- Callbacks ----------
def s1_cb(channel):
    """ON while pressed, OFF when released (both edges)."""
    try:
        level = GPIO.input(S1_PIN)
        if level == GPIO.LOW:
            bug.start()
            # print("Bug: START")
        else:
            bug.stop()
            # print("Bug: STOP")
    except Exception:
        # don’t crash callbacks; leave quiet during cleanup/exit
        pass

def s2_cb(channel):
    """Flip wrap mode on ANY state change (press OR release)."""
    try:
        bug.isWrapOn = not bug.isWrapOn
        # print(f"Wrap toggled -> {bug.isWrapOn}")
    except Exception:
        pass

def s3_cb(channel):
    """3× speed while pressed; restore on release."""
    try:
        level = GPIO.input(S3_PIN)
        bug.timestep = (0.1/3.0) if (level == GPIO.LOW) else 0.1
        # print(f"Speed {'FAST' if level == GPIO.LOW else 'NORMAL'}; dt={bug.timestep:.3f}s")
    except Exception:
        pass

# ---------- Event detection (with debounce) ----------
DEBOUNCE_MS = 75  # adjust if your switches bounce more/less

# s1: need BOTH edges so we can start (press) and stop (release)
GPIO.add_event_detect(S1_PIN, GPIO.BOTH, callback=s1_cb, bouncetime=DEBOUNCE_MS)

# s2: any edge should flip wrap
GPIO.add_event_detect(S2_PIN, GPIO.BOTH, callback=s2_cb, bouncetime=DEBOUNCE_MS)

# s3: both edges so we can speed up on press and restore on release
GPIO.add_event_detect(S3_PIN, GPIO.BOTH, callback=s3_cb, bouncetime=DEBOUNCE_MS)

# Initialize outputs according to current switch states
# (Pressing/releasing later will be handled by callbacks.)
s1_cb(S1_PIN)
s3_cb(S3_PIN)

try:
    # Idle forever; callbacks do the work
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    # Remove events first so no callbacks run during shutdown
    for pin in (S1_PIN, S2_PIN, S3_PIN):
        try:
            GPIO.remove_event_detect(pin)
        except Exception:
            pass
    # Graceful shutdown (stop -> LEDs off, then cleanup)
    try:
        # If your Bug class has shutdown(), use it; else stop+cleanup here
        if hasattr(bug, "shutdown"):
            bug.shutdown()
        else:
            bug.stop()
            GPIO.cleanup()
    except Exception:
        GPIO.cleanup()
