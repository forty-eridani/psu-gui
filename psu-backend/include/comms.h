#ifndef COMMS_H_
#define COMMS_H_

#include <stdint.h>

// Performs the initial negotiation for RFC2217
void negotiate(int sockfd);

#endif
