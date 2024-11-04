#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <assert.h>

void send_request(int socket_desc, const char *request, char *response) {
    send(socket_desc, request, strlen(request), 0);
    recv(socket_desc, response, 2000, 0);
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        printf("Usage: %s <host> <port> <username> <chat_message>\n", argv[0]);
        return -1;
    }

    char *host = argv[1];
    int port = atoi(argv[2]);
    char *username = argv[3];

    // Combine the remaining arguments as the chat message, allowing spaces
    char chat_message[1024] = "";
    for (int i = 4; i < argc; i++) {
        strcat(chat_message, argv[i]);
        if (i < argc - 1) strcat(chat_message, " ");
    }

    int socket_desc;
    struct sockaddr_in server_addr;
    char response[2000];
    char login_request[1024];
    char post_request[2048];
    char get_request[1024];
    char session_cookie[100];

    // Create socket
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_desc == -1) {
        printf("Could not create socket\n");
        return -1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, host, &server_addr.sin_addr) <= 0) {
        printf("Invalid address/ Address not supported\n");
        return -1;
    }

    if (connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        printf("Unable to connect\n");
        return -1;
    }

    // LOGIN request
    snprintf(login_request, sizeof(login_request),
             "POST /api/login HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Content-Type: application/json\r\n"
             "Content-Length: %ld\r\n\r\n"
             "{\"user\":\"%s\"}",
             host, strlen(username) + 10, username);

    send_request(socket_desc, login_request, response);
    snprintf(session_cookie, sizeof(session_cookie), "%s", username);

    // Close and reopen socket for the next request
    close(socket_desc);
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr));

    // POST message
    snprintf(post_request, sizeof(post_request),
             "POST /api/messages HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Content-Type: application/json\r\n"
             "Cookie: session_id=%s\r\n"
             "Content-Length: %ld\r\n\r\n"
             "{\"message\":\"%s\"}",
             host, session_cookie, strlen(chat_message) + 12, chat_message);

    send_request(socket_desc, post_request, response);
    assert(strstr(response, "200 OK") != NULL); // Ensure the message was accepted

    // Close and reopen socket for the verification request
    close(socket_desc);
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr));

    // GET request to verify the chat message
    snprintf(get_request, sizeof(get_request),
             "GET /api/messages HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Cookie: session_id=%s\r\n\r\n",
             host, session_cookie);

    send_request(socket_desc, get_request, response);

    // Check if the posted message is in the response
    assert(strstr(response, chat_message) != NULL); // Verify the chat message is present

    printf("Message posted and verified successfully!\n");

    close(socket_desc);
    return 0;
}
