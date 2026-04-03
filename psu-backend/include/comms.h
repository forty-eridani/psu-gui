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
				 

// Errors for the device itself
#define E01 "[Device Error] E01" // Voltage too high for either rating or OVP
#define E02 "[Device Error] E02" // Voltage below UVL
#define E04 "[Device Error] E04" // OVP programmed too low
#define E06 "[Device Error] E06" // UVL programmed above programmed output voltage
#define E07 "[Deivce Error] E07" // Programmed on during a fault shutdown

#define C01 "[Device Error] C01" // Illegal command
#define C02 "[Device Error] C02" // Missing parameter
#define C03 "[Device Error] C03" // Illegal parameter
#define C04 "[Device Error] C04" // Checksum error
#define C05 "[Device Error] C05" // Setting out of range

// Pretty self-explanitory
#define OK "OK"

#define INOP "INOP" // Inoperational commands that I am either too lazy to program 
					// or are impossible to emulate

// Performs the initial negotiation for RFC2217
void negotiate(int sockfd);

// Responds to all of the TELNET requests as a pretend serial device
void respondWithState(int sockfd);

// Doesn't bother with telenet protocols, assumes raw socket
void rawSocketComms(int sockfd);

#endif
