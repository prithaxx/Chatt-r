import socket
import threading
import os
import json
import mimetypes

HOST = ''
PORT = 8211
SERVER_HOST = ''
SERVER_PORT = 8210

# Function to connect to chat server
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
    if request.startswith("GET / ") or request.startswith("GET /"):
        file_path = "./static/index.html"
    else:
        file_path = "." + request.split(" ")[1]

    # Check if file exists
    if os.path.exists(file_path):
        # Detect the file's MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            headers += f"Content-Type: {mime_type}\r\n"
        else:
            headers += "Content-Type: text/plain\r\n"

        with open(file_path, "r") as f:
            response = headers + "\r\n" + f.read()
        conn.send(response.encode())
    else:
        # Send 404 response if file not found
        headers = "HTTP/1.1 404 Not Found\r\n"
        response = headers + "\r\nFile not found"
        conn.send(response.encode())
    
    conn.close()

# Function to handle API requests
def handle_api(csock, request):
    if request.startswith('GET /api/messages'):
        response = connect_server('get_history')
        if response:
            headers = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'
            csock.send(headers.encode() + response.encode())
        else:
            print("Error connecting to chat server.")  # Log connection error
            csock.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')

    elif request.startswith('POST /api/messages'):
        headers, body = request.split('\r\n\r\n', 1)
        print('Body: ', body) # Log the body of the message
        try:
            new_message = json.loads(body)
        except json.JSONDecodeError:
            print("Failed to decode JSON: ", body)  # Log JSON parsing error
            csock.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
            return

        user = new_message.get('user')
        message = new_message.get('message')
        if user and message:
            chat_request = f"{user}: {message}"
            response = connect_server(chat_request)
            csock.send(b'HTTP/1.1 200 OK\r\n\r\n')
        else:
            print("Missing user or message in the request.")  # Log missing fields
            csock.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

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
