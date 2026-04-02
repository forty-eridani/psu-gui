#include "comms.h"

#include <sys/socket.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define BUF_LEN 512

typedef struct {
	char* buf;
	int len;
} Response;

uint8_t signal_buf[BUF_LEN];

static void printBufHex(const char* prefix, const uint8_t* buf, int len) {
		printf("%s with length %d: '", prefix, len);

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

// Responds with the ability of our emulator to do that option
static uint8_t getResponse(uint8_t option) {
	switch (option) {
		case ECHO:
		case SGA:
		case COM_PORT:
			return WILL;
		default:
			return WONT;
	}
}

static int setSignalBuffer(uint8_t* rec, int len) {
	int i;

	for (i = 0; i < len; i++) {
		signal_buf[i++] = IAC; // Indicating that a command is about to be sent
		signal_buf[i] = getResponse(rec[i + 1]);
		i++;
		signal_buf[i] = rec[i];
		printf("I is %d\n", i);
	}

	// printf("I is %d right before returning where length is %d\n", i, len);

	return i;
}

void respondWithState(int sockfd) { 
	uint8_t rec_buf[BUF_LEN];

	printf("Watining for request...\n");

	int len = recv(sockfd, rec_buf, BUF_LEN, 0);

	printf("Recieved Request!\n");

	int send_len = setSignalBuffer(rec_buf, len);

	printBufHex("Recieved Buffer (in hex)", rec_buf, len);

	printBufHex("Sending Buffer (in hex)", signal_buf, send_len);

	send(sockfd, signal_buf, send_len, 0);

	printf("Sent response!\n");
}
