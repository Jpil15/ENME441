import socket
import sys
import signal
import json
from urllib.parse import unquote_plus
import RPi.GPIO as GPIO

HOST = ''           
PORT = 8080         
FREQ_HZ = 1000      

#GPIO / PWM setup
GPIO.setmode(GPIO.BCM)
LED_PINS = [17, 27, 22]   # keep your wiring
for p in LED_PINS:
    GPIO.setup(p, GPIO.OUT)
PWMS = [GPIO.PWM(p, FREQ_HZ) for p in LED_PINS]
for p in PWMS:
    p.start(0)

levels = [0, 0, 0]  # brightness 0..100

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def set_led(idx, duty):
    duty = clamp(int(duty), 0, 100)
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

# HTML and JavaScript
def html_page():
    return f"""\
<html>
  <head>
    <meta charset="utf-8">
    <title>ENME 441 — Lab 7 (Problem 2)</title>
    <style>
      body {{ font-family: Arial, sans-serif; max-width: 720px; margin: 24px; }}
      .row {{ display: grid; grid-template-columns: 120px 1fr 60px; gap: 12px; align-items: center; margin: 10px 0; }}
      input[type=range] {{ width: 100%; }}
      .card {{ border: 2px solid #ddd; border-radius: 10px; padding: 16px; }}
      .muted {{ color: #555; }}
    </style>
  </head>
  <body>
    <h2>ENME 441 — Lab 7: LED PWM Control (Problem 2)</h2>
    <p class="muted">
      

    <div class="card">
      <div class="row">
        <div>LED 1 (GPIO {LED_PINS[0]})</div>
        <input id="s1" type="range" min="0" max="100" value="{levels[0]}" oninput="send(0, this.value)">
        <div><span id="v1">{levels[0]}</span>%</div>
      </div>
      <div class="row">
        <div>LED 2 (GPIO {LED_PINS[1]})</div>
        <input id="s2" type="range" min="0" max="100" value="{levels[1]}" oninput="send(1, this.value)">
        <div><span id="v2">{levels[1]}</span>%</div>
      </div>
      <div class="row">
        <div>LED 3 (GPIO {LED_PINS[2]})</div>
        <input id="s3" type="range" min="0" max="100" value="{levels[2]}" oninput="send(2, this.value)">
        <div><span id="v3">{levels[2]}</span>%</div>
      </div>
    </div>


    <script>
      // Simple debounce so we don't spam the server while sliding quickly
      let t = null;
      function send(idx, val) {{
        document.getElementById('v' + (idx+1)).textContent = val; // optimistic UI
        if (t) clearTimeout(t);
        t = setTimeout(() => {{
          const body = 'led=' + encodeURIComponent(idx) + '&brightness=' + encodeURIComponent(val);
          fetch('/', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
            body
          }})
          .then(r => r.json())
          .then(data => {{
            // authoritative update from server
            if (Array.isArray(data.levels) && data.levels.length === 3) {{
              document.getElementById('v1').textContent = data.levels[0];
              document.getElementById('v2').textContent = data.levels[1];
              document.getElementById('v3').textContent = data.levels[2];
            }}
          }})
          .catch(_ => {{ /* ignore for quick lab demo */ }});
        }}, 80);
      }}
    </script>
  </body>
</html>
"""

#HTTP raw socket
def send_http_html(conn, body_html, code=200, text="OK"):
    head  = f"HTTP/1.1 {code} {text}\r\n"
    head += "Content-Type: text/html; charset=utf-8\r\n"
    head += "Connection: close\r\n"
    head += "\r\n"
    conn.sendall((head + body_html).encode('utf-8'))

def send_http_json(conn, obj, code=200, text="OK"):
    payload = json.dumps(obj)
    head  = f"HTTP/1.1 {code} {text}\r\n"
    head += "Content-Type: application/json; charset=utf-8\r\n"
    head += "Connection: close\r\n"
    head += "\r\n"
    conn.sendall((head + payload).encode('utf-8'))

def parse_headers_and_body(req_bytes):
    sep = req_bytes.find(b"\r\n\r\n")
    if sep == -1:
        return None, {}, b""
    header_text = req_bytes[:sep].decode("iso-8859-1", errors="replace")
    body = req_bytes[sep+4:]
    lines = header_text.split("\r\n")
    start = lines[0] if lines else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return start, headers, body

def read_full_request(conn):
    chunks = []
    conn.settimeout(2.0)
    try:
        chunk = conn.recv(4096)
        if not chunk:
            return b""
        chunks.append(chunk)
        start, headers, body = parse_headers_and_body(chunk)
        # if headers not complete, continue reading
        while start is None:
            more = conn.recv(4096)
            if not more:
                break
            chunks.append(more)
            start, headers, body = parse_headers_and_body(b"".join(chunks))
        # if POST with content-length, read full body
        if start:
            parts = start.split()
            method = parts[0] if len(parts) >= 1 else ""
            if method.upper() == "POST":
                cl = int(headers.get("content-length", "0") or "0")
                while len(body) < cl:
                    more = conn.recv(4096)
                    if not more:
                        break
                    chunks.append(more)
                    _, _, body = parse_headers_and_body(b"".join(chunks))
        return b"".join(chunks)
    except Exception:
        return b""

def parse_urlencoded(body_bytes):
    out = {}
    try:
        text = body_bytes.decode("utf-8", errors="replace")
        for pair in text.split("&"):
            if not pair: continue
            if "=" in pair:
                k, v = pair.split("=", 1)
                out[unquote_plus(k)] = unquote_plus(v)
            else:
                out[unquote_plus(pair)] = ""
    except Exception:
        pass
    return out

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)
        print(f"Listening on http://0.0.0.0:{PORT}")

        while True:
            conn, addr = srv.accept()
            with conn:
                raw = read_full_request(conn)
                if not raw:
                    continue
                start, headers, body = parse_headers_and_body(raw)
                method, path = "", "/"
                if start:
                    parts = start.split()
                    if len(parts) >= 2:
                        method, path = parts[0], parts[1]

                if method.upper() == "GET" and path == "/":
                    # Serve the full HTML+JS app
                    send_http_html(conn, html_page(), 200, "OK")

                elif method.upper() == "POST" and path == "/":
                    
                    form = parse_urlencoded(body)
                    try:
                        led_idx = int(form.get("led", "0"))
                        duty = int(form.get("brightness", "0"))
                        if led_idx in (0, 1, 2):
                            set_led(led_idx, duty)
                    except ValueError:
                        pass
                    # Return JSON
                    send_http_json(conn, {"levels": levels}, 200, "OK")

                else:
                    send_http_html(conn, "<html><body>Not Found</body></html>", 404, "Not Found")

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup_and_exit()


