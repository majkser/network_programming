#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <hostname>\n", argv[0]);
        return 1;
    }
    char *hostname = argv[1];
    printf("Resolving hostname: %s\n", hostname);

    struct addrinfo hints = {
        .ai_family = AF_INET6,
        .ai_socktype = SOCK_STREAM
    };

    struct addrinfo *result;

    int res = getaddrinfo(hostname, NULL, &hints, &result);
    if (res != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(res));
        return 1;
    }

    for (struct addrinfo *p = result; p != NULL; p = p->ai_next) {
        char ipstr[INET6_ADDRSTRLEN];
        void *addr = NULL;

        if (p->ai_family == AF_INET6) {
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)p->ai_addr;
            addr = &ipv6->sin6_addr;
        }

        if (inet_ntop(p->ai_family, addr, ipstr, sizeof(ipstr)) != NULL) {
            printf("IP address: %s\n", ipstr);
        }
    }

    freeaddrinfo(result);
    return 0;
}