import socket
import threading

HOST = ''
PORT = 8211

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread = threading.thread(target=handle_client, args=(conn))
            thread.run()

