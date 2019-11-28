/**
*
* Team : Oh! Friends
* Project : Golden Way
* File : integrate.cpp
* Author : Eunwoo Jung
* Date : 2019.11.26
* Brief : 사이렌소리와 긴급차량 이미지를 받아와 통합처리하는 코드
*
*/

#include "goldenway.h"
#include <iostream>

using namespace std;

#define none 0
#define siren 1
#define ambulance 1
#define firetruck 2
#define complication 3
#define normal 3
#define left 1
#define right 2

int sir_pd, img_pd, show_pd;
int n, err, boot_cnt;
int killmain;
int sir_thread_state, img_thread_state, show_thread_state;
int sirpy_thread_state, imgpy_thread_state, showpy_thread_state;

char sirmsg[10] = {0,};
char imgmsg[10] = {0,};
char showmsg[14] = {0,};

pthread_t tid[6];
pthread_mutex_t Mutex_sir;
pthread_mutex_t Mutex_img;
pthread_mutex_t Mutex_show;
pthread_mutex_t Mutex_cnt;
pthread_cond_t cond;

void *sir_thread(void *arg);
void *img_thread(void *arg);
void *show_thread(void *arg);
void *sirpy_thread(void *arg);
void *imgpy_thread(void *arg);
void *showpy_thread(void *arg);

int main(void)
{
    char temp[11] = {0,};
    int i;
    int sir_state, sir_detect, sir_end=0;
    int img_state, img_detect, position, img_end=0;
    int state, direction, exception=0;
    int *checksum_p;

    pthread_mutex_init(&Mutex_img, NULL);
    pthread_mutex_init(&Mutex_sir, NULL);
    pthread_mutex_init(&Mutex_show, NULL);
    pthread_mutex_init(&Mutex_cnt, NULL);
    pthread_cond_init(&cond, NULL);

    sir_end = 0;
    img_end = 0;
    boot_cnt = 0;

    imgpy_thread_state = pthread_create(&tid[4], NULL, imgpy_thread, (void *)5);
    if(imgpy_thread_state != 0)
    {
      perror("imagepy thread create!\n");
      exit(1);
    }
    sirpy_thread_state = pthread_create(&tid[5], NULL, sirpy_thread, (void *)6);
    if(sirpy_thread_state != 0)
    {
      perror("sirenpy thread create!\n");
      exit(1);
    }

    show_thread_state = pthread_create(&tid[2], NULL, show_thread, (void *)3);
    if(show_thread_state != 0)
    {
      perror("show thread create!\n");
      exit(1);
    }

    sleep(2);
    while(1)
    {
      pthread_mutex_lock(&Mutex_cnt);
      if(boot_cnt==2)
      {
        pthread_mutex_unlock(&Mutex_cnt);
        break;
      }
      pthread_mutex_unlock(&Mutex_cnt);
    }


    sir_thread_state = pthread_create(&tid[0], NULL, sir_thread, (void *)1);
    if(sir_thread_state != 0)
    {
      perror("sir thread create!\n");
      exit(1);
    }
    img_thread_state = pthread_create(&tid[1], NULL, img_thread, (void *)2);
    if(img_thread_state != 0)
    {
      perror("img thread create!\n");
      exit(1);
    }
    showpy_thread_state = pthread_create(&tid[3], NULL, showpy_thread, (void *)4);
    if(showpy_thread_state != 0)
    {
      perror("showpy thread create!\n");
      exit(1);
    }

    while(1)
    {
      temp[2]='\0';
      pthread_mutex_lock(&Mutex_sir);
      strncpy(temp, &sirmsg[2], 2);
      sir_state = strtol(temp, NULL, 16);
      strncpy(temp, &sirmsg[4], 2);
      sir_detect = strtol(temp, NULL, 16);
      pthread_mutex_unlock(&Mutex_sir);

      pthread_mutex_lock(&Mutex_img);
      strncpy(temp, &imgmsg[2], 2);
      img_state = strtol(temp, NULL, 16);
      strncpy(temp, &imgmsg[4], 2);
      img_detect = strtol(temp, NULL, 16);
      strncpy(temp, &imgmsg[6], 2);
      position = strtol(temp, NULL, 16);
      pthread_mutex_unlock(&Mutex_img);

      if((img_state == 0xF3)&&(img_end ==0))
      {
          exception = 0xF3;
          cout << "exception detected\n";
          img_end = 0xF;
      }
      if((sir_state == 0xF2)&&(sir_end ==0))
      {
          exception = 0xF2;
          cout << "exception detected\n";
          sir_end = 0xF;
      }
      if((img_state==0xF3)&&(img_end ==0xF))
      {
        img_state = 0xFF;
        img_end = 0xFF;

        if(unlink("./IMG_MSG") == -1)
        {
            perror("Failed to remove img fifo");
        }
      }
      if((sir_state==0xF2)&&(sir_end == 0xF))
      {
        sir_state = 0xFF;
        sir_end = 0xFF;

        if(unlink("./SIR_MSG") == -1)
        {
            perror("Failed to remove sir fifo");
        }
      }
      if((img_end == 0xFF)&&(sir_end == 0xFF))
      {
        killmain = 0xFF;
      }

      if((0xFF == img_end)&&(0xFF == sir_end))
      {
        exception = 0xFF;
        exit(0);
      }

      if(img_detect == ambulance)
      {
        if(sir_detect == siren){state = ambulance;}
        else{state = normal;}
      }
      else if(img_detect == firetruck)
      {
        if(sir_detect == siren){state = firetruck;}
        else{state = normal;}
      }
      else if(img_detect == none)
      {
        if(sir_detect == siren){state = none;}
        else{state = normal;}
      }
      else{state = none;}

      if(position == 0){direction = normal;}
      else if(position == 1){direction = right;}
      else if(position == 2){direction = left;}
      else{direction = none;}

      if(img_end == 0xFF){exception = 0xF3;}
      else if(sir_end == 0xFF){exception = 0xF2;}

      pthread_mutex_lock(&Mutex_show);
      strcpy(showmsg, "AA");
      ixtoa(state, &showmsg[2]);
      ixtoa(direction, &showmsg[4]);
      ixtoa(exception, &showmsg[6]);
      strcpy(&showmsg[8], "00");
      strcpy(&showmsg[10], "55\0");
      pthread_mutex_unlock(&Mutex_show);
    }
    pthread_exit(0);
    return 0;
}

