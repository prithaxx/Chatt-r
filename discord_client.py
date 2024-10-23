import socket
import sys
import select

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " <server_host>")
    sys.exit(1)

HOST = sys.argv[1]
PORT = 8210

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        message = ''

        while True:
            readable, writable, exceptional = select.select([sys.stdin, s], [], [])

            for source in readable:
                if source is s:
                    data = s.recv(1024)
                    if not data:
                        print('Disconnected from server')
                        sys.exit(0)

                    # Bring curson to the beginning of the current line and clear the line
                    sys.stdout.write('\r\033[K')
                    print('\r' + data.decode().strip())
                    
                    # Show prompt again after receiving message
                    sys.stdout.write('You: ')
                    sys.stdout.flush()

                else:
                    message = input()
                    s.sendall(message.encode())
                    message = ''

    except KeyboardInterrupt:
        print('\nClient is shutting down')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()