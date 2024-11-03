import socket
import threading
import json
import os

HOST = ''
PORT = 8211
SERVER_HOST = ''
SERVER_PORT = 8212

def connect_server(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:
            web_socket.connect((SERVER_HOST, SERVER_PORT))
            web_socket.sendall(message.encode())
            response = web_socket.recv(1024).decode()
            return response
    except Exception as e:
        print('Error connecting to chat server:', e)
        return None


def serve_static_file(conn, request):
    headers = "HTTP/1.1 200 OK\r\n"
    file_path = None

    if request.startswith("GET / "):
        file_path = "index.html"
        headers += "Content-Type: text/html\r\n"
    elif request.startswith("GET /webfiles/script.js "):
        file_path = "script.js"
        headers += "Content-Type: application/javascript\r\n"

    elif request.startswith("GET /"):
        requested_path = request.split(" ")[1].lstrip('/')
        file_path = os.path.join("../files", requested_path)

        if file_path.endswith(".html"):
            headers += "Content-Type: text/html\r\n"
        elif file_path.endswith((".jpeg", ".jpg")):
            headers += "Content-Type: image/jpeg\r\n"
        elif file_path.endswith(".png"):
            headers += "Content-Type: image/png\r\n"
        else:
            headers = "HTTP/1.1 415 Unsupported Media Type\r\n"
            response = headers + "\r\nUnsupported file type"
            conn.send(response.encode())
            conn.close()
            return

    if file_path is None:
        headers = "HTTP/1.1 404 Not Found\r\n"
        response = headers + "\r\nFile not found"
        conn.send(response.encode())
        conn.close()
        return

    try:
        with open(file_path, "rb") as f:
            response = headers + "\r\n"
            conn.send(response.encode())
            conn.sendfile(f)
    except FileNotFoundError:
        headers = "HTTP/1.1 404 Not Found\r\n"
        response = headers + "\r\nFile not found"
        conn.send(response.encode())

    conn.close()


def handle_api(conn, request):
    if request.startswith('POST /api/login'):
        headers, body = request.split('\r\n\r\n', 1)
        try:
            data = json.loads(body)
            username = data.get('user')
            if username:
                session_id = username
                headers = (
                    'HTTP/1.1 200 OK\r\n'
                    'Set-Cookie: session_id={}; Path=/; Expires=Tue, 19 Jan 2038 03:14:07 GMT; HttpOnly\r\n'
                    '\r\n'.format(session_id)
                )
                conn.send(headers.encode())
            else:
                conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        except json.JSONDecodeError:
            conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

    if request.startswith('GET /api/login'):
        if 'Cookie: session_id=' in request:
            session_id = request.split("Cookie: session_id=")[1].split()[0]
            body = json.dumps({'user':session_id})
            headers = (
                    'HTTP/1.1 200 OK\r\n'
                    'Set-Cookie: session_id={}; Path=/; Expires=Tue, 19 Jan 2038 03:14:07 GMT; HttpOnly\r\n\r\n'.format(session_id)
            )
            conn.send(headers.encode() + body.encode())
        else:
            conn.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')

    elif request.startswith('POST /api/messages'):
        if 'Cookie: session_id=' in request:
            headers, body = request.split('\r\n\r\n', 1)
            try:
                data = json.loads(body)
                message = data.get('message')
                user = headers.split("Cookie: session_id=")[1].split()[0]
                if user and message:
                    response = connect_server(f'post_message:{user}:{message}')
                    if response:
                        conn.send(b'HTTP/1.1 200 OK\r\n\r\n')
                    else:
                        conn.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
                else:
                    conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
            except json.JSONDecodeError:
                conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        else:
            conn.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')

    elif request.startswith('GET /api/messages ') and 'timestamp=' not in request:
        if 'Cookie: session_id=' in request:
            response = connect_server('get_history')
            if response:
                headers = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'
                conn.send(headers.encode() + response.encode())
            else:
                conn.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
        else:
            conn.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')

    elif request.startswith('GET /api/messages?timestamp='):
        if 'Cookie: session_id=' in request:
            timestamp = request.split("timestamp=")[1].split()[0]
            response = connect_server('get_message:' + timestamp)
            if response:
                headers = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'
                conn.send(headers.encode() + response.encode())
            else:
                conn.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
        else:
            conn.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')

    elif request.startswith('DELETE /api/login'):
        if 'Cookie: session_id=' in request:
            response = connect_server('quit')
            if response:
                conn.send(response.encode())
            else:
                conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        else:
            conn.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')

    else:
        conn.send(b'HTTP/1.1 404 Not Found\r\n\r\n')


def handle_client(conn):
    request = conn.recv(1024).decode()
    if request.startswith('GET /api') or request.startswith('POST /api') or request.startswith('DELETE /api'):
        handle_api(conn, request)
    else:
        serve_static_file(conn, request)
    conn.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print('Web server running on port 8211')
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()
