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

    # Basic HTTP response
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += "<html><body><h1>Hello World</h1></body></html>"
    conn.sendall(response.encode())
    conn.close()