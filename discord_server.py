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
CHAT_HISTORY = 'chat_history.json'
MAX_HISTORY = 50

clients = []
usernames = {}
chat_history = []

def load_chat_history():
    if os.path.exists(CHAT_HISTORY):
        with open(CHAT_HISTORY, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                print('Error')
        return history[-MAX_HISTORY:]
    return []

def add_message_to_history(user, message):
    chat_message = {'user': user, 'timestamp': timestamp, 'message': message}
    chat_history.append(chat_message) 
    with open(CHAT_HISTORY, 'w') as f:
        json.dump(chat_history, f, indent = 1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    
    print('Server started, waiting for connections...')
    
    while True:
        try:
            inputs = [s] + clients
            readable, writable, exceptional = select.select(inputs, [], inputs)
            
            for client in readable:
                if client is s:
                    conn, addr = s.accept()
                    print('Connected by ', addr)
                    clients.append(conn)
                    
                    conn.sendall(b'Welcome! Please provide your username to start chatting:\n')

                else:
                    try:
                        data = client.recv(1024)
                        if data:
                            message = data.strip().decode()
                            
                            if(message.lower() != 'quit'):
                                timestamp = str(time.time())
                                
                                # If this is a new username -> add it to list, else just append username before their message
                                if client not in usernames:
                                    usernames[client] = message
                                    client.sendall(b'You can start chatting now:\n')
                                    
                                    chat_history = load_chat_history()
                                    for chat in chat_history:
                                        formatted_message = '(' + chat['timestamp'] + ') ' + chat['user'] + ': ' + chat['message'] + '\n'
                                        client.sendall(formatted_message.encode())  
                                        
                                else:
                                    user = usernames[client]
                                    formatted_message = '(' + timestamp + ') ' + user + ': ' + message
                                    for c in clients:
                                        if c in usernames:
                                            c.sendall((formatted_message + '\n').encode())
                                    add_message_to_history(user, message)
                            
                            else:
                                if client in usernames:
                                    print(usernames[client], 'has quit the server.\n')
                                else:
                                    print(client, 'has quit the server.\n')
                                clients.remove(client)
                                client.close()
     
                        else:
                            # if client has quit or keyboard interrupt
                            if client in usernames:
                                print(usernames[client], 'has disconnected.\n')
                                clients.remove(client)
                            client.close()
                        
                    except Exception as e:
                        print('Error: ', e)
                        clients.remove(client)
                        client.close()
                    
        except KeyboardInterrupt:
            print('Server is shutting down.')
            sys.exit(0)
        except Exception as e:
            print('Something went wrong:')
            print(e)
            traceback.print_exc()