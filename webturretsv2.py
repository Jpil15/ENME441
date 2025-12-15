import math
import time
import json
import threading
import http.server
import socketserver
import urllib.parse
import multiprocessing
import requests

from RPi import GPIO
from shifter import Shifter
from stepper_class_shiftregister_multiprocessing import Stepper

PORT = 8000

# =========================
#  GPIO / HARDWARE SETUP
# =========================

GPIO.setmode(GPIO.BCM)

# One shared shift register for both motors
s = Shifter(data=17, clock=27, latch=22)

# Shared lock for multiprocessing-based stepper driver
lock = multiprocessing.Lock()

# Two shared stepper motors
m1 = Stepper(s, lock)   # Motor 1 (e.g. Qa–Qd or Qe–Qh depending on wiring)
m2 = Stepper(s, lock)   # Motor 2

# Optionally zero motors on startup
m1.zero()
m2.zero()


# =========================
#  TURRET PROGRAM LOGIC
# =========================

def runturrets(theID):
  GPIO.setmode(GPIO.BCM)
  # RAW GitHub JSON URL
  #url = "http://192.168.1.254:8000/positions.json"
  #test url
  #url = "https://raw.githubusercontent.com/Jpil15/JacobENME441/refs/heads/main/jsontest.json"
  url = "http://192.168.1.254:8000/positions.json"
  
  # Retrieve and parse JSON
  response = requests.get(url)
  data = response.json()
  
  # ----- Extract Turret Data -----
  turret_ids = []
  turret_r = []
  turret_theta = []
  
  for tid, tinfo in data["turrets"].items():
      turret_ids.append(int(tid))
      turret_r.append(tinfo["r"])
      turret_theta.append(tinfo["theta"])
  
  # ----- Extract Globe Data -----
  globe_r = []
  globe_theta = []
  globe_z = []
  
  for g in data["globes"]:
      globe_r.append(g["r"])
      globe_theta.append(g["theta"])
      globe_z.append(g["z"])
  
  # ----- Print to verify -----
  print("Turret IDs:", turret_ids)
  print("Turret r:", turret_r)
  print("Turret theta:", turret_theta)
  
  print("Globe r:", globe_r)
  print("Globe theta:", globe_theta)
  print("Globe z:", globe_z)
  
  
  
  
  
  class Turrets:
      def __init__(self, ident, rval, theta_deg, zval):
          self.ident = ident
          self.rval = rval 
          self.theta_deg = theta_deg   # store degrees for readability
          self.theta_rad = math.radians(theta_deg)  # also store radians
          self.zval = zval
  
  
  class NewTurrets:
      def __init__(self, ident, x, y, z):
          self.ident = ident
          self.x = x
          self.y = y
          self.z = z
  
  #Turret stuff 
  ident_example = turret_ids
  rval_example = []
  for i in range(len(turret_r)):
      x = turret_r[i] / 100
      rval_example.append(x)
  
  
  theta_example = []
  for i in range(len(turret_theta)):
      x = math.degrees(turret_theta[i])
      theta_example.append(x)
    # degrees
  
  
  #Globe stuff - gonna pretend theyre turrets just at a different z 
  globe_r_example = []
  for i in range(len(globe_r)): 
      x = globe_r[i] / 100
      globe_r_example.append(x) # changing into meters
  
  
  globe_theta_example = []
  for i in range(len(globe_theta)):
      x = math.degrees(globe_theta[i]) 
      globe_theta_example.append(x)
      
  globe_z_example = [] 
  for i in range(len(globe_z)): 
      x = globe_z[i] / 100
      globe_z_example.append(x)
  
  
  
  
  # Create list of polar turrets
  turrets = []
  for i in range(len(ident_example)):
      turret_id = ident_example[i]
      new_turret = Turrets(turret_id, rval_example[i], theta_example[i], 0)
      turrets.append(new_turret)
  
  for g in range(len(globe_theta_example)): 
      globe = Turrets(1000, globe_r_example[g], globe_theta_example[g], globe_z_example[g])
      turrets.append(globe)
  
  # Print polar data
  print("Polar Coordinates of Turrets")
  for obj in turrets:
      print(f"id: {obj.ident}, r: {obj.rval}, theta_deg: {obj.theta_deg}, zval: {obj.zval}")
  
  # Centering our Turret at the origin.
  our_Turret_id = theID
  
  our_theta_deg = None
  for t in turrets:
      if our_Turret_id == t.ident:
          our_theta_deg = t.theta_deg
          break
  
  if our_theta_deg is None:
      raise ValueError("Invalid turret ID")
  
  rotate_deg = 270 - our_theta_deg
  
  rotated_Turrets = []
  for t in turrets:
      new_turret = Turrets(t.ident, t.rval, t.theta_deg + rotate_deg, t.zval)
      rotated_Turrets.append(new_turret)
  
  print("Polar Coordinates of Rotated Turrets")
  for obj in rotated_Turrets:
      print(f"id: {obj.ident}, r: {obj.rval}, theta_deg: {obj.theta_deg}")
  
  # Polar to Rect transformation
  cartesian_turrets = []
  for t in rotated_Turrets:
      # use radians for trig (theta_rad set in __init__)
      x = t.rval * math.cos(t.theta_rad)
      y = t.rval * math.sin(t.theta_rad) + 2
      z = t.zval  
  
      new_turret = NewTurrets(t.ident, x, y, z)
      cartesian_turrets.append(new_turret)
  
  print("Cartesian Turrets")
  for obj in cartesian_turrets:
      print(f"id: {obj.ident}")
      print(f"  x: {round(obj.x, 3)}")
      print(f"  y: {round(obj.y, 3)}")
      print(f"  z: {round(obj.z, 3)}")
  
  
  
  # Convert coordinates of each turret into angles
  xyangles = []
  for obj in cartesian_turrets:
      if obj.y > 0.0:
          angle = math.degrees(math.atan(obj.x / obj.y))
          xyangles.append(angle)
  
  print("raw angles to rotate to")
  print(xyangles)
  
  curr_pos = 0
  
  holder = xyangles
  holder.insert(0, curr_pos)
  print(holder)
  
  # Movement angles between successive turret positions (degrees)
  xymovement = []
  for i in range(len(holder) - 1):
      delta_angle = holder[i + 1] - holder[i]   # in degrees
      xymovement.append(delta_angle)
  
  print("xy angle deltas (deg)")
  print(xymovement)
  
  zholder = []
  for obj in cartesian_turrets: 
      if obj.y > 0.0:
          dis = math.sqrt((obj.x**2) + (obj.y**2))
          angle = math.degrees(math.atan(obj.z / dis))
          zholder.append(angle)
  
  zholder.insert(0, curr_pos)
  
  print(zholder) 
  
  zmovement = []
  
  for i in range(len(zholder) - 1):
      delta_angle = zholder[i + 1] - zholder[i]   # in degrees
      zmovement.append(delta_angle)
  
  
  
  print("z angle delta angles")
  print(zmovement)

  
  GPIO.setup(26, GPIO.OUT)
  def shootlaser():
    GPIO.output(26, GPIO.HIGH)
    time.sleep(2) 
    GPIO.output(26, GPIO.LOW)
  
  
  try:
      # Use motor 1 (m1) to execute the turret rotation sequence
      for obj in range(len(xymovement)): 
          m1.rotate(xymovement[obj])
          print(f"Rotating m1 {xymovement[obj]} degrees")
          m2.rotate(zmovement[obj])
          print(f"Rotating m2 {zmovement[obj]} degrees")
          time.sleep(0.2)
          shootlaser()
        
          

    
   #   for delta in xymovement:
     #     print(f"Rotating motor 1 by {delta} degrees")
       #   m1.rotate(delta)
     #     m2.rotate(delta)
      #    time.sleep(0.1)   # small pause between commands
  
      
      while True:
          pass
  
  except KeyboardInterrupt:
      print("\nStopped by user")
      GPIO.cleanup()
  except Exception as e:
      print(e)
      GPIO.cleanup()    
      time.sleep(0.1)
      print(f"[AUTO] (stub) Finished turret program for turret {theID}")


