#ifndef COMMS_H_
#define COMMS_H_

#include <stdint.h>

// TELNET command options
#define ECHO 0x01 // Whether the device will read back input sent
#define RECON 0x02 // If connection drops out, whether the device will reconnect
#define SGA 0x03 // Whether to switch from simplex to duplex
#define APPROX_MSG_SIZE_NEG 0x04 // Expected size of data going between devices 
#define STATUS 0x05 // Requests other device to display current option negotiation 
#define MARK 0x06 // Synchronizes comms
#define TERMINAL_TYPE 0x18 // Requesting terminal type
#define TERMINAL_SPEED 0x20 // Request for other device to report current connection speed
#define LINEMODE 0x22 // Requesting to send data line by line instead of by characters
#define COM_PORT 0x2C // Requesting use of RFC2217 

// TELNET commands
#define GA 0xF9 // Go ahead command
#define WILL 0xFB
#define WONT 0xFC
#define DO 0xFD
#define DONT 0xFE
#define IAC 0xFF // Escape byte for indicating a command

// Performs the initial negotiation for RFC2217
void negotiate(int sockfd);

// Responds to all of the TELNET requests as a pretend serial device
void respondWithState(int sockfd);

#endif
