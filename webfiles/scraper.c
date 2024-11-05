#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h> 
#include <assert.h>

void send_request(int socket_desc, const char *request, char *response){
    send(socket_desc, request, strlen(request), 0);
    recv(socket_desc, response, 2000, 0);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Usage: %s <host> <port> <username> <chat_message>\n", argv[0]);
        return -1;
    }

    char *host = argv[1];
    int port = atoi(argv[2]);
    char *username = argv[3];
    char *chat_message = argv[4];

    int socket_desc;
    struct sockaddr_in server_addr;
    struct hostent *he;  // Structure for host information
    char response[2000];
    char cookie_request[1024];
    char post_request[1024];
    char get_request[1024];

    // Resolve hostname to IP address
    if ((he = gethostbyname(host)) == NULL) {
        perror("Error resolving hostname");
        return -1;
    }

    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_desc == -1) {
        printf("Could not create socket\n");
        return -1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    memcpy(&server_addr.sin_addr, he->h_addr_list[0], he->h_length);

    if (connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        printf("Unable to connect\n");
        return -1;
    }

    // Checks for a cookie
    snprintf(cookie_request, sizeof(cookie_request),
             "GET /api/status HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Cookie: session_id=%s\r\n\r\n",
             host, username);
    
    send_request(socket_desc, cookie_request, response);
    assert(strstr(response, username) != NULL && "Cookie does not exist");
    printf("Cookie (%s) exists and verified successfully.\n", username);

    close(socket_desc);
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr));

    // POST chat message
    snprintf(post_request, sizeof(post_request),
             "POST /api/messages HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Content-Type: application/json\r\n"
             "Content-Length: %ld\r\n"
             "Cookie: session_id=%s\r\n\r\n"
             "{\"message\":\"%s\"}",
             host, strlen(chat_message)+20, username, chat_message);

    send_request(socket_desc, post_request, response);

    close(socket_desc);
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr));

    // GET verification
    snprintf(get_request, sizeof(get_request),
             "GET /api/messages HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Cookie: session_id=%s\r\n\r\n",
             host, username);

    send_request(socket_desc, get_request, response);

    assert(strstr(response, chat_message) != NULL && "Message verification failed");
    printf("Message (%s) sent and verified successfully.\n", chat_message);

    close(socket_desc);

    return 0;
}