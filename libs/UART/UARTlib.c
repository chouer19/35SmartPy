#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <termios.h>
#include "uart.h"
#include "uartdata.h"
#include "queue.h"
#include <string.h>

unsigned char *gnss_read = new unsigned char[60];
extern "C" unsigned char *readGNSS(){

    int uartlen = 0;
    if((uartlen = GetReceiveUartDataLen(MCU_UART)) > 59){
        unsigned char uartdata[uartlen+1];
        GetReceiveUartData(MCU_UART,uartdata,uartlen);
    }

    while( (uartlen = GetReceiveUartDataLen(MCU_UART)) < 60 ){
        ;
    }
    GetReceiveUartData(MCU_UART, gnss_read, uartlen);

    return gnss_read;
}

extern "C"  void init(void)
{
    QueueInit();
    MCUUartInit();
    MCUUartListen();
}
