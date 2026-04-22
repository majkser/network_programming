#define _POSIX_C_SOURCE 200809L
#include <stdbool.h>
#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

bool isValidPalindrome(const char *str);
bool isFormatError(const unsigned char *buf, size_t cnt, size_t original_cnt);
bool writeAll(int fd, const char *buf, size_t len);
bool handleClient(int clnt_sock);
bool processLine(int clnt_sock, unsigned char *line, size_t line_len, bool line_too_long);

int main(void)
{
    int lst_sock;
    int clnt_sock;
    int rc;

    lst_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (lst_sock == -1) {
        perror("socket");
        return 1;
    }

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_addr = {.s_addr = htonl(INADDR_ANY)},
        .sin_port = htons(2020)
    };

    rc = bind(lst_sock, (struct sockaddr *) &addr, sizeof(addr));
    if (rc == -1) {
        perror("bind");
        return 1;
    }

    rc = listen(lst_sock, 10);
    if (rc == -1) {
        perror("listen");
        return 1;
    }

    if (signal(SIGCHLD, SIG_IGN) == SIG_ERR) {
        perror("signal");
        return 1;
    }

    printf("Server is listening on port: 2020\n");
    while (true) {
        clnt_sock = accept(lst_sock, NULL, NULL);
        if (clnt_sock == -1) {
            perror("accept");
            return 1;
        }

        pid_t pid = fork();
        if (pid == -1) {
            perror("fork");
            return 1;
        }

        if (pid == 0) {
            rc = close(lst_sock);
            if (rc == -1) {
                perror("close");
                return 1;
            }

            bool ok = handleClient(clnt_sock);
            rc = close(clnt_sock);
            if (rc == -1) {
                perror("close");
                return 1;
            }

            return ok ? 0 : 1;
        }

        rc = close(clnt_sock);
        if (rc == -1) {
            perror("close");
            return 1;
        }
    }

    rc = close(lst_sock);
    if (rc == -1) {
        perror("close");
        return 1;
    }

    return 0;
}

bool handleClient(int clnt_sock)
{
    unsigned char buf[2048];
    unsigned char line[2048];
    size_t line_len = 0;
    bool line_too_long = false;

    while (true) {
        ssize_t cnt = read(clnt_sock, buf, sizeof(buf));
        if (cnt == -1) {
            perror("read");
            return false;
        }
        printf("received %zd bytes: ", cnt);
        for (ssize_t i = 0; i < cnt; i++) {
            printf("%c", buf[i]);
        }
        printf("\n");

        if (cnt == 0) {
            if (line_len > 0 || line_too_long) {
                if (!processLine(clnt_sock, line, line_len, line_too_long)) {
                    return false;
                }
            }
            return true;
        }

        for (ssize_t i = 0; i < cnt; i++) {
            unsigned char ch = buf[i];
            if (ch == '\n' && line_len > 0 && line[line_len - 1] == '\r') {
                line_len--;
                line[line_len] = '\0';
                if (!processLine(clnt_sock, line, line_len, line_too_long)) {
                    return false;
                }
                line_len = 0;
                line_too_long = false;
            } else {
                if (!line_too_long) {
                    if (line_len < sizeof(line) - 1) {
                        line[line_len++] = ch;
                    } else {
                        line_too_long = true;
                    }
                }
            }
        }
    }

    return true;
}

bool processLine(int clnt_sock, unsigned char *line, size_t line_len, bool line_too_long)
{
    bool format_error;
    if (line_too_long) {
        format_error = true;
    } else {
        format_error = isFormatError(line, line_len, line_len);
    }

    char response[50];
    if (format_error) {
        snprintf(response, sizeof(response), "ERROR\r\n");
    } else {
        char *words[1000];
        int word_count = 0;

        char *word = strtok((char *) line, " ");
        while (word != NULL && word_count < 1000) {
            words[word_count++] = word;
            word = strtok(NULL, " ");
        }

        int palindromeCounter = 0;
        for (int i = 0; i < word_count; i++) {
            if (isValidPalindrome(words[i])) {
                palindromeCounter++;
            }
        }

        snprintf(response, sizeof(response), "%d/%d\r\n", palindromeCounter, word_count);
    }

    return writeAll(clnt_sock, response, strlen(response));
}

bool isValidPalindrome(const char *str)
{
    size_t len = strlen(str);
    for (size_t i = 0; i < len / 2; ++i) {
        if (tolower((unsigned char) str[i]) != tolower((unsigned char) str[len - 1 - i])) {
            return false;
        }
    }
    return true;
}

bool isFormatError(const unsigned char *buf, size_t cnt, size_t original_cnt)
{
    if (original_cnt > 1024) {
        return true;
    } else if (cnt > 0 && (buf[0] == ' ' || buf[cnt - 1] == ' ' || buf[cnt - 1] > 127 || buf[cnt -1] < 0 || !isalpha(buf[cnt - 1]))) {
        return true;
    } else if (cnt > 0) {
        for (size_t i = 0; i + 1 < cnt; i++) {
            if (buf[i] == ' ' && buf[i + 1] == ' ') {
                return true;
            }
            if (buf[i] > 127 || (!isalpha(buf[i]) && buf[i] != ' ')) {
                return true;
            }
        }
    }
    return false;
}

bool writeAll(int fd, const char *buf, size_t len)
{
    size_t written_cnt = 0;

    while (written_cnt < len) {
        ssize_t cnt = write(fd, buf + written_cnt, len - written_cnt);
        if (cnt == -1) {
            perror("write");
            return false;
        }

        written_cnt += (size_t) cnt;
    }

    printf("sent %zu bytes\n", written_cnt);
    return true;
}
