#ifndef COMMS_H_
#define COMMS_H_

#include <stdint.h>

// Performs the initial negotiation for RFC2217
void negotiate(int sockfd);

// Responds to all of the TELNET requests as a pretend serial device
void respondWithState(int sockfd);

#endif
