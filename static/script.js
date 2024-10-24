document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed"); // Check if this logs
    document.getElementById("sendbtn").addEventListener("click", function() {
        console.log("Button clicked"); // Check if this logs when button is clicked
        sendMessage();
    });
});

function sendMessage() {
    var message = document.getElementById('message').value;
    var user = "web_user"; // Replace this with the username logic
    console.log("Sending message: ", message); // Debugging log
    if (!message) {
        console.log("Message cannot be empty."); // Log for empty messages
        return;
    }
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/messages", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                console.log("Message sent successfully");
                document.getElementById('message').value = ''; // Clear the input field
            } else {
                console.log("Error sending message: ", xhr.status, xhr.statusText); // Log error status
            }
        }
    };
    xhr.send(JSON.stringify({ user: user, message: message }));
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

// Poll for new messages every 5 seconds
setInterval(fetchMessages, 5000);

