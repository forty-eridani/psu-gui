#include "comms.h"

#include <sys/socket.h>
#include <stdint.h>
#include <stdio.h>

#define BUF_LEN 512

typedef struct {
	char* buf;
	int len;
} Response;

uint8_t signal_buf[BUF_LEN];

static void printBufHex(const char* prefix, const uint8_t* buf, int len) {
		printf("%s: '", prefix);

		for (int i = 0; i < len; i++) {
			printf("%X ", (uint8_t)buf[i]);
		}

		printf("'\n");
}

static void telnetNegotiateResponse(uint8_t* res, int len) {
	for (int i = 0; i < len; i++) {
		// Hope that each telnet command will start with 0xFF
		signal_buf[i++] = 0xFF;

		// Being really mean here and only accepting the RFC2217 request
		switch (res[i + 1]) {
			case 0x2C: {
				signal_buf[i++] = 0xFD;
				signal_buf[i] = res[i];
				break;
			}

			default: {
				signal_buf[i++] = 0xFC;
				signal_buf[i] = res[i];
				break;
			}
		}
	}
}

void negotiate(int sockfd) {
	uint8_t rec_buf[BUF_LEN];

	int len = recv(sockfd, rec_buf, BUF_LEN, 0);

	telnetNegotiateResponse(rec_buf, len);

	printBufHex("Recieved Buffer (in hex)", rec_buf, len);
	printBufHex("Sending Buffer (in hex)", signal_buf, len);

	send(sockfd, signal_buf, len, 0);
}

void respondWithState(int sockfd) { 

}
