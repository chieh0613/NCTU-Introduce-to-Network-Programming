#! /usr/bin/python3
import threading
import socket
import select
import sys
import time
import sqlite3

HOST = sys.argv[1]
PORT = int(sys.argv[2])



def TCP_socket(tcp_chat_server):
    global  input_server, not_std_input
    while True:
        readable, _, _ = select.select(accept_client, [], [], 0.1)
        if close_accept == 1:
            break
        for chat_server in readable:
            client_socket, chat_addr = chat_server.accept()
            input_server.append(client_socket) 
            not_std_input.append(client_socket)
    

def detach_thread():
    global attach_chatroom, input_server, not_std_input,chat_record
    while True:
        if attach_chatroom == 1:
            break

        readable, _, _ = select.select(input_server, [], [], 0.1)
        for i in readable:
            if i != sys.stdin:
                data = i.recv(4096)
                tmp = data.decode()
                if 'sys' in  tmp and 'join us' in tmp: #someone join the chatroom
                    for all_client in not_std_input:
                        if all_client != i:
                            all_client.sendall(data)
                        else:
                            msg_len = len(chat_record)
                            last_three_msg = ''
                            if msg_len >3:
                                for temp in chat_record[len(chat_record)-3:]:
                                    last_three_msg+=temp+'\n'
                            else:
                                for temp in chat_record:
                                    last_three_msg+=temp+'\n'

                            last_three_msg.strip()
                            all_client.sendall(last_three_msg.encode())
                elif 'sys' in tmp and 'leave us' in tmp:  #someone leave the chatroom
                    for all_client in not_std_input:
                        if all_client == i:  #close socket
                            input_server.remove(all_client)  #delete the socket in the server list
                            not_std_input.remove(all_client)
                            all_client.close()
                        else:
                            all_client.sendall(tmp.encode())
                else:
                    chat_record.append(tmp.strip())
                    for all_client in not_std_input:
                        if all_client != i:
                            all_client.sendall(data)         
                        

                        


def chatroom_server(name,attach,restart):
    print('*****************************\n** Welcome to the chatroom **\n*****************************')
    global not_std_input, input_server,chat_record,attach_chatroom,close_accept
    back_to_bbs = 0
    if attach == 1:
        msg_len = len(chat_record)
        last_three_msg = ''
        if msg_len >3:
            for temp in chat_record[len(chat_record)-3:]:
                last_three_msg+=temp+'\n'
        else:
            for temp in chat_record:
                last_three_msg+=temp+'\n'

        print(last_three_msg.strip())
        attach_chatroom = 1

    if restart == 1:
        msg_len = len(chat_record)
        last_three_msg = ''
        if msg_len >3:
            for temp in chat_record[len(chat_record)-3:]:
                last_three_msg+=temp+'\n'
        else:
            for temp in chat_record:
                last_three_msg+=temp+'\n'

        print(last_three_msg.strip())

    while True:
        
        readable, _, _ = select.select(input_server, [], [], 0.1)
        for i in readable:
            if i == sys.stdin:
                tmp = i.readline()
                if tmp.strip() == 'detach':
                    attach_chatroom = 0
                    detach=threading.Thread(target=detach_thread)
                    detach.start()
                    print('Welcome back to BBS.')
                    back_to_bbs = 1
                    break
                elif tmp.strip() == 'leave-chatroom':
                    send_time = str(time. strftime ( "%H:%M" ))    

                    close_accept = 1
                    send_data ='sys['+send_time+']: the chatroom is close. '
                    for all_client in not_std_input:
                        all_client.sendall(send_data.encode())
                    input_server = [sys.stdin]
                    not_std_input = []
                    #accept_client = []
                    send_to_bbs = 'leave-chatroom '+name
                    tcp_s.sendall(send_to_bbs.encode())

                    back_to_bbs = 1
                    print('Welcome back to BBS.')
                    break

                else:                            
                    send_time = str(time. strftime ( "%H:%M" ))    
                    send_data = name +'['+send_time+']:'+tmp
                    chat_record.append(send_data.strip())
                    for all_client in not_std_input:
                        all_client.sendall(send_data.encode())
                
            else:
                data = i.recv(4096)
                tmp = data.decode()
                if 'sys' in  tmp and 'join us' in tmp: #someone join the chatroom
                    for all_client in not_std_input:
                        if all_client != i:
                            all_client.sendall(data)
                        else:
                            msg_len = len(chat_record)
                            last_three_msg = ''
                            if msg_len >3:
                                for temp in chat_record[len(chat_record)-3:]:
                                    last_three_msg+=temp+'\n'
                            else:
                                for temp in chat_record:
                                    last_three_msg+=temp+'\n'

                            last_three_msg.strip()
                            all_client.sendall(last_three_msg.encode())

                elif 'sys' in tmp and 'leave us' in tmp:  #someone leave the chatroom
                    for all_client in not_std_input:
                        if all_client == i:  #close socket
                            #print(not_std_input)
                            input_server.remove(all_client)  #delete the socket in the server list
                            not_std_input.remove(all_client)
                            #print(not_std_input)
                            all_client.close()
                        else:
                            all_client.sendall(tmp.encode())
                                                                              
                else:
                    chat_record.append(tmp.strip())
                    for all_client in not_std_input:
                        if all_client != i:
                            all_client.sendall(data)                           
                print(data.decode().strip())
        if back_to_bbs == 1:
            break

                

            
