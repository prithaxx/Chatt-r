import socket
import sys
import select
import traceback
import os
import json
import time
import random

HOST = ''
PORT = 8210
WEB_SERVER_PORT = 8212
CHAT_HISTORY = 'chat_history.json'
MAX_HISTORY = 10

server_clients = []
web_clients = []
usernames = {}
chat_history = []

def load_chat_history():
    if os.path.exists(CHAT_HISTORY):
        with open(CHAT_HISTORY, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                print('Error in loading chat history')
                return []
        return history[-MAX_HISTORY:]
    return []


def add_message_to_history(user, message, message_id):
    timestamp = str(time.time())
    chat_message = {'user': user, 'timestamp': timestamp, 'message': message, 'message_id': message_id}
    chat_history.append(chat_message)
    with open(CHAT_HISTORY, 'w') as f:
        json.dump(chat_history, f, indent=1)


def delete_message_from_history(user, id):
    chat_history = load_chat_history()
    result = False
    for chat in chat_history:
        if chat.get('message_id') == id and chat.get('user') == user:
            chat_history.remove(chat)
            with open('chat_history.json', 'w') as f:
                json.dump(chat_history, f, indent=1)
            result = True
            break

    return result


def broadcast_message(client_list, message):
    for c in client_list:
        try:
            c.sendall(message.encode())
        except Exception as e:
            print("Failed to send message:", e)
            client_list.remove(c)
            c.close()

def get_messages(timestamp):
    try:
        timestamp = float(timestamp)
        chats = []
        for chat in chat_history:
            if float(chat['timestamp']) > timestamp:
                chats.append(chat)
        return chats
    except ValueError:
        return []


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:
        web_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        web_socket.bind((HOST, WEB_SERVER_PORT))
        web_socket.listen()

        print('Chat server started, waiting for connections...')

        while True:
            try:
                inputs = [server_socket, web_socket] + server_clients + web_clients
                readable, writable, exceptional = select.select(inputs, [], inputs)

                for client in readable:
                    if client is server_socket:
                        conn, addr = server_socket.accept()
                        print('Terminal client connected by', addr)
                        server_clients.append(conn)
                        conn.sendall(b'Welcome! Please provide your username to receive older and incoming chats:\n')

                    elif client is web_socket:
                        conn, addr = web_socket.accept()
                        web_clients.append(conn)

                    else:
                        try:
                            data = client.recv(1024)
                            if data:
                                message = data.strip().decode()

                                # Handle messages from web clients
                                if client in web_clients:
                                    if message.startswith('post_message'):
                                        parts = message.split(':')
                                        user = parts[1].strip()
                                        user_message = parts[2].strip()
                                        message_id = parts[3].strip()

                                        timestamp = str(time.time())
                                        formatted_message = f'({timestamp}) {user}: {user_message}'
                                        add_message_to_history(user, user_message, message_id)

                                        # Broadcast to all clients
                                        broadcast_message(server_clients, formatted_message)
                                        client.sendall(b'HTTP/1.1 200 OK\r\n\r\n')

                                    elif message == 'get_history':
                                        chat_history = load_chat_history()
                                        client.sendall(json.dumps(chat_history).encode())

                                    elif message.startswith('get_message'):
                                        parts = message.split(':', 1)
                                        timestamp = parts[1].strip()
                                        chats = get_messages(timestamp)
                                        client.sendall(json.dumps(chats).encode())
                                    
                                    # BONUS
                                    elif message.startswith('delete_message'):
                                        parts = message.split(':')
                                        user = parts[1].strip()
                                        message_id = parts[2].strip()
                                        result = delete_message_from_history(user, message_id)
                                        if result:
                                            client.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
                                        else:
                                            client.sendall(b'HTTP/1.1 400 Bad Request\r\n\r\n')

                                    elif message == 'quit':
                                        client.sendall(b'HTTP/1.1 200 OK\r\n'
                                                       b'Set-Cookie: session_id=; path=/; '
                                                       b'Expires=Thu, 01 Jan 1970 00:00:00 GMT; '
                                                       b'HttpOnly\r\n'
                                                       b'\r\n')
                                        web_clients.remove(client)
                                        client.close()

                                else:
                                    # Handle messages from terminal clients
                                    if message.lower() != 'quit':
                                        timestamp = str(time.time())
                                        message_id = str(random.randint(0, 999999))

                                        if client not in usernames:
                                            usernames[client] = message
                                            client.sendall(b'You can start chatting now:\n')

                                            # Send chat history to new terminal client
                                            chat_history = load_chat_history()
                                            for chat in chat_history:
                                                formatted_message = f"({chat['timestamp']}) {chat['user']}: {chat['message']}\n"
                                                client.sendall(formatted_message.encode())

                                        else:
                                            user = usernames[client]
                                            formatted_message = f'({timestamp}) {user}: {message}'
                                            broadcast_message(server_clients, formatted_message + '\n')
                                            add_message_to_history(user, message, message_id)

                                    else:
                                        # Handle client quit
                                        if client in usernames:
                                            print(usernames[client], 'has quit the server.\n')
                                            del usernames[client]
                                        elif client in web_clients:
                                            print('A web client has disconnected.\n')
                                            web_clients.remove(client)
                                        server_clients.remove(client)
                                        client.close()

                            else:
                                if client in usernames:
                                    print(usernames[client], 'has disconnected.\n')
                                    del usernames[client]
                                    server_clients.remove(client)
                                elif client in web_clients:
                                    web_clients.remove(client)
                                client.close()

                        except Exception as e:
                            print('Error:', e)
                            if client in server_clients:
                                server_clients.remove(client)
                            elif client in web_clients:
                                web_clients.remove(client)
                            client.close()

            except KeyboardInterrupt:
                print('Server is shutting down.')
                sys.exit(0)
            except Exception as e:
                print('Something went wrong:')
                traceback.print_exc()
