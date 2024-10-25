var username;

function login(){
    username = document.getElementById("username").value;
    if (!username)
        alert("Username is required to login")
    else{
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/login", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.withCredentials = true;
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200)
                setupChatInterface();
        }
        xhr.send(JSON.stringify({ user: username }));
    }
}

function setupChatInterface() {
    var chatDiv = document.getElementById('chat');
    chatDiv.innerHTML = '';

    var messageInput = document.createElement('input');
    messageInput.type = 'text';
    messageInput.id = 'message';
    messageInput.placeholder = 'Enter your message';

    var sendBtn = document.createElement('button');
    sendBtn.textContent = 'Send';
    sendBtn.onclick = sendMessage;

    chatDiv.appendChild(messageInput);
    chatDiv.appendChild(sendBtn);

    var messagesDiv = document.createElement('div');
    messagesDiv.id = 'messages';
    chatDiv.appendChild(messagesDiv);
}

function sendMessage() {
    var message = document.getElementById('message').value;
    if (!message) {
        alert("Message cannot be empty.");
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/messages", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var messagesDiv = document.getElementById('messages');
            var newMessage = username + ": " + message;
            var messageElement = document.createElement('div');
            messageElement.textContent = newMessage;
            messagesDiv.appendChild(messageElement);

            // Clear the input field after sending the message
            document.getElementById('message').value = '';
        }
    };
    xhr.send(JSON.stringify({ user: username, message: message }));
}

function fetchMessages() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/messages", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var messages = JSON.parse(xhr.responseText);
            var messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = ''; // Clear the div
            messages.forEach(function (msg) {
                messagesDiv.innerHTML += msg.user + ': ' + msg.message + '<br>';
            });
        }
    };
    xhr.send();
}

setInterval(fetchMessages, 3000);

