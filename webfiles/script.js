var username;
var last_message_timestamp = 0;
var pollInterval;
var message_id;

window.onload = function() {
    checkLoginStatus();
};

function login(){
    username = document.getElementById("username").value;
    if (!username) {
        alert("Username is required to login");
    } else {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/login", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.withCredentials = true;
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                setupChatInterface();
            }
        };
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
    chatDiv.appendChild(messageInput);

    var sendBtn = document.createElement('button');
    sendBtn.textContent = 'Send';
    sendBtn.onclick = sendMessage;
    chatDiv.appendChild(sendBtn);

    var logoutBtn = document.createElement('button');
    logoutBtn.textContent = 'Logout';
    logoutBtn.onclick = logout;
    chatDiv.appendChild(logoutBtn);

    var messagesDiv = document.createElement('div');
    messagesDiv.id = 'messages';
    chatDiv.appendChild(messagesDiv);

    poll();
}

function createLoginInterface(){
    var chatDiv = document.getElementById('chat');
    chatDiv.innerHTML = '';

    var usernameInput = document.createElement('input');
    usernameInput.type = 'text';
    usernameInput.id = 'username';
    usernameInput.placeholder = 'Enter your username';
    chatDiv.appendChild(usernameInput);

    var loginBtn = document.createElement('button');
    loginBtn.textContent = 'Login';
    loginBtn.onclick = login;
    chatDiv.appendChild(loginBtn);
}

function sendMessage() {
    var message = document.getElementById('message').value;
    if (!message) {
        alert("Message cannot be empty.");
    } else {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/messages", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.withCredentials = true;
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                document.getElementById('message').value = ''; 
                last_message_timestamp = Date.now() / 1000;
            } else if (xhr.status === 401)
                logout();
        };
        xhr.send(JSON.stringify({ user: username, message: message, message_id: Math.floor(Math.random()*1000000)}));
    }
}


function poll() {
    pollInterval = setInterval(fetchMessages, 800);
}

function fetchMessages() {
    var xhr = new XMLHttpRequest();
    var url = last_message_timestamp !== 0
        ? "/api/messages?timestamp=" + last_message_timestamp
        : "/api/messages";

    xhr.open("GET", url, true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var messages = JSON.parse(xhr.responseText);
            var messagesDiv = document.getElementById('messages');
            messages.forEach(function (msg) {
                var messageElement = document.createElement('div');
                messageElement.id = `message-${msg.message_id}`;
                
                var messageText = document.createElement('span');
                messageText.textContent = msg.user + ': ' + msg.message;
                messageElement.appendChild(messageText);
                
                var button = document.createElement('button');
                button.textContent = "X";
                button.onclick = function() {
                    deleteMessage(msg.message_id);
                };
                messageElement.appendChild(button);

                messagesDiv.appendChild(messageElement);
            });
            if (messages.length > 0) {
                last_message_timestamp = messages[messages.length - 1].timestamp;
            }
        } else if (xhr.status === 401) {
            logout();
        }
    };
    xhr.send();
}

function logout() {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/api/login", true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
        if ((xhr.readyState === 4 && xhr.status === 200) || xhr.status === 401) {
            createLoginInterface();
            clearInterval(pollInterval);
            username = null;
            last_message_timestamp = 0;
        }
    };
    xhr.send();
}

function checkLoginStatus() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/login", true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            username = JSON.parse(xhr.responseText).user;
            setupChatInterface();
        } else if (xhr.status === 401)
            createLoginInterface();
    };
    xhr.send();
}

function deleteMessage(message_id) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/api/messages/" + message_id, true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var messageElement = document.getElementById(`message-${message_id}`);
            if (messageElement) {
                messageElement.remove();
            }
        } else if (xhr.status === 400) {
            alert("You can only delete your own message!");
        }
    };
    xhr.send();
}
