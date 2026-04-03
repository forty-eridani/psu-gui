#include "comms.h"

#include <signal.h>
#include <sys/socket.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BUF_LEN 512
#define UNTERMINATED_ERR "[Emulation Error] Command improperly terminated; must end with \\r" 

bool inRemoteMode = false;

char signal_buf[BUF_LEN];

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

struct {
	uint8_t addr;
	double output_voltage;
	double current;
	bool device_on;
	bool foldback_prot;
	uint8_t foldback_delay;
	double ovp; // Over voltage limit
	double ovl; // Undervoltage limit
	double uvl;
	bool ast; // Auto restart
	bool is_addressed;
} device;

char lastCommand[BUF_LEN] = {'\0'};

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

	printf("Waiting for request...\n");

	int len = recv(sockfd, rec_buf, BUF_LEN, 0);

	printf("Recieved Request!\n");

	int send_len = setSignalBuffer(rec_buf, len);

	printBufHex("Recieved Buffer (in hex)", rec_buf, len);

	printBufHex("Sending Buffer (in hex)", signal_buf, send_len);

	send(sockfd, signal_buf, send_len, 0);

	printf("Sent response!\n");
}

// All commands end via a carriage return (ascii 13)
static bool properlyTerminated(const char* s) {
	return s[strlen(s) - 1] == '\r';
}

static bool numericallyCorrect(const char* s) {
	bool decimal = false;

	// Offsetting by one if there is an offset
	int offset = s[0] == '-' ? 1 : 0;

	// strlen() - 1 excludes carriage return
	for (int i = offset; i < strlen(s) - 1; i++) {
		if (s[i] >= '0' || s[i] <= '9')
			continue;
		else if (s[i] == '.' && decimal == false) {
			decimal = true;
			continue;
		} else {
			printf("Failed when s[i] = '%c'.\n", s[i]);
			return false;
		}
	}

	return true;
}

static bool integerCorrect(const char* s) {
	// Offsetting by one if there is an offset
	int offset = s[0] == '-' ? 1 : 0;

	for (int i = 0; i < strlen(s) - 1; i++) {
		if (s[i] >= '0' || s[i] <= '9')
			continue;

		return false;
	}

	return true;
}

static void addNewline(char* s) {
	s[strlen(s)] = '\n';
	s[strlen(s) + 1] = '\0';
}

// Writes "OK" to the signal buffer
static void okay() {
	strcpy(signal_buf, C03);
}

// All boolean commands can either take an 'ON' or '1' for true, and
// 'OFF' or '0' for false
static int boolean(const char* s) {
	if (!properlyTerminated(s)) {
		strcpy(signal_buf, UNTERMINATED_ERR);
	} else if (s[strlen(s) - 3] == '1' || strncmp(s + 4, "ON", 2)) {
		return 1;
	} else if (s[strlen(s) - 3] == '0' || strncmp(s + 4, "OFF", 3)) {
		return 0;
	} 

	return -1;
}

