var username;
var last_message_timestamp = 0;
var pollInterval;


window.onload = function() {
    checkLoginStatus();
};

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
    chatDiv.appendChild(messageInput);

    var sendBtn = document.createElement('button');
    sendBtn.textContent = 'Send';
    sendBtn.onclick = sendMessage;
    chatDiv.appendChild(sendBtn);

    var logoutBtn = document.createElement('button')
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
    if (!message)
        alert("Message cannot be empty.");
    else {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/messages", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.withCredentials = true;
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var messagesDiv = document.getElementById('messages');
                var newMessage = username + ": " + message;
                var messageElement = document.createElement('div');
                messageElement.textContent = newMessage;
                messagesDiv.appendChild(messageElement);

                document.getElementById('message').value = '';
            }
            else if (xhr.status === 401){
                logout();
            }
        };
        xhr.send(JSON.stringify({ user: username, message: message }));
    }
}

function poll() {
    pollInterval = setInterval(fetchMessages, 1000);
}

function fetchMessages() {
    var xhr = new XMLHttpRequest();
    // if(last_message_timestamp!==0){
    //     varurl="/api/messages?timestamp="+last_message_timestamp;
    //     xhr.open("GET",url,true);
    // } else{
    //     xhr.open("GET","/api/messages",true);
    // }
    xhr.open("GET", "/api/messages", true);
    xhr.withCredentials = true;  // Ensures cookies are sent with request
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var messages = JSON.parse(xhr.responseText);
            console.log(JSON.stringify(messages));
            var messagesDiv = document.getElementById('messages');
            messages.forEach(function (msg) {
                messagesDiv.innerHTML += msg.user + ': ' + msg.message + '<br>';
                last_message_timestamp = msg.timestamp;
            });
        }
        else if (xhr.status === 401){
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
        if (xhr.readyState === 4 && xhr.status === 200) {
            createLoginInterface();
            username = null;
            last_message_timestamp = 0;
            clearInterval(pollInterval)
        }
        else if (xhr.status === 401){
            clearInterval(pollInterval);
            createLoginInterface();
        }
    };
    xhr.send();
}

function checkLoginStatus() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/login", true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200)
            setupChatInterface();
        else if (xhr.status === 401)
            login();
    };
    xhr.send();
}