# =========================
#  MANUAL MOTOR CONTROL
# =========================

def rotate_motor(motor: int, degrees: float) -> None:
    """
    Manually rotate one of the motors by 'degrees' (positive or negative).

    motor = 1 -> m1
    motor = 2 -> m2
    """
    global m1, m2
    print(f"[MANUAL] Rotating Motor {motor} by {degrees} degrees")

    if motor == 1:
        m1.rotate(degrees)
    else:
        m2.rotate(degrees)

    # Small delay to avoid hammering the process
    time.sleep(0.1)


# =========================
#  SIMPLE HTML PAGE
# =========================

PAGE = f"""\
<!DOCTYPE html>
<html>
<head>
    <title>Turret Control</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        h1 {{
            margin-bottom: 0.3em;
        }}
        fieldset {{
            margin-bottom: 1em;
            padding: 1em;
        }}
        button {{
            margin: 0.2em;
            padding: 0.4em 0.8em;
        }}
        input[type="number"] {{
            width: 4em;
        }}
    </style>
</head>
<body>
    <h1>Turret Web Control</h1>

    <fieldset>
        <legend>Run Turret Program</legend>
        <form method="POST" action="/run">
            <label for="tid">Turret ID:</label>
            <input type="number" id="tid" name="tid" min="1" required>
            <button type="submit">Run Turret Program</button>
        </form>
    </fieldset>

    <fieldset>
        <legend>Manual Rotation</legend>

        <form method="POST" action="/move">
            <input type="hidden" name="motor" value="1">
            <label>Motor 1 degrees:</label>
            <input type="number" name="deg" step="1" value="10">
            <button type="submit">Rotate Motor 1</button>
        </form>

        <form method="POST" action="/move">
            <input type="hidden" name="motor" value="2">
            <label>Motor 2 degrees:</label>
            <input type="number" name="deg" step="1" value="10">
            <button type="submit">Rotate Motor 2</button>
        </form>
    </fieldset>
</body>
</html>
"""


