#define _POSIX_C_SOURCE 200809L
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <ctype.h>
#include <string.h>

bool isValidPalindrome(const char *str) {
    size_t len = strlen(str);
    for (size_t i = 0; i < len / 2; ++i) {
        if (tolower(str[i]) != tolower(str[len - 1 - i])) {
            return false;
        }
    }
    return true;
}

int main(void)
{
    int sock;
    int rc;         // "rc" to skrót słów "result code"
    ssize_t cnt;    // na wyniki zwracane przez recvfrom() i sendto()

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("socket");
        return 1;
    }

    int port = 2020;
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_addr = { .s_addr = htonl(INADDR_ANY) },
        .sin_port = htons(port)
    };

    rc = bind(sock, (struct sockaddr *) & addr, sizeof(addr));
    if (rc == -1) {
        perror("bind");
        return 1;
    }
    printf("Server is listening on port: %d\n", port);

    bool keep_on_handling_clients = true;
    while (keep_on_handling_clients) {

        unsigned char buf[2048];
        struct sockaddr_in clnt_addr;
        socklen_t clnt_addr_len;

        clnt_addr_len = sizeof(clnt_addr);
        cnt = recvfrom(sock, buf, sizeof(buf), 0,
                (struct sockaddr *) & clnt_addr, & clnt_addr_len);
        if (cnt == -1) {
            perror("recvfrom");
            return 1;
        }
        printf("received %zi bytes\n", cnt);
        
        ssize_t original_cnt = cnt;

        if (cnt > 0 && (buf[cnt - 1] == '\n')) {
            cnt--;
            if (cnt > 0 && buf[cnt - 1] == '\r') {
                cnt--;
            }
        }

        buf[cnt] = '\0';

        bool format_error = false;
        if (original_cnt > 1024) { //Serwer musi być w stanie przetwarzać zapytania mające 1024 bajty lub mniej, na większe może odpowiadać „ERROR”
            format_error = true;
        } else if (cnt > 0 && (buf[0] == ' ' || buf[cnt - 1] == ' ' || !isalpha(buf[cnt - 1]))) {
            format_error = true;
        } else if (cnt > 0) {
            for (ssize_t i = 0; i < cnt - 1; i++) {
                if (buf[i] == ' ' && buf[i + 1] == ' ') {
                    format_error = true;
                    break;
                }
                if (!isalpha(buf[i]) && buf[i] != ' ') {
                    format_error = true;
                    break;
                }
            }
        }
        
        char response[50];
        if (format_error) {
            snprintf(response, sizeof(response), "ERROR");
        } else  {
            char *words[1000];
            int word_count = 0;
                char *word = strtok((char *)buf, " ");
                while (word != NULL && word_count < 1000) {
                    words[word_count++] = word;
                    word = strtok(NULL, " ");
                }

            int palindromeCounter = 0;
            for (int i = 0; i < word_count; i++) {
                bool isPalindrome = isValidPalindrome(words[i]);
                if (isPalindrome) {
                    palindromeCounter++;
                }
            }

            snprintf(response, sizeof(response), "%d/%d", palindromeCounter, word_count);
        }

        cnt = sendto(sock, response, strlen(response), 0,
                (struct sockaddr *) & clnt_addr, clnt_addr_len);
        if (cnt == -1) {
            perror("sendto");
            return 1;
        }
        printf("sent %zi bytes\n", cnt);

    }

    rc = close(sock);
    if (rc == -1) {
        perror("close");
        return 1;
    }

    return 0;
}