void *sir_thread(void *arg)
{
  char temp[10] = {0,};

  while((strncmp("F2", &sirmsg[2], 2) != 0))
  {
    if ((sir_pd = open("./SIR_MSG", O_RDONLY)) == -1)
    {
        perror("open");
        exit(1);
    }
    pthread_mutex_lock(&Mutex_sir);
    n=read(sir_pd, temp, 10);
    memset(sirmsg, '\n', sizeof(sirmsg));
    strncpy(sirmsg, temp, 10);
    if(n == -1)
    {
       perror("read");
       exit(1);
    }
    sleep(1);
    pthread_mutex_unlock(&Mutex_sir);
    printf("\n");
    write(1, "\n", 1);

    close(sir_pd);
  }
  pthread_exit(0);
}

void *img_thread(void *arg)
{
  char temp[10] = {0,};

  while ((strncmp("F3", &imgmsg[2], 2) != 0))
  {
    if ((img_pd = open("./IMG_MSG", O_RDONLY)) == -1)
    {
        perror("open");
        exit(1);
    }

    pthread_mutex_lock(&Mutex_img);
    n=read(img_pd, temp, 10);
    memset(imgmsg, '\n', sizeof(imgmsg));
    strncpy(imgmsg, temp, 10);

    if(n == -1)
    {
       perror("read");
       exit(1);
    }
    sleep(1);

    pthread_mutex_unlock(&Mutex_img);
    printf("\n");
    write(1, "\n", 1);

    close(img_pd);
  }
  cout << "img thread exit\n";
  pthread_exit(0);
}

void *show_thread(void *arg)
{
  char temp[14] = {0,};
  int killtemp = 0;

  if(mkfifo("./show_MSG", 0666) == -1)
  {
      perror("mkfifo");
      exit(1);
  }

  while (1)
  {
    memset(temp, '\n', sizeof(temp));
    if((show_pd = open("./show_MSG", O_WRONLY )) == -1)
    {
        perror("open");
        exit(1);
    }

    pthread_mutex_lock(&Mutex_show);
    n = write(show_pd, showmsg, strlen(showmsg));
    if (n == -1)
    {
        perror("write");
        exit(1);
    }
    cout<< "\n Send to show" << showmsg <<"\n";
    close(show_pd);
    sleep(1);

    if((killtemp == 0xFF)&&(killmain == 0xFF))
    {
      cout<< "\nAll thread killed _ killing main\n";
      sleep(5);

      if(unlink("./show_MSG") == -1)
      {
          perror("Failed to remove show fifo");
      }
      cout << "end show_msg fifo\n";

      break;
    }
    else if(killmain == 0xFF)
    {
      killtemp = killmain;
    }
    pthread_mutex_unlock(&Mutex_show);
    while(1)
    {
      pthread_mutex_lock(&Mutex_cnt);
      if(boot_cnt==3);
      {
        pthread_mutex_unlock(&Mutex_cnt);
        break;
      }
      pthread_mutex_unlock(&Mutex_cnt);
    }
  }
  cout << "main show thread exit\n";
  pthread_exit(0);
}

void *showpy_thread(void *arg)
{
    while(1)
    {
      pthread_mutex_lock(&Mutex_cnt);
      if(boot_cnt==3);
      {
        pthread_mutex_unlock(&Mutex_cnt);
        break;
      }
      pthread_mutex_unlock(&Mutex_cnt);
    }
    sleep(1);
    system("python3 $HOME/goldenway/show.py");
}

void *imgpy_thread(void *arg)
{
    pthread_mutex_lock(&Mutex_cnt);
    boot_cnt++;
    pthread_mutex_unlock(&Mutex_cnt);
    system("python3 $HOME/goldenway/goldenway_img.py");
}

void *sirpy_thread(void *arg)
{
    pthread_mutex_lock(&Mutex_cnt);
    boot_cnt++;
    pthread_mutex_unlock(&Mutex_cnt);
    system("python3 $HOME/goldenway/goldenway_sir.py");
}
