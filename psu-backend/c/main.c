#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netdb.h>
#include <memory.h>
#include <netinet/in.h>
#include <stdlib.h>

#include "comms.h"

#define PORT "4000"
#define BACKLOG 10
#define REC_BUF_SIZE 2048
#define SEND_BUF_SIZE 2048

static void printBufHex(const char* prefix, const char* buf, int len) {
		printf("%s: '", prefix);

		for (int i = 0; i < len; i++) {
			printf("%X ", (uint8_t)buf[i]);
		}

		printf("'\n");
}

static void getAddrString(struct sockaddr* addr, char* buf) {
	if (addr == NULL) {
		printf("Could not make string out of null address.\n");
		return;
	}
	if (addr->sa_family == AF_INET) {
		struct sockaddr_in* addr_in = (struct sockaddr_in*)addr;
		inet_ntop(addr_in->sin_family, &(addr_in->sin_addr), buf, INET_ADDRSTRLEN);
	 } else {
		struct sockaddr_in6* addr_in6 = (struct sockaddr_in6*)addr;
		inet_ntop(addr_in6->sin6_family, &(addr_in6->sin6_addr), buf, INET6_ADDRSTRLEN);
	 }
}

int main() {
	struct addrinfo hints, *res, *cur;
	
	memset(&hints, 0, sizeof(hints));

	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;

	char display_addr_buf[INET6_ADDRSTRLEN];

	int status;

	if ((status = getaddrinfo(NULL, PORT, &hints, &res)) != 0) {
		fprintf(stderr, "[Error %d] getaddrinfo: %s\n", status, gai_strerror(status));
		exit(-1);
	}

	int local_fd = -1;
	int yes = 1;

	for (cur = res; cur != NULL; cur = cur->ai_next) {
		local_fd = socket(AF_INET, SOCK_STREAM, cur->ai_protocol);

		setsockopt(local_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));

		if (local_fd < 0)
			continue;

		if (bind(local_fd, cur->ai_addr, cur->ai_addrlen) != 0) {
			close(local_fd);
			local_fd = -1;
		} else {
			break; // Success!
		}
	}

	if (local_fd == -1) {
		fprintf(stderr, "Could not bind, Error: %s.\n", gai_strerror(errno));
		exit(-1);
	}	

	getAddrString(cur->ai_addr, display_addr_buf);
	printf("Found open socket on '%s'.\n", display_addr_buf);

	freeaddrinfo(res);

	if (listen(local_fd, BACKLOG) != 0) {
		fprintf(stderr, "Could not listen.\n");
		exit(-1);
	}

	printf("Now listening.\n");

	struct sockaddr_storage other_addr;
	socklen_t other_addr_size = sizeof(other_addr);

	while (true) {
		int their_fd = accept(local_fd, (struct sockaddr*)&other_addr, &other_addr_size);

		getAddrString((struct sockaddr*)&other_addr, display_addr_buf);

		printf("Connected to %s.\n", display_addr_buf);

		while (rawSocketComms(their_fd) != -1);

		// char rec_buf[REC_BUF_SIZE];
		// char send_buf[SEND_BUF_SIZE];
		//
		//
		// int rec_length = recv(their_fd, rec_buf, REC_BUF_SIZE, 0);
		// printf("Recieved From Client (string): '%s'\n", rec_buf);
		// printBufHex("Recieved From Client (hex)", rec_buf, rec_length);

	}

	printf("Reached end of program somehow\n");
}
