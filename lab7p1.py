import socket
import sys
import signal
import RPi.GPIO as GPIO
from urllib.parse import unquote_plus

HOST = ''          # bind to all interfaces (0.0.0.0)
PORT = 8080        # non-privileged port per lecture guidance
FREQ_HZ = 1000     # PWM frequency; 500–1000 Hz avoids visible flicker

# ===== GPIO / PWM setup =====
GPIO.setmode(GPIO.BCM)
LED_PINS = [17, 27, 22]              # keep your wiring
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
PWMS = [GPIO.PWM(p, FREQ_HZ) for p in LED_PINS]
for p in PWMS:
    p.start(0)

# Track current brightness (0..100)
levels = [0, 0, 0]

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def set_led(idx, duty):
    duty = clamp(duty, 0, 100)
    levels[idx] = duty
    PWMS[idx].ChangeDutyCycle(duty)

def cleanup_and_exit(*_):
    for p in PWMS:
        try:
            p.stop()
        except Exception:
            pass
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)


def html_page():

    return f"""\
<html>
  <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 24px;">
    <h2>ENME 441 — Lab 7</h2>
    <p>Use the form to select an LED and set its brightness (0–100%). Uses POST to modify device state.</p>

    <h3>Current Brightness</h3>
    <ul>
      <li>LED 1 (GPIO {LED_PINS[0]}): {levels[0]}%</li>
      <li>LED 2 (GPIO {LED_PINS[1]}): {levels[1]}%</li>
      <li>LED 3 (GPIO {LED_PINS[2]}): {levels[2]}%</li>
    </ul>

    <hr>
    <h3>Set LED Brightness</h3>
    <form action="/" method="POST">
      <div>
        <label><input type="radio" name="led" value="1" required> LED 1</label><br>
        <label><input type="radio" name="led" value="2"> LED 2</label><br>
        <label><input type="radio" name="led" value="3"> LED 3</label><br>
      </div>
      <div style="margin-top: 8px;">
        <label>Brightness: <input type="range" name="brightness" min="0" max="100" value="50"></label>
      </div>
      <div style="margin-top: 8px;">
        <input type="submit" value="Set Brightness">
      </div>
    </form>

    <hr>
  </body>
</html>
"""

def send_http(conn, body_html, status_code=200, status_text="OK"):
    head  = f"HTTP/1.1 {status_code} {status_text}\r\n"
    head += "Content-Type: text/html; charset=utf-8\r\n"
    head += "Connection: close\r\n"
    head += "\r\n"
    resp = head + body_html
    conn.sendall(resp.encode("utf-8"))

def parse_headers_and_body(request_bytes):
    sep = request_bytes.find(b"\r\n\r\n")
    if sep == -1:
        
        return None, {}, b"", sep
    header_part = request_bytes[:sep].decode("iso-8859-1", errors="replace")
    body = request_bytes[sep+4:]

    # First line
    lines = header_part.split("\r\n")
    start_line = lines[0] if lines else ""
    # Headers
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return start_line, headers, body, sep

def read_full_request(conn):
    
    chunks = []
    conn.settimeout(2.0)
    try:
        # Read initial bytes (headers + maybe some body)
        first = conn.recv(4096)
        if not first:
            return b""
        chunks.append(first)

    
        start_line, headers, body, sep = parse_headers_and_body(first)
        if sep == -1:
            # Keep reading 
            while True:
                more = conn.recv(4096)
                if not more:
                    break
                chunks.append(more)
                all_ = b"".join(chunks)
                start_line, headers, body, sep = parse_headers_and_body(all_)
                if sep != -1:
                    break

        # If POST with Content-Length, ensure full body is read
        all_ = b"".join(chunks)
        start_line, headers, body, sep = parse_headers_and_body(all_)
        if start_line and "content-length" in headers:
            need = int(headers["content-length"])
            have = len(body)
            while have < need:
                more = conn.recv(4096)
                if not more:
                    break
                chunks.append(more)
                all_ = b"".join(chunks)
                # Recompute body portion after appending
                _, _, body, _ = parse_headers_and_body(all_)
                have = len(body)
        return b"".join(chunks)
    except socket.timeout:
        return b""
    except Exception:
        return b""

def parse_post_form(body_bytes):

    data = {}
    try:
        text = body_bytes.decode("utf-8", errors="replace")
        # Split pairs
        for pair in text.split("&"):
            if not pair:
                continue
            if "=" in pair:
                k, v = pair.split("=", 1)
                k = unquote_plus(k)
                v = unquote_plus(v)
                data[k] = v
            else:
                data[unquote_plus(pair)] = ""
    except Exception:
        pass
    return data

# ===== Main server loop =====

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)
        print(f"Listening on http://0.0.0.0:{PORT}")

        while True:
            conn, addr = srv.accept()
            with conn:
                req_raw = read_full_request(conn)
                if not req_raw:
                    # No valid request; just close
                    continue

                # Parse request line and headers again
                start_line, headers, body, _ = parse_headers_and_body(req_raw)
                method = ""
                path = "/"
                if start_line:
                    parts = start_line.split()
                    if len(parts) >= 2:
                        method, path = parts[0], parts[1]

                # Handle POST to modify LED state
                if method.upper() == "POST" and path == "/":
                    form = parse_post_form(body)
                
                    try:
                        led_idx = int(form.get("led", "0")) - 1
                        duty = int(form.get("brightness", "0"))
                        if led_idx in (0, 1, 2):
                            set_led(led_idx, duty)
                    except ValueError:
                        # Ignore bad input; just re-serve page
                        pass
                    # Serve updated page
                    send_http(conn, html_page(), 200, "OK")

                # Serve form page for GET
                elif method.upper() == "GET" and path.startswith("/"):
                    send_http(conn, html_page(), 200, "OK")

                else:
                    # Not found
                    send_http(conn, "<html><body>Not Found</body></html>", 404, "Not Found")

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup_and_exit()

