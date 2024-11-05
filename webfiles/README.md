# README

Part 1 of this Assignment has been completed in **Python** and **JavaScript**. Part 2 of the assignment has been completed with **C** and **Python**. Please refer to this document to know how to execute the files and about the bugs and the fixes in the code.

## Part 1: Execution
The files that are needed for the Part 1 are:
- ```discord_server.py``` : runs the chat server
- ```webserver.py``` : runs the web server
- ```script.js``` : chubby client for assignment 2
- ```discord_client.py``` : thin client from assignment 1
- ```index.html``` : frontend

### To Host the Chat Server
Run the following command in your terminal to host the chat server.
```
python discord_server.py
```
After you successfully hosted the server, the screen will show you that the server has successfully started:
```markdown
[dasp4@hawk webfiles]> python discord_server.py
Chat server started, waiting for connections...
```

### To Host the Webserver
Run the following code in your terminal to host your webserver.
```
python webserver.py
```
After you successfully hosted the webserver, the screen will show you the port number where your client can connect to.
```markdown
[dasp4@hawk webfiles]> python webserver.py 
Web server running on port 8211
```

### Client Connections
To connect a client to the webserver, follow these steps:

1. Open a **New Incognito Window** on **Google Chrome**.

Clients can join the server in two ways. To run the client code please follow the structure of the following command.
```
python discord_client.py <server_name>
```
So for example, if your server is running on ```crow.cs.umanitoba.ca``` then run 
```
python discord_client.py crow.cs.umanitoba.ca
```

### To Run with Telnet or Netcat
Another way in which client can join the server is with ```telnet``` or ```nc```. Log into your ```aviary.cs.umanitoba.ca``` account using ```SSH``` and then follow the structure of the command
```
telnet <server_name> <port_number>
```
The port number is **8210**. If your server is running on ```crow.cs.umanitoba.ca``` then you will run:
```
telnet crow.cs.umanitoba.ca 8210
```
You can also use ```nc``` in a very similar way
```
nc crow.cs.umanitoba.ca 8210
```

### How to Disconnect Client from Server
There are two ways in you can disconnect client from server. You can either enter ```quit``` when you want to exit from the chat or you can hit ```Ctrl+C```.

### How to Stop the Server
To stop the server you have to hit ```Ctrl+C``` from your keyboard.

---
## Part 1: Features
This chat program is persistent and will show upto 50 older messages when a client successfully logs in. The chat history is maintained in ```chat_history.JSON``` file which will be automatically created on your system when you start chatting for the first time. A sample file has been provided with this assignment to showcase the persistence.

Upon connecting a client, the server will ask the client for a username. Until the client provides a valid username, they would not be able to receive any incoming messages or view any older messages from history. This is what this feature would look like:
```markdown
[dasp4@heron A1]> python discord_client.py heron.cs.umanitoba.ca
Welcome! Please provide your username to start chatting:
You: 
```
If you provide a valid username, you will be able to view all older messages.
```markdown
[dasp4@heron A1]> python discord_client.py heron.cs.umanitoba.ca
Welcome! Please provide your username to start chatting:
You: Alice
You can start chatting now:
(1728410292.4039567) bob: hi
(1728410304.888814) frank: hi bob
(1728410308.1316512) bob: hi frank
(1728410317.4825277) bob: meh
(1728410323.6061094) frank: hru????ok
You: 
```
An example of an invalid username would be ```quit```, as the server would assume that the client wants to leave the chat and hence it would disconnect them.
```markdown
[dasp4@heron A1]> python discord_client.py heron.cs.umanitoba.ca
Welcome! Please provide your username to start chatting:
You: quit
Disconnected from server
```
---
## Part 1: Bugs & Fixes
I was able to partially fix the message interlacing problem of the UI. To explain my progress let's assume there there are two clients- Alice and Bob. In the screenshot attached, the left is Alice's chat and the right is Bob's chat. In this image we can see that both of our clients are currently typing.

![Screenshot](./images/overlap_before.png)

