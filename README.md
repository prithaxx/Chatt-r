## Table of Contents

The files that are needed for the Part 1 are:
- `server.py` : runs the chat server
- `webserver.py` : runs the web server
- `script.js` : web client
- `client.py` : client that uses terminal
- `index.html` : frontend

### To Host the Chat Server
Run the following command in your terminal to host the chat server.
```
python server.py
```

### To Host the Webserver
Run the following code in your terminal to host your webserver.
```
python webserver.py
```

### Web Client Connections
To connect a client to the webserver, follow these steps:

1. Open a **New Window** on **Google Chrome**.
2. Write the following in your broswer window. The port number is **8211**
``` markdown
http://localhost:8211
```

### Terminal Client Connections

Terminal clients can join the server in two ways. To run the client code please follow the structure of the following command.
```
python client.py localhost
```

### To Run with Telnet or Netcat
Another way in which client can join the server is with `telnet` or `nc`. 
```
telnet localhost 8210
```
OR,
```
nc localhost 8210
```

### How to Disconnect client from Server
- **Web client:** To logout from the chat, you need to click on the `Logout` Button on the chat window. Closing the browser would not sign out the client as your saved cookies will identify you the next time you open a browser.

- **Terminal client:** There are two ways in you can disconnect a thin client from the server. You can either enter `quit` when you want to exit from the chat or you can hit `Ctrl+C`.

### How to Stop the Server or Webserver
To stop the server or the webserver you have to hit `Ctrl+C` from your keyboard.
