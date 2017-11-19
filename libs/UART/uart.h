#ifndef __UART_H__
#define __UART_H__
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#ifdef __cplusplus
extern  "C" {
#endif
extern int fduart;
extern int txuart;
#define tx1uart	 9600

typedef struct SERIAL
{
  unsigned char *ComName;    //serial name
  unsigned int  ComBaud;     //serial baudrate
  unsigned char ComVerify;   // serial parity
  unsigned int  ComData;     //serial  data bit
  unsigned int  ComStop;     //serial stop bit
}STR_SERIAL;
void UartInit(void);
void TXUartInit(void);	
void MCUUartInit(void);
int setCom(int fdCom , unsigned int baudrate ,unsigned int databit ,  unsigned char parity , unsigned int stopbit);
#ifdef __cplusplus
}
#endif
#endif
