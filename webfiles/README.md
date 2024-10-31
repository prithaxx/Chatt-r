# README

This assignment has been done entirely in Python. Please refer to this document to know how to execute the files and about the bugs and the fixes in the code.

## Part 1: Execution
The files that are needed for the execution for Part 1 are ```discord_server.py``` and ```discord_client.py```. 

To host the server run the following command in your terminal. 
```
python discord_server.py
```
After you successfully host the server, the screen will show the port number in which you can connect to if you are using ```telnet``` or ``nc``. This is something it would look like-
```markdown
[dasp4@heron A1]> python discord_server.py
Server started, waiting for connections...
Hosted on port: 9510
```
Please note that the port number is **randomly generated**. If the port is busy, you can simply **re-run the server code** as it will generate a new port number for you.

### To Run the Client Code 
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
The port number is show in the server window as specified above. If your server is running on ```crow.cs.umanitoba.ca``` and if your port is 5000 then run
```
telnet crow.cs.umanitoba.ca 5000
```
You can also use ```nc``` in a very similar way
```
nc crow.cs.umanitoba.ca 5000
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
- The chat history log is no longer persistent. Every time you restart the server, a blank ```chat_history_test.JSON``` file will be created. 
    -  This was implemented because within 5 minutes, a client is able to send thousdands of messages. Storing all these messages will drastically increase the size of the file and reduce the speed of the server. 
    - Every server hosting would be slower than the previous one which would give inaccurate and biased results in the analysis section of this assignment.

---
## Part 2: Bugs & Fixes
