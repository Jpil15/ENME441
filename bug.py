# bug.py
import RPi.GPIO as GPIO
import time
import random
import threading
from shifter import Shifter

GPIO.setmode(GPIO.BCM)

class Bug:
    def __init__(self, serialPin, clockPin, latchPin,
                 timestep=0.1, x=3, isWrapOn=True, active_low=False):
        """
        timestep:  time step (s)
        x:         current active LED position (0..7)
        isWrapOn:  if True, wrap around edges; else clamp at edges
        active_low: set True if your LEDs light on LOW (invert output)
        """
        self.timestep = float(timestep)
        self.x = max(0, min(7, int(x)))
        self.isWrapOn = bool(isWrapOn)

        # private shifter (composition)
        self.__shifter = Shifter(serialPin, clockPin, latchPin)

        # internals
        self.__active_low = bool(active_low)
        self.__running = False
        self.__thread = None

    # ---------- helpers ----------
    def __one_hot_byte(self):
        b = 1 << self.x
        return (~b & 0xFF) if self.__active_low else b

    def __step_once(self):
        step = random.choice((-1, 1))
        if self.isWrapOn:
            self.x = (self.x + step) % 8
        else:
            self.x = max(0, min(7, self.x + step))

    # ---------- public API ----------
    def start(self):
        """Start changing the LED position at the current speed."""
        if self.__running:
            return
        self.__running = True

        def _loop():
            try:
                while self.__running:
                    self.__shifter.shiftByte(self.__one_hot_byte())
                    self.__step_once()
                    time.sleep(self.timestep)
            finally:
                # ensure LED off if loop exits unexpectedly
                self.__shifter.shiftByte(0xFF if self.__active_low else 0x00)

        self.__thread = threading.Thread(target=_loop, daemon=True)
        self.__thread.start()

    def stop(self):
        """Stop changing the LED position and turn the LED bar off."""
        self.__running = False
        if self.__thread is not None:
            self.__thread.join(timeout=1.0)
            self.__thread = None
        # off
        self.__shifter.shiftByte(0xFF if self.__active_low else 0x00)
        self.__shifter.cleanup()

    def shutdown(self):
        self.stop()
        # make sure your Shifter has a cleanup() that calls GPIO.cleanup()
        self._Bug__shifter.cleanup()

# Example usage (run this file directly to test):
if __name__ == "__main__":
    DATA_PIN, CLOCK_PIN, LATCH_PIN = 23, 25, 24   # BCM numbering
    bug = Bug(DATA_PIN, CLOCK_PIN, LATCH_PIN, timestep=0.05, x=3, isWrapOn=True)
    try:
        bug.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
            bug.shutdown()




