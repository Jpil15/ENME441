import RPi.GPIO as GPIO
import time

class Shifter:
    def __init__(self, serialPin, clockPin, latchPin):
        """
        serialPin -> SER (data)
        clockPin  -> SRCLK (shift/clock)
        latchPin  -> RCLK (latch)
        """
        self.serialPin = serialPin
        self.clockPin = clockPin
        self.latchPin = latchPin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.serialPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clockPin, GPIO.OUT, initial=GPIO.LOW)

    def _ping(self, p):
        """Quick HIGH->LOW pulse on pin p."""
        GPIO.output(p, GPIO.HIGH)
        time.sleep(0)  # brief edge
        GPIO.output(p, GPIO.LOW)

    def shiftByte(self, b):
        """Shift out one byte LSB-first, then latch outputs."""
        for i in range(8):
            GPIO.output(self.serialPin, GPIO.HIGH if (b & (1 << i)) else GPIO.LOW)
            self._ping(self.clockPin)
        self._ping(self.latchPin)

    def cleanup(self):
        GPIO.cleanup()


# Quick test (runs only if this file is executed directly)
if __name__ == "__main__":
    dataPin, clockPin, latchPin = 23, 25, 24  # BCM numbering
    sh = Shifter(dataPin, clockPin, latchPin)
    try:
        sh.shiftByte(0b01100110)
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        sh.cleanup()
