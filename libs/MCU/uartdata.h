#ifndef __UARTDATA_H_

#define __UARTDATA_H_
#include <time.h>
#ifdef __cplusplus
extern  "C" {
#endif
#define TX1_0     4

/*#define TX1_1     1

#define TX1_2     2

#define TX1_3     3

#define FPGA_0    4

#define FPGA_1    5*/
#define MCU_UART  3

#define MCU_UART1  2 //new

#define can250  0

#define can500  1

#define DEBUGERR
//#define DEBUGMSG

#ifdef DEBUGMSG
#define DEBUG_MSG(format,arg...) printf(format,##arg)
#else
#define DEBUG_MSG(format,arg...)
#endif

#ifdef DEBUGERR
#define DEBUG_ERR(format,arg...) printf(format,##arg)
#else
#define DEBUG_ERR(format,arg...)
#endif
#define tx1uart	 9600
#define mcuuart  115200

#define MAXLEN 8196
#define PACKET_BUFFER_LIMIT 8196
#define canlen 15

extern FILE *canid;
extern FILE *candata;

typedef struct _CAN_OBJ {
    unsigned int     ID;
    unsigned int     TimeStamp;
    unsigned char    TimeFlag;
//    unsigned char    SendType;
    unsigned char    RemoteFlag;
    unsigned char    ExternFlag;
    unsigned char    DataLen;
    unsigned char    Data[8];
//    unsigned char    Reserved[3];

} CAN_OBJ, *P_CAN_OBJ;


//can api
void InitCANOBJ(P_CAN_OBJ pReceive, int len);
int GetReceiveCanNum( int id);
int GetReceiveCanData( int id,P_CAN_OBJ pReceive, int len);
int SendCanData( int id,P_CAN_OBJ pSend, int len);
void PrintGetReceiveCanData(P_CAN_OBJ pReceive, int len);
void gettime();

int packageValidation(void);
unsigned char * EncodePackage( int id,unsigned char *queue, int  len);





//uart api
void TXUartListen(void);
void MCUUartListen(void);
void UartListen(void);
int GetReceiveUartData( int id,unsigned char *queue, int len);
int SendMCUUartData(int id, unsigned char *queue, int len);
int SendTX1UartData(unsigned char *queue, int len);
int GetReceiveUartDataLen( int id);





#ifdef __cplusplus
}
#endif

#endif
