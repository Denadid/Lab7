#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <pthread.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <iostream>
#include <string>

using namespace std;
//Client

int main(int argc,char* argv[])
{
    
    int socketD=socket(AF_INET,SOCK_STREAM,0);\
    printf("socket = %d\n",socketD);
    sockaddr_in myAddr;
    int cons = 0;
    string message = "";
    char mes[100];
    //string kuku = "Hello Server i am client";
    myAddr.sin_family=AF_INET;
    myAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
	myAddr.sin_port        = htons(4567);
    cout<<"if you want to exit, input = 999"<<endl;
    if(connect(socketD,(const struct sockaddr*)&myAddr,sizeof(myAddr))==-1)
        {
            cout<<"Exiting"<<endl;
            exit(0);
        }
    while (cons != 999)
    {
        cout<<"Input ID Babuin"<<endl;
        cin>>cons;
        cout<<endl;
        
            
        int err=send(socketD,(const void*)&cons,sizeof(int),0);
        recv(socketD,&mes,sizeof(mes),0);
        cout<<mes<<endl<<endl<<endl;
    }
    
    
    return 0;
}