import time
import random
from shifter import Shifter

# ====== Pin setup (BCM) — change if your wiring is different ======
DATA_PIN  = 23   # SER
CLOCK_PIN = 25   # SRCLK
LATCH_PIN = 24   # RCLK

# If your LEDs are wired active-LOW, set this to True to invert the bit.
ACTIVE_LOW = False

def one_hot(pos):
    """Return a byte with exactly one LED ON at index pos (0..7), LSB-first."""
    b = 1 << pos
    if ACTIVE_LOW:
        b = (~b) & 0xFF
    return b

def main():
    sh = Shifter(DATA_PIN, CLOCK_PIN, LATCH_PIN)

    try:
        pos = 3  # start somewhere in the middle (0..7)
        dt = 0.05

        while True:
            # Show current LED
            sh.shiftByte(one_hot(pos))

            # Random step: -1 or +1 with equal probability
            step = random.choice((-1, 1))
            pos += step

            # Keep within [0, 7]
            if pos < 0:
                pos = 0
            elif pos > 7:
                pos = 7

            time.sleep(dt)

    except KeyboardInterrupt:
        pass
    finally:
        # Optionally clear the display on exit
        sh.shiftByte(0x00 if not ACTIVE_LOW else 0xFF)
        sh.cleanup()

if __name__ == "__main__":
    main()