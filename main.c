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
int main(void)
{
    QueueInit();
    MCUUartInit();
    MCUUartListen();

    CAN_OBJ canRecv[10];//设置足够大小接收数据
    CAN_OBJ canSend[1];//每次发送一帧数据

    while(1)
    {
        int canLen = 0;

        InitCANOBJ(canRecv,10);//初始化
        InitCANOBJ(canSend,1);//初始化

        canLen=GetReceiveCanNum(can500);
        if(canLen > 0)
        {
            GetReceiveCanData(can500, canRecv, canLen);
            for(int i=0;i < canLen;i++)
            {
                char tmp = 0;
                for(int j=0;j<8;j++)
                {
                    if(canRecv[i].ID==0x82)//读取第一帧数据
                        tmp = canRecv[i].Data[j];//读取第j字节的数据
                    else if(canRecv[i].ID==0x7f)//读取第二帧数据
                        tmp = canRecv[i].Data[j];//读取第j字节的数据
                }
            }
        }

        for(int i=0;i<1;i++)//每次只发送一帧数据
        {
            canSend[i].ID = 0x81;
            canSend[i].RemoteFlag = 0;
            canSend[i].ExternFlag = 0;
            canSend[i].DataLen = 8;

            //字节0赋值
            canSend[i].Data[0]=0x40;//智能控制数据发送
            //字节1赋值,自动驾驶
            canSend[i].Data[1]=0x03;
            //字节2赋值，当前档位（高4位），油门(低4位)
            canSend[i].Data[2]=0x2;
            //字节3赋值,油门
            canSend[i].Data[3]=0;
            //字节4赋值，转向角度高位
            canSend[i].Data[4]=0;
            //字节5赋值，转向角度低位
            canSend[i].Data[5]=0;
            //字节6赋值，制动档位
            canSend[i].Data[6]=0;
            //字节7赋值，保留
        }
        SendCanData(can500,canSend,1);//发送帧
    }
}