def chatroom_client(ip,port,name):
    
    print('*****************************\n** Welcome to the chatroom **\n*****************************')

   
    tcp_chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_chat_client.connect((ip, port))
    input_client.append(tcp_chat_client)
    welcome_time = str(time. strftime ( "%H:%M" ))
    welcome_msg = 'sys['+welcome_time+']:'+name+' join us.'
    tcp_chat_client.sendall(welcome_msg.encode())
    client_leave = 0
    
      
    while True:
        readable, _, _ = select.select(input_client, [], [], 0.1)
        for i in readable:
                if i == sys.stdin:
                    tmp = i.readline()        
                    if tmp.strip() == 'leave-chatroom':
                        send_time = str(time. strftime ( "%H:%M" ))
                        send_data = 'sys[' + send_time + ']:' + name + ' leave us.'
                        tcp_chat_client.sendall(send_data.encode())
                        #print(tcp_chat_client)
                        input_client.remove(tcp_chat_client) #remove the socket in the client list
                        tcp_chat_client.close()
                        client_leave = 1
                        print('Welcome back to BBS.')
                        break

                    send_time = str(time. strftime ( "%H:%M" ))
                    send_data = name +'['+send_time+']:'+tmp
                    tcp_chat_client.sendall(send_data.encode())

                else:
                    data = i.recv(4096)
                    if 'the chatroom is close' in data.decode() and 'sys' in data.decode() :
                        input_client.remove(tcp_chat_client)
                        tcp_chat_client.close()
                        client_leave = 1
                        print(data.decode().strip())
                        print('Welcome back to BBS.')
                        break
                    print(data.decode().strip())
        if client_leave == 1:
            break



    


def start_tcp(inputmsg,command):  
    
        
    tcp_s.sendall(inputmsg.encode())
    #print(inputmsg)
    global status,tcp_chat_server
    if command!="exit":
        indata = tcp_s.recv(4096)
        if command=="login":
            if "&"  in indata.decode():
                pos=indata.decode().index("&")
                str1=""
                global id
                id=int(indata.decode()[pos+1:])
                str1=indata.decode()[:pos]
                print(str1)
                global name
                name = indata.decode()[9:pos - 1]
                status = 1      
            else:
                print(indata.decode())
        elif command == 'logout':
            outmsg = indata.decode()
            if (outmsg[len(outmsg)-1] == '&'):
                print(outmsg.strip('&'))
            else:
                status = 0
                print(indata.decode())

        else:
            if 'start to create chatroom...' in indata.decode():
                global create
                create = 1
                tmp = indata.decode().split('&')
                print(tmp[0])

                global accept_client

                
                tcp_chat_server.bind((tmp[1],int(tmp[2])))
                tcp_chat_server.listen(5)
                accept_client.append(tcp_chat_server) 
                TCP_thread=threading.Thread(target=TCP_socket,args=(tcp_chat_server,))
                TCP_thread.start()

                chatroom_server(name,0,0)
            elif 'connection to chatroom server' in indata.decode():
                tmp = indata.decode().split('&')
                #print(tmp)
                chatroom_client(tmp[1], int(tmp[2]), name)
            elif 'restart chatroom server' in indata.decode():
                global close_accept
                close_accept = 0
                TCP_thread=threading.Thread(target=TCP_socket,args=(tcp_chat_server,))
                TCP_thread.start()
                chatroom_server(name, 0,1)
                
            else:          
                print(indata.decode())
    

def start_udp(inputmsg,command,id): 
    if command=="whoami" or command == 'list-chatroom':
        inputmsg=inputmsg+" & "+str(id)
    udp_s.sendto(inputmsg.encode(),(HOST,PORT))
    indata=udp_s.recvfrom(1024)
    print(indata[0].decode())
    #udp_s.close()




print("********************************\n** Welcome to the BBS server. **\n********************************")
id=-1 
name = ''
chat_record = []
input_server = [sys.stdin]
input_client = [sys.stdin]
not_std_input = []
accept_client = []
count_msg_num = 0
status = 0  #logout
create = 0  # not create chatroom
attach_chatroom = 0
close_accept = 0

tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_s.connect((HOST, PORT))
udp_s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
tcp_chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


while True:
    inputmsg=input("% ")
    command=inputmsg.split()
   
    if command[0]=="register" or command[0]=="whoami" or  command[0] == 'list-chatroom':
        start_udp(inputmsg,command[0],id)
    elif command[0]=="login" or  command[0]=="logout" or command[0]=="list-user" :
        start_tcp(inputmsg,command[0])
    elif command[0]=="create-board" or command[0]=="list-board" or command[0]=="create-post" or command[0]=="list-post" or command[0]=="read" or command[0]=="delete-post" or command[0]=="update-post" or command[0]=="comment":
        start_tcp(inputmsg,command[0])
    elif command[0] == 'create-chatroom' or command[0] == 'join-chatroom' or command[0]=='restart-chatroom':
        start_tcp(inputmsg, command[0])
    elif command[0] == 'attach':
        if status == 0:
            print('Please login first.')
        elif create == 0:
            print('Please create-chatroom first.')
        elif close_accept == 1:
            print('Please restart-chatroom first.')    
        else:
            chatroom_server(name,1,0)
            

        
        
    elif command[0]=="exit":
        start_tcp(inputmsg,command[0])
        break

tcp_s.close()
udp_s.close()    
    






    