int rawSocketComms(int sockfd) {	
	char rec_buf[BUF_LEN];
	memset(signal_buf, 0, BUF_LEN);

	printf("Waiting for request...\n");
	
	int len = recv(sockfd, rec_buf, BUF_LEN, 0);
	rec_buf[len] = '\0';

	double num_buf[BUF_LEN] = {'\0'};

	if (len == 0)
		return -1;

	printf("Recieved Request! Command recieved: %s\n", rec_buf);

	if (strncmp(rec_buf, "ADR ", 4) == 0) {
		int num = atoi(rec_buf + 4);
		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else if (!integerCorrect(rec_buf) || atoi(rec_buf) < 0 || atoi(rec_buf) > 30) {
			strcpy(signal_buf, C03);
		} else {
			okay();
		}
	} 
	else if (strcmp(rec_buf, "CLS\r") == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "RST\r") == 0) {
		device.output_voltage = 0.0;
		device.current = 0.0;
		device.ast = false;
		device.ovp = 660;
		device.foldback_prot = false;
		device.uvl = 0.0;
		okay();
	} 
	else if (strncmp(rec_buf, "RMT ", 4) == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "RMT?\r") == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "MDAV?\r") == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "\\\r") == 0) {
		okay();
	} 
	else if (strcmp(rec_buf, "IDN?\r") == 0) {
		strcpy(signal_buf, "GEN600-2.6");
	} 
	else if (strcmp(rec_buf, "REV?\r") == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "SN?\r") == 0) {
		strcpy(signal_buf, INOP);	
	} 
	else if (strcmp(rec_buf, "DATE?\r") == 0) {
		time_t rawtime;
		struct tm* info;
		char time_buffer[80];

		time(&rawtime);

		info = localtime(&rawtime);

		strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%d", info);

		strcpy(signal_buf, time_buffer);
	} 

	if (strncmp(rec_buf, "PV ", 3) == 0) {
		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else {
			double pv = atof(rec_buf + 3);

			if (!numericallyCorrect(rec_buf + 3)) {
				strcpy(signal_buf, C03);
			} else if (pv > 600.0 || pv < 0) { // Doesn't check for violations of OVP since 
											   // that is impossible in our little emulation 
				strcpy(signal_buf, E01);
			} else {
				device.output_voltage = pv;
				strcpy(signal_buf, OK);	
			}
		}
	} 
	else if (strcmp(rec_buf, "PV?\r") == 0) {
		sprintf(signal_buf, "%fV", device.output_voltage);	
	} 
	else if (strcmp(rec_buf, "MV?\r") == 0) {
		// Let's just always assume that our true output always equals our target output
		sprintf(signal_buf, "%fV", device.output_voltage);	
	} 
	else if (strncmp(rec_buf, "PC ", 3) == 0) {
		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else {
			double pc = atof(rec_buf + 3);

			if (!numericallyCorrect(rec_buf + 3)) {
				strcpy(signal_buf, C03);
			} else if (pc > 2.6 || pc < 0.0) {
				strcpy(signal_buf, C05);
			} else {
				device.current = pc;
				strcpy(signal_buf, OK);	
			}
		}
		
	} 
	else if (strcmp(rec_buf, "PC?\r") == 0) {
		sprintf(signal_buf, "%fA", device.current);
	} 

	else if (strcmp(rec_buf, "MC?\r") == 0) {
		// Once again, target is always true output magically here
		sprintf(signal_buf, "%fA", device.current);
	} 
	else if (strcmp(rec_buf, "DVC?\r") == 0) {
		sprintf(signal_buf, "%f, %f, %f, %f, %f, %f", device.output_voltage, device.output_voltage, 
				device.current, device.current, device.ovl, device.uvl);
	} 
	else if (strncmp(rec_buf, "OUT ", 4) == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "OUT?\r") == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strncmp(rec_buf, "FLD ", 4) == 0) {
		int state = boolean(rec_buf);

		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else {
			switch (state) {
				case 0: {
					device.foldback_prot = false;
					okay();
					break;
				}
				case 1: {
					device.foldback_prot = true;
					okay();
					break;
				}
				default: {
					strcpy(signal_buf, C03);
				}
			}
		}
	} 
	else if (strcmp(rec_buf, "FLD?\r") == 0) {
		const char* bool_state = device.foldback_prot ? "ON" : "OFF";
		strcpy(signal_buf, bool_state);
	} 
	else if (strncmp(rec_buf, "FBD ", 4) == 0) {
		int fbd = atoi(rec_buf + 4);	
		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else if (!integerCorrect(rec_buf + 4)) {
			strcpy(signal_buf, C03);
		} else if (fbd < 0 || fbd > 255) {
			strcpy(signal_buf, C05);
		} else {
			device.foldback_delay = 0.1 * fbd;
		}
	} 
	else if (strcmp(rec_buf, "FBD?\r") == 0) {
		sprintf(signal_buf, "%us", device.foldback_delay);
	} 
	else if (strcmp(rec_buf, "FBDRST\r") == 0) {
		device.foldback_delay = 0.0;
		okay();
	} 
	else if (strncmp(rec_buf, "OVP ", 4) == 0) {
		double ovp = atof(rec_buf + 4);
		double min = device.output_voltage > 5.0 ? device.output_voltage : 5.0;

		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else if (!numericallyCorrect(rec_buf + 4)) {
			strcpy(signal_buf, C03);
		} else if (ovp < min) {
			strcpy(signal_buf, E04);
		} else if (ovp > 660.0) {
			strcpy(signal_buf, C05);
		} else {
			device.ovp = ovp;
			okay();
		}
	} 
	else if (strcmp(rec_buf, "OVP?\r") == 0) {
		sprintf(signal_buf, "%fV", device.ovp);
	} 
	else if (strcmp(rec_buf, "OVM\r") == 0) {
		 device.ovp = 660.0;
	} 
	else if (strncmp(rec_buf, "UVL ", 4) == 0) {
		double uvl = atof(rec_buf + 4);
		double max = 0.95 * device.output_voltage > 570.0 ? 0.95 * device.output_voltage : 570.0;

		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else if (!numericallyCorrect(rec_buf + 4)) {
			strcpy(signal_buf, C03);
		} else if (uvl > max || uvl < 5.0) {
			strcpy(signal_buf, E06);
		} else {
			device.ovp = uvl;
			okay();
		}	
	} 
	else if (strcmp(rec_buf, "UVL?\r") == 0) {
		sprintf(signal_buf, "%fV", device.uvl);
	} 
	else if (strncmp(rec_buf, "AST ", 4) == 0) {
		strcpy(signal_buf, INOP);
	} 
	else if (strcmp(rec_buf, "AST?\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "SAV\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "RCL\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "MODE?\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "MS?\r") == 0) {
		strcpy(signal_buf, INOP);
	}

	// Global inputs
	else if (strcmp(rec_buf, "GRST\r") == 0) {
		device.output_voltage = 0.0;
		device.ovp = 660.0;
	}
	else if (strncmp(rec_buf, "GPV ", 4) == 0) {
		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else {
			double pv = atof(rec_buf + 3);

			if (!numericallyCorrect(rec_buf + 3) == 0) {
				strcpy(signal_buf, C03);
			} else if (pv > 600.0 || pv < 0) { // Doesn't check for violations of OVP since 
											   // that is impossible in our little emulation 
				strcpy(signal_buf, E01);
			} else {
				device.output_voltage = pv;
				strcpy(signal_buf, OK);	
			}
		}
	}	
	else if (strncmp(rec_buf, "GPC ", 4) == 0) {
		if (!properlyTerminated(rec_buf)) {
			strcpy(signal_buf, UNTERMINATED_ERR);
		} else {
			double pc = atof(rec_buf + 3);

			if (!numericallyCorrect(rec_buf + 3) == 0) {
				strcpy(signal_buf, C03);
			} else if (pc > 2.6 || pc < 0.0 || pc > device.ovp) {
				strcpy(signal_buf, C05);
			} else {
				device.current = pc;
				strcpy(signal_buf, OK);	
			}
		}	
	} 
	else if (strcmp(rec_buf, "GOUT\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "GSAV\r") == 0) {
		strcpy(signal_buf, INOP);	
	}
	else if (strcmp(rec_buf, "GRCL\r") == 0) {
		strcpy(signal_buf, INOP);
	}

	// Status and Control Commands	
	else if (strcmp(rec_buf, "STT?\r") == 0) {
		sprintf(signal_buf, "MV(%f),PV(%f),MC(%f),PC(%f),SR(INOP),FR(INOP)", device.output_voltage, device.output_voltage, device.current, device.current);
	}
	else if (strcmp(rec_buf, "FLT?\r") == 0) {
		strcpy(signal_buf, INOP);	
	}
	else if (strcmp(rec_buf, "FENA\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "FENA?\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "FEVE?\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "STAT?\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "SENA\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "SENA?\r") == 0) {
		strcpy(signal_buf, INOP);
	}
	else if (strcmp(rec_buf, "SEVE?\r") == 0) {
		strcpy(signal_buf, INOP);
	} else {
		strcpy(signal_buf, C01);
	}

	addNewline(signal_buf);

	printf("Sending '%s'.\n", signal_buf);

	send(sockfd, signal_buf, strlen(signal_buf) + 1, 0);

	printf("Response Sent!\n");

	return 0;
}
