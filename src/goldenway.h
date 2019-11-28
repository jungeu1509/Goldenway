/**
*
* Team : Oh! Friends
* Project : Golden Way
* File : goldenway.h
* Author : Eunwoo Jung
* Date : 2019.11.26
* Brief : integrate.cpp의 헤더파일
*
*/

#ifndef __goldenway_H_
#define __goldenway_H_

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/signal.h>
#include <sys/ioctl.h>
#include <sys/poll.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <wait.h>
#include <errno.h>
#include <time.h>
#include <termios.h>

void itoa(int num, char *str);
void ixtoa(int num, char *str);

void itoa(int num, char *str)
{
    int i=0;
    int radix =10;
    int deg=1;
    int cnt=0;

    while(1)
    {
        if((num/deg)>0){cnt++;}
        else break;
        deg *= radix;
    }
    deg /= radix;
    for(i=0;i<cnt;i++)
    {
        *(str+1) = num/deg + '0';
        num -= ((num/deg)*deg);
        deg /= radix;
    }
    *(str+i) = '\0';
    return;
}

void ixtoa(int num, char *str)
{
    int mod;
    char change[]={'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
    if(num<0||num>0xFF)
    {
        printf("\nerror : out of range at ixtoa num\n");
        *str = 'F';
        *(str+1) = 'F';
        return;
    }
    mod = num % 16;
    num = num / 16;
    *str = change[num];
    *(str+1) = change[mod];
    return;
}

#endif
