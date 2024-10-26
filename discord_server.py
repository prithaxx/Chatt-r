import socket
import sys
import select
import traceback
import os
import json
import time

HOST = ''
PORT = 8210
CHAT_HISTORY_FILE = 'chat_history.json'
MAX_HISTORY = 50

clients = []
usernames = {}  # Maps each client connection to their username
chat_history = []  # Stores the chat history


# Load chat history from file if it exists
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r') as f:
            try:
                history = json.load(f)
                return history[-MAX_HISTORY:]  # Load the most recent messages
            except json.JSONDecodeError:
                print('Error decoding chat history.')
                return []
    return []


# Save a new message to the chat history and write it to file
def add_message_to_history(username, message):
    timestamp = str(time.time())
    chat_message = {'user': username, 'timestamp': timestamp, 'message': message}
    chat_history.append(chat_message)

    # Write updated chat history to file
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(chat_history[-MAX_HISTORY:], f, indent=1)


# Return the last MAX_HISTORY messages as a JSON string
def get_chat_history():
    return json.dumps(chat_history[-MAX_HISTORY:])


# Load chat history at startup to initialize chat history
chat_history = load_chat_history()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print('Chat server started, waiting for connections...')

    while True:
        try:
            # Prepare the list of sockets to monitor
            inputs = [server_socket] + clients
            readable, _, exceptional = select.select(inputs, [], inputs)

            for client in readable:
                # New client connection
                if client is server_socket:
                    conn, addr = server_socket.accept()
                    print('New connection from', addr)
                    clients.append(conn)
                    conn.sendall(b'Welcome! Please provide your username to start chatting:\n')

                # Existing client message
                else:
                    try:
                        data = client.recv(1024)
                        if data:
                            message = data.decode().strip()

                            # Check for message in format "user: message"
                            if ':' in message:
                                parts = message.split(':', 1)
                                username = parts[0].strip()
                                user_message = parts[1].strip()

                                usernames[client] = username

                                # Broadcast message to all clients
                                timestamp = str(time.time())
                                formatted_message = f'({timestamp}) {username}: {user_message}'
                                for c in clients:
                                    if c in usernames:
                                        c.sendall((formatted_message + '\n').encode())

                                # Save the message to chat history
                                add_message_to_history(username, user_message)
                                client.sendall(b'HTTP/1.1 200 OK\r\n\r\n')  # Send response to webserver

                            elif message == 'get_history':
                                client.sendall(get_chat_history().encode())

                            elif message.lower() == 'quit':
                                print(f"{usernames.get(client, 'Unknown user')} has quit.")
                                clients.remove(client)
                                client.close()

                        else:
                            # Handle disconnection
                            if client in usernames:
                                print(f"{usernames[client]} has disconnected.")
                            clients.remove(client)
                            client.close()

                    except Exception as e:
                        print('Error processing client message:', e)
                        traceback.print_exc()
                        if client in clients:
                            clients.remove(client)
                        client.close()

        except KeyboardInterrupt:
            print('Server is shutting down.')
            sys.exit(0)
        except Exception as e:
            print('Unexpected server error:', e)
            traceback.print_exc()
