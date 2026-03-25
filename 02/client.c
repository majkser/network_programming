#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <ctype.h>

int main(int argc, char *argv[])
{
    int sock;
    int rc;         // "rc" to skrót słów "result code"
    ssize_t cnt;    // wyniki zwracane przez read() i write() są tego typu

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        return 1;
    }

    printf("Connecting to server at %s:%s\n", argv[1], argv[2]);

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_addr = { .s_addr = inet_addr(argv[1]) }, //0x7F000001  // 127.0.0.1
        .sin_port = htons(atoi(argv[2])) //20123
    };

    rc = connect(sock, (struct sockaddr *) & addr, sizeof(addr));
    if (rc == -1) {
        perror("connect");
        return 1;
    }

    unsigned char buf[1024];

    cnt = read(sock, buf, sizeof(buf) - 1);
    if (cnt == -1) {
        perror("read");
        return 1;
    }

    for (size_t i = 0; i < cnt; ++i) {
        unsigned char c = buf[i];
        if (!isprint(c) && c != '\n' && c != '\r' && c != '\t') {
            buf[i] = '.';
        }
    }

    buf[cnt] = '\0';
    printf("read %zi bytes\n", cnt);
    printf("message: %s\n", buf);

    rc = close(sock);
    if (rc == -1) {
        perror("close");
        return 1;
    }

    return 0;
}