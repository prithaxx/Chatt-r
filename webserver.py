import socket
import threading
import os

HOST = ''
PORT = 8211

def serve_static_file(conn, request):
    headers = "HTTP/1.1 200 OK\r\n"
    if request.startswith("GET / "):
        file_path = "./static/index.html"
    elif request.startswith("GET /static/script.js "):
        file_path = "./static/script.js"
        headers += "Content-Type: application/javascript\r\n"
    else:
        headers = "HTTP/1.1 404 Not Found\r\n"
        response = headers + "\r\nFile not found"
        conn.send(response.encode())
        conn.close()
        return
    
    with open(file_path, "r") as f:
        response = headers + "\r\n" + f.read()
    conn.send(response.encode())
    conn.close()


def handle_client(conn):
    request = conn.recv(1024).decode()
    if request.startswith("GET"):
        serve_static_file(conn, request)
    conn.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.run()
