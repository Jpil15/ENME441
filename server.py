import socket

HOST = ''          # listen on all interfaces
PORT = 8080        # non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print(f"Listening on {PORT}...")

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    print("Request:", request)


    html = """\
    <html>
        <body>
            <h2>LED Control</h2>
            <form action="/" method="POST">
                <input type="radio" name="led" value="1"> LED 1<br>
                <input type="radio" name="led" value="2"> LED 2<br>
                <input type="radio" name="led" value="3"> LED 3<br>
                <input type="range" name="brightness" min="0" max="100" value="50"><br>
                <input type="submit" value="Set Brightness">
            </form>
        </body>
    </html>"""
    

    # Basic HTTP response
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += html
    conn.sendall(response.encode())
    conn.close()
