import socket
import threading
import sqlite3
import sys


HOST = '127.0.0.1'
PORT = int(sys.argv[1])


def create_database():
    conn = sqlite3.connect('record.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
            (UID INTEGER PRIMARY KEY AUTOINCREMENT,
            username NOT NULL UNIQUE,
            email    TEXT    NOT NULL,
            password   TEXT     NOT NULL
             )''')

    c.execute('''CREATE TABLE IF NOT EXISTS  list
           (UID INTEGER PRIMARY KEY AUTOINCREMENT,
            username NOT NULL 
           )''')

    
def delete_database():
    conn = sqlite3.connect('record.db')
    c=conn.cursor()
    c.execute("DROP TABLE users")
    c.execute("DROP TABLE list")


def udp_job():
    while True:
        indata,addr = udp_s.recvfrom(1024)
        command=indata.decode().split()
        if command[0]=='register':
            result=register(command)
        elif command[0]=='whoami':
            pos=indata.decode().index("&")
            id=int(indata.decode()[pos+1:])
            result=whoami(id)
        
        #outdata= 'echo '+indata.decode()
        #print(indata.decode())
        udp_s.sendto(result.encode(),addr)    
    #udp_s.close()
        
        
        
def TCP_socket():
    while True:
        conn, addr = tcp_s.accept()
        print("New connection.")
        tcp_thread=threading.Thread(target=tcp_job,args=(conn,))
        tcp_thread.start()


def register(indata):
    #data=indata.split()
    if len(indata)!=4:
        return "Usage register <username> <email> <password>"
    else:
        conn = sqlite3.connect('record.db')
        c=conn.cursor()
        tmp=c.execute("SELECT count(*) from users where username==(?)",(indata[1],))
        cnt=tmp.fetchall()
        if cnt[0][0]==0:
             c.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",(indata[1],indata[2],indata[3]))
             conn.commit()
             return "Register successfully."
        else :
            #print("insert failed")
            return "Username is already used."

def login(indata,status):
    if len(indata)!=3:
        return ("Usage login <username> <password>",status,-1)
    else:
        if status==1:
            return ("Please logout first.",status,-1)
        else:
            conn = sqlite3.connect('record.db')
            c=conn.cursor()
            sql1="SELECT count(*) from users where username==(?) and password==(?)"
            task1=(indata[1],indata[2],)
            tmp2=c.execute(sql1,task1)
            cnt2=tmp2.fetchall()
            if cnt2[0][0]==1:
                status=1
                c.execute("INSERT INTO list (username) VALUES (?)",(indata[1],))
                conn.commit()
                tmp3=c.execute("SELECT UID from list where username==(?) order by UID DESC LIMIT 1",(indata[1],))
                id=tmp3.fetchall()
                return ("Welcome, "+indata[1],status,id[0][0])
            else :
                return ("Login failed.",status,-1)
        

       
def logout(status,id):
    if status==0:
        return "Please login first",status
    else :
        conn = sqlite3.connect('record.db')
        c=conn.cursor()
        tmp=c.execute("SELECT username from list where UID==(?)",(id,))
        user=tmp.fetchall()
        #print(user[0][0])
        c.execute("DELETE from list where UID==(?)",(id,))
        conn.commit()
        status=0
        return "Bye, "+user[0][0],status


def whoami(id):
    conn = sqlite3.connect('record.db')
    c=conn.cursor()
    tmp=c.execute("SELECT count(*) from list where UID==(?)",(id,))
    cnt=tmp.fetchall()
    if cnt[0][0]==0:
        return "Please login first."
    else:
        tmp2=c.execute("SELECT username from list where UID==(?)",(id,))
        name=tmp2.fetchall()
        return name[0][0]


def list_user():
    conn = sqlite3.connect('record.db')
    c=conn.cursor()
    tmp=c.execute("SELECT username, email from users ")
    res=tmp.fetchall()
    str1="Name Email "
    #print("list_user")
    for i in res:
        str1+="\n"
        for j in i:
            str1=str1+j+" "

        
    
    #for i in res:
    #    print(res[i][0]+" "+res[i][1])
    #    str1+=res[i][0]+" "+res[i][1]+"\n"
    #print(res[0])
    return str1

    


def tcp_job(conn):
    status = 0  #logout
    id=-1
    while True:
        indata = conn.recv(1024)
        #print(indata.decode())
        command=indata.decode().split()
        if command[0]=='login':
            result=login(command,status)
            status=result[1]
            if result[2]>0:
                id=result[2]
                conn.sendall((str(result[0])+"."+"&"+str(result[2])).encode())
            else:
                conn.sendall(str(result[0]).encode())
        elif command[0]=='logout':
            result,status=logout(status,id)
            result+="."
            conn.sendall(result.encode())
        elif command[0]=='list-user':
            result=list_user()
            conn.sendall(result.encode())
        elif command[0]=='exit':
            break
                      
    if command[0]=="exit":
            conn.close()
           
       # conn.sendall(result.encode())



#main
#delete_database()    
create_database()

#print("--------------------------------------")
udp_s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udp_s.bind((HOST,PORT))
#    UDP_socket()
UDP_thread=threading.Thread(target=udp_job)
UDP_thread.start()

tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_s.bind((HOST, PORT))
tcp_s.listen(5)
TCP_thread=threading.Thread(target=TCP_socket)
TCP_thread.start()
#TCP_socket()




         





            
           
            
        

        
