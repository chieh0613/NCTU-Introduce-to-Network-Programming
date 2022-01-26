#! /usr/bin/python3

import socket
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])



def start_tcp(inputmsg,command):  
      
    tcp_s.sendall(inputmsg.encode())
    #print(inputmsg)
    if command!="exit":
        indata = tcp_s.recv(1024)
        if command=="login":
            if "&"  in indata.decode():
                pos=indata.decode().index("&")
                str1=""
                global id
                id=int(indata.decode()[pos+1:])
                str1=indata.decode()[:pos]

                print(str1)
            else:
                print(indata.decode())
                
        else:      
            print(indata.decode())
    

def start_udp(inputmsg,command,id): 
    if command=="whoami":
        inputmsg=inputmsg+" & "+str(id)
    udp_s.sendto(inputmsg.encode(),(HOST,PORT))
    indata=udp_s.recvfrom(1024)
    print(indata[0].decode())
    #udp_s.close()




print("********************************\n** Welcome to the BBS server. **\n********************************")

tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_s.connect((HOST, PORT))
udp_s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

id=-1 
while True:
    inputmsg=input("% ")
    #print(inputmsg)
    command=inputmsg.split()

    if command[0]=="register" or command[0]=="whoami":
        start_udp(inputmsg,command[0],id)
    elif command[0]=="login" or  command[0]=="logout" or command[0]=="list-user":
        start_tcp(inputmsg,command[0])
    elif command[0]=="exit":
        start_tcp(inputmsg,command[0])
        break

tcp_s.close()
udp_s.close()    
    




    
         



    
