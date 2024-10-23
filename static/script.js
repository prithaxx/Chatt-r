function sendMessage() {
    var message = document.getElementById('message').value;
    console.log("Message sent: " + message);
    // Later: Implement sending message to /api/messages using XMLHttpRequest
}

// This will be polling every 5 seconds to get new messages
setInterval(function() {
    console.log("Fetching new messages...");
    // Later: Implement GET /api/messages here using XMLHttpRequest
}, 5000);