Now, Bob hits 'Enter' and sends his message.

![Screenshot](./images/overlap_send.png)

Bob's message is successfully sent to the chat without any overlapping. However, we have lost the message that Alice was typing. This lost message has only vanished from the screen but it is veru much present in our buffer. So if Alice simply hits 'Enter', she would be able to send her previously typed message.

![Screenshot](./images/overlap_buffer.png)

This is because of this part of the code that I wrote in the client program which brings the cursor to the beginning of the current line and then clears the line. 

```markdown
# Bring curson to the beginning of the current line and clear the line
sys.stdout.write('\r\033[K')
print('\r' + data.decode().strip())
```
I tried using the ```curses``` library to fix the overlapping UI but I wasn't able to go much further with that. I have however partially solved this issue so I hope I would be able to get some points for that.

---
## Part 2: Execution
The files that are needed for the execution of Part 2 are ```test_server.py```, ```test_client.py``` (optional) and ```load_test_demo.sh```. 

To host the server run the following command in your terminal.
```
python test_server.py
```
### To Run the Client Code 
Clients can join the server in two ways. You can either manually run the client code using the following command structure:
```
python test_client.py <server_name>
```
So for example, if your server is running on ```crow.cs.umanitoba.ca``` then run 
```
python test_client.py crow.cs.umanitoba.ca
```
### To Connect Multiple Clients with Bash script
Another way in which multiple clients can be created and connected at the same time is by using the ```load_test_demo.sh``` script. 

Before running the script, you might have to give speciall permission access to the script. Please run the following command in your terminal:
```
chmod +x load_test_demo.sh
```
Now you are ready to create clients. This is the structure to run the script
```
./load_test_demo.sh <server_name> <num_clients>
```
So for example, if your server is running on ```crow.cs.umanitoba.ca``` and you want to create 10 clients then run:
```
./load_test_demo.sh crow.cs.umanitoba.ca 10
```
### How to Stop the Server
The server will automatically stop after 5 minutes. All clients will be disconnected when this happens. Once the server stops, it will print out statistics such as:
- Total Number of Messages Sent
- Total Number of Messages Received
- Time Elapsed

To stop the server mnaually, you have to hit ```Ctrl+C``` from your keyboard.

---
## Part 2: Features & Observations
A few modifications was made in ```test_server.py``` to meet the requirements of the assignment:
- The chat history log has been limited to 50 messages. When the server is hosted, the first 50 messages gets written to ```chat_history_test.JSON```, after which he file is cleared and then filled again for incoming messages.
    -  This was implemented because within 5 minutes, a client is able to send thousdands of messages. Storing all these messages will drastically increase the size of the file and reduce the speed of the server. 
    - Every server hosting would be slower than the previous one which would give inaccurate and biased results in the analysis section of this assignment.

- To make a completely non-blocking server, I implemented a message queue using writable. During a BlockingIO Exception, I append the failed messages in a message queue. All failed maessages are appeneded to this message queue so that they can be sent later.  
    - The writable iterates through all the message queue for each client and relays the message to all clients. If the buffer gets full, the message is inserted in the queue again.
```
for client in writable:
    if queue[client]:
        next_message = queue[client].pop(0)
        try:
            bytes_sent = client.send(next_message.encode())
            if bytes_sent < len(next_message):
                queue[client].insert(0, next_message[bytes_sent:])
            else:
                message_sent += 1
                add_message_to_history(usernames[client], next_message)
        except BlockingIOError:
            queue[client].insert(0, next_message)
```

---
## Part 2: Bugs & Fixes
The only inconsistent thing I have noticed in this part of the assignment is the fact that the number of messages varies from client to client. Sometimes I got more sent messages for 50 clients than 5 clients. Althouh the average messages sent is steadily decreasing; my guess behind why this happens would be network traffic.

It is possible that when I ran my test for 5 clients, there were more people connected to that aviary bird than the time I tested for 50 clients. Since, the high volume of messages sent was completely random and not recurring, this is my best bet.