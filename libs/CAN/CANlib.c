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

unsigned char *brake_point = new unsigned char[8];
CAN_OBJ brake_receive[10];    
extern "C"  unsigned char *readBrake(){
    InitCANOBJ(brake_receive,10);
    int canLen = 0;
    int haveBrake = 0;
    while(!haveBrake){//1.1
        while(canLen <=0){
            canLen=GetReceiveCanNum(can250);
        }
        GetReceiveCanData(can250, brake_receive, canLen);
        for(int i=canLen - 1; i >=0; i--){//1.1.1
            if(brake_receive[i].ID == 0x100){//000
                haveBrake = 1;
                for(int j=0;j<8;j++){
                    brake_point[j] = brake_receive[i].Data[j];
                }
                //break;
                return brake_point;
            }//000
        }//1.1.1
    }//1.1
    return brake_point;
}

unsigned char gun[8];
CAN_OBJ gun_receive[50];    
unsigned char *gun_point = new unsigned char[8];
extern "C"  unsigned char *readGun(){
    InitCANOBJ(gun_receive,50);
    int canLen = 0;
    int haveBrake = 0;
    while(!haveBrake){//1.1
        while(canLen <=0){
            canLen=GetReceiveCanNum(can250);
        }
        GetReceiveCanData(can250, gun_receive, canLen);
        for(int i=canLen - 1; i >=0; i--){//1.1.1
            if(gun_receive[i].ID == 0x200){//000
                haveBrake = 1;
                for(int j=0;j<8;j++){
                    gun_point[j] = gun_receive[i].Data[j];
                }
                //break;
                return gun_point;
            }//000
        }//1.1.1
    }//1.1
    return gun_point;
}

unsigned char *testRead = new unsigned char[8];
unsigned char tst[8];
CAN_OBJ receive[50];
extern "C" unsigned char * readTest(){
    InitCANOBJ(receive, 50);
    int canLen = 0;
    while(canLen <= 0){
        canLen = GetReceiveCanNum(can250);
    }
    GetReceiveCanData(can250, receive, canLen);
    for(int i=0; i< 1; i++){
        for(int j=0; j<8; j++){
            testRead[j] = receive[i].Data[j];
        }
    }
    return testRead;
}

unsigned char steer[8];
unsigned char *steer_point = new unsigned char[8];
extern "C"  unsigned char *readSteer(){
    CAN_OBJ steer_receive[10];    
    InitCANOBJ(steer_receive,10);
    int canLen = 0;
    int haveBrake = 0;
    while(!haveBrake){//1.1
        while(canLen <=0){
            canLen=GetReceiveCanNum(can250);
        }
        GetReceiveCanData(can250, steer_receive, canLen);
        for(int i=canLen - 1; i >=0; i--){//1.1.1
            if(steer_receive[i].ID == 0x401){//000
                haveBrake = 1;
                for(int j=0;j<8;j++){
                    steer_point[j] = steer_receive[i].Data[j];
                }
                //break;
                return steer_point;
            }//000
        }//1.1.1
    }//1.1
    return steer_point;
}

extern "C"  void sendBrake(unsigned char control_mode, unsigned char control_depth){
    CAN_OBJ send_brake[1];
    InitCANOBJ(send_brake,1);
    for(int i=0;i<1;i++){
        send_brake[0].ID = 0x99;
        send_brake[0].ExternFlag = 0;//4he0
        send_brake[0].RemoteFlag = 0;//2he0
        send_brake[0].DataLen = 8;
        send_brake[0].Data[0] = control_mode;
        send_brake[0].Data[1] = control_depth;
        send_brake[0].Data[2] = 0x00;
        send_brake[0].Data[3] = 0x00;
        send_brake[0].Data[4] = 0x00;
        send_brake[0].Data[5] = 0x00;
        send_brake[0].Data[6] = 0x00;
        send_brake[0].Data[7] = 0x00;
    }
    SendCanData(can250, send_brake, 1);
}

extern "C"  void sendGun(unsigned char control_mode, unsigned char control_depth){
    CAN_OBJ send_gun[1];
    InitCANOBJ(send_gun,1);
    for(int i=0;i<1;i++){
        send_gun[0].ID = 0x199;
        send_gun[0].ExternFlag = 0;//4he0
        send_gun[0].RemoteFlag = 0;//2he0
        send_gun[0].DataLen = 8;
        send_gun[0].Data[0] = control_mode;
        send_gun[0].Data[1] = control_depth;
        send_gun[0].Data[2] = 0x00;
        send_gun[0].Data[3] = 0x00;
        send_gun[0].Data[4] = 0x00;
        send_gun[0].Data[5] = 0x00;
        send_gun[0].Data[6] = 0x00;
        send_gun[0].Data[7] = 0x00;
    }
    SendCanData(can250, send_gun, 1);
}

extern "C"  void sendSteer(unsigned char control_mode, unsigned char steer_h, unsigned char steer_l,unsigned char calib){
    CAN_OBJ send_gun[1];
    InitCANOBJ(send_gun,1);
    for(int i=0;i<1;i++){
        send_gun[0].ID = 0x469;
        send_gun[0].ExternFlag = 0;//4he0
        send_gun[0].RemoteFlag = 0;//2he0
        send_gun[0].DataLen = 8;
        send_gun[0].Data[0] = control_mode;
        send_gun[0].Data[1] = 0x74;
        send_gun[0].Data[2] = 0x94;
        send_gun[0].Data[3] = steer_h;
        send_gun[0].Data[4] = steer_l;
        send_gun[0].Data[5] = calib;
        send_gun[0].Data[6] = 0xb7;
        send_gun[0].Data[7] = control_mode ^ 0x74 ^ 0x94 ^ steer_h ^ steer_l ^ calib ^ 0xb7;
    }
    SendCanData(can250, send_gun, 1);
}

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
    InitCANOBJ(receive, 50);
}