# =========================
#  HTTP HANDLER
# =========================

class Handler(http.server.BaseHTTPRequestHandler):

    def send_html(self, html: str) -> None:
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        # Always show the main page
        self.send_html(PAGE)

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        params = urllib.parse.parse_qs(body)

        # ---- Run main turret program ----
        if self.path == "/run":
            try:
                tid = int(params["tid"][0])
            except (KeyError, ValueError, IndexError):
                print("[SERVER] Invalid or missing turret ID")
                return self.send_html(PAGE)

            def run_motor_program():
                print(f"[SERVER] Starting AUTO turret program with ID {tid}")
                global theID
                theID = tid
                runturrets(tid)
                print(f"[SERVER] AUTO turret program finished for ID {tid}")

            threading.Thread(target=run_motor_program, daemon=True).start()
            return self.send_html(PAGE)

        # ---- Manual motor control ----
        if self.path == "/move":
            try:
                motor = int(params["motor"][0])
                deg = float(params["deg"][0])
            except (KeyError, ValueError, IndexError):
                print("[SERVER] Invalid manual move parameters")
                return self.send_html(PAGE)

            rotate_motor(motor, deg)
            return self.send_html(PAGE)

        # Fallback
        self.send_html(PAGE)


# =========================
#  MAIN SERVER LOOP
# =========================

def main():
    try:
        with socketserver.TCPServer(("", PORT), Handler) as server:
            print(f"\nWeb interface running at: http://<your_pi_ip>:{PORT}\n")
            print("Press CTRL+C to stop.")
            server.serve_forever()
    finally:
        # On exit, release GPIO
        GPIO.cleanup()
        print("GPIO cleaned up, exiting.")


if __name__ == "__main__":
    main()
