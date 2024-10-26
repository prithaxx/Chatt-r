import socket
import threading
import json
import uuid

HOST = ''
PORT = 8211
SERVER_HOST = ''
SERVER_PORT = 8210

def connect_server(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(message.encode())
            response = s.recv(1024).decode()
            return response
    except Exception as e:
        print('Error connecting to chat server: ', e)
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


sessions = {}
def handle_api(csock, request):
    # Request - Login
    if request.startswith('POST /api/login'):
        headers, body = request.split('\r\n\r\n', 1)
        try:
            data = json.loads(body)
            username = data.get('user')
            if username:
                session_id = username
                headers = 'HTTP/1.1 200 OK\r\nSet-Cookie: session_id={}; HttpOnly\r\n\r\n'.format(session_id)
                csock.send(headers.encode())
            else:
                csock.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        except json.JSONDecodeError:
            csock.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

    # Request - Send a message
    elif request.startswith('POST /api/messages'):
        headers, body = request.split('\r\n\r\n', 1)
        try:
            data = json.loads(body)
            user = data.get('user')
            message = data.get('message')
            if user and message:
                chat_request = f"{user}: {message}"
                response = connect_server(chat_request)
                if response:
                    csock.send(b'HTTP/1.1 200 OK\r\n\r\n')
                else:
                    csock.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
            else:
                csock.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
        except json.JSONDecodeError:
            csock.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

    # Request - Get a list of messages
    elif request.startswith('GET /api/messages'):
        response = connect_server('get_history')
        if response:
            headers = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'
            csock.send(headers.encode() + response.encode())
        else:
            csock.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')

    # Request - Invalid
    else:
        csock.send(b'HTTP/1.1 404 Not Found\r\n\r\n')


# Function to handle incoming client requests
def handle_client(conn):
    request = conn.recv(1024).decode()
    if request.startswith('GET /api') or request.startswith('POST /api'):
        handle_api(conn, request)
    else:
        serve_static_file(conn, request)
    conn.close()

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Web server running on port 8211')
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()