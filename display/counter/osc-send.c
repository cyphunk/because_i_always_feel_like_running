
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "lo/lo.h"

int main(int argc, char *argv[])
{

    /* an address to send messages to. sometimes it is better to let the server
     * pick a port number for you by passing NULL as the last argument */
//    lo_address t = lo_address_new_from_url( "osc.unix://localhost/tmp/mysocket" );
    if (argc < 2) {
      fprintf(stderr, "usage: %s <port> <prefix> <int>\n", argv[0]);
      fprintf(stderr, "eg. 9000 int 1\n");
      return -1;
    }

    lo_address t = lo_address_new(NULL, argv[1]);
    if (lo_send(t, argv[2], "i", atoi(argv[3])) == -1) {
        printf("OSC error %d: %s\n", lo_address_errno(t),
               lo_address_errstr(t));
    }
    usleep(300*1000);
    return 0;
}
