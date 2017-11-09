#ifndef __QUEUE_H_
#define __QUEUE_H_

#include <stdio.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#ifdef __cplusplus
extern  "C" {
#endif

#define OK 1
#define ERROR 0
#define TRUE 1
#define FALSE 0



#define QUEUESIZE 50000

#define Devices 5



typedef unsigned char ElemType ;


typedef int State;


typedef struct _CircleQueue
{
    ElemType data[QUEUESIZE];
    State front;
    State rear;
    State count;
    pthread_spinlock_t spinlock;
}CircleQueue;



extern CircleQueue ReadQueue[Devices],WriteQueue[Devices];
extern CircleQueue ReadBuf;
State InitQueue(CircleQueue *queue);
State EnQueue(CircleQueue *queue,unsigned char * e,  int len);
unsigned char *DeQueue(CircleQueue *queue,  int len);
State GetLength(CircleQueue *queue);
State Print(CircleQueue *q);
void QueueInit(void);
State DeleteQueue(CircleQueue *queue, int len);
#ifdef __cplusplus
}
#endif
#endif
