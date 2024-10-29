import socket
import threading
import json

HOST = ''
PORT = 8211
SERVER_HOST = ''  # Set this to the actual server host
SERVER_PORT = 8212
sessions = {}  # Store client sessions

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


def handle_api(conn, request):
    if request.startswith('POST /api/login'):
        headers, body = request.split('\r\n\r\n', 1)
        try:
            data = json.loads(body)
            username = data.get('user')
            if username:
                session_id = username
                sessions[session_id] = conn
                headers = 'HTTP/1.1 200 OK\r\nSet-Cookie: session_id={}; HttpOnly\r\n\r\n'.format(session_id)
                conn.send(headers.encode())
            else:
                conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        except json.JSONDecodeError:
            conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

    elif request.startswith('POST /api/messages'):
        headers, body = request.split('\r\n\r\n', 1)
        try:
            data = json.loads(body)
            user = data.get('user')
            message = data.get('message')
            if user and message:
                response = connect_server(f'{user}:{message}')
                if response:
                    conn.send(b'HTTP/1.1 200 OK\r\n\r\n')
                else:
                    conn.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
            else:
                conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        except json.JSONDecodeError:
            conn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

    elif request.startswith('GET /api/messages'):
        # ?
        response = connect_server('get_history')
        if response:
            headers = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'
            conn.send(headers.encode() + response.encode())
        else:
            conn.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')

    else:
        conn.send(b'HTTP/1.1 404 Not Found\r\n\r\n')


# Function to handle incoming client requests in new threads
def handle_client(conn):
    request = conn.recv(1024).decode()
    if request.startswith('GET /api') or request.startswith('POST /api') or request.startswith('DELETE /api'):
        handle_api(conn, request)
    else:
        serve_static_file(conn, request)
    conn.close()


# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print('Web server running on port 8211')
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()