import socket
import threading
import sqlite3
import sys
import datetime


HOST = '127.0.0.1'
PORT = int(sys.argv[1])

board_list=[]
post_list=[]
s_n=0


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

    c.execute('''CREATE TABLE IF NOT EXISTS  board
           (idx INTEGER PRIMARY KEY AUTOINCREMENT,
            username  NOT NULL,
           boardname NOT NULL UNIQUE 
           )''')

    
def delete_database():
    conn = sqlite3.connect('record.db')
    c=conn.cursor()
    c.execute("DROP TABLE users")
    c.execute("DROP TABLE list")
    c.execute("DROP TABLE board")


def udp_job():
    while True:
        indata,addr = udp_s.recvfrom(4096)
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

def login(indata,status,author):
    if len(indata)!=3:
        return ("Usage login <username> <password>",status,-1),author
    else:
        if status==1:
            return ("Please logout first.",status,-1),author
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
                author=indata[1]
                return ("Welcome, "+indata[1],status,id[0][0]),author
            else :
                return ("Login failed.",status,-1),author
        

       
def logout(status,id,author):
    if status==0:
        return "Please login first",status,author
    else :
        conn = sqlite3.connect('record.db')
        c=conn.cursor()
        tmp=c.execute("SELECT username from list where UID==(?)",(id,))
        user=tmp.fetchall()
        #print(user[0][0])
        c.execute("DELETE from list where UID==(?)",(id,))
        conn.commit()
        status=0
        author="logout"
        return "Bye, "+user[0][0],status,author


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

    return str1



def create_board(indata,status,id,author):
    if len(indata)!=2:
        return "Usage create-board <name>",status,author
    elif status==0:
        return "Please login first.",status,author
    else:
        conn = sqlite3.connect('record.db')
        c=conn.cursor()
        tmp=c.execute("SELECT count(*) from board where boardname==(?)",(indata[1],))
        cnt=tmp.fetchall()
        if cnt[0][0]==1:
            return "Board already exists.",status,author    
        else :
            tmp2=c.execute("SELECT username from list where UID==(?)",(id,))
            user=tmp2.fetchall()
            c.execute("INSERT INTO board (username,boardname) VALUES (?,?)",(user[0][0],indata[1],))
            conn.commit()
            author=user[0][0]
            global board_list
            global post_list
            board_list.append(indata[1])
            mutex.acquire()
            post_list.append([indata[1]])
            mutex.release()
            return "Create board successfully.",status,author


def list_board(indata):
    if len(indata)!=1:
        return "Usage list-board"
    conn = sqlite3.connect('record.db')
    c=conn.cursor()
    tmp=c.execute("SELECT idx, boardname,username from board ")
    res=tmp.fetchall()
    str1="Index Name Moderator "
    #print("list_user")
    for i in res:
        str1+="\n"
        for j in i:
            str1=str1+str(j)+" "

    return str1


def create_post(indata,author):
    global board_list
    global post_list
    if '--title' not in indata or '--content' not in indata:
        return "Usage create-post <board-name> --title <title>--content <content>",author
    index_title=indata.index('--title')
    index_content=indata.index('--content')
    if indata[1]=='--title' or index_content-index_title==1 or indata[len(indata)-1]=='--content ' :
        return "Usage create-post <board-name> --title <title>--content <content>",author
    elif author=='logout':
        return "Please login first.",author
    elif indata[1] not in board_list:
        return "Board does not exist.",author
    else:
        title=""
        content=""
        i=index_title+1
        while i<index_content:
            title+=indata[i]+" "
            i+=1
        j=index_content+1
        while j<len(indata):
            k=0
            while k<len(indata[j]):
                if indata[j][k]=='<' and indata[j][k+1]=='b' and indata[j][k+2]=='r' and indata[j][k+3]=='>':
                    content+='\n'
                    k+=4
                else:
                    content+=indata[j][k]
                    k+=1
            content+=" "
            j+=1
   
        global s_n
        s_n+=1

        now=datetime.datetime.now()
        date=str(now.month)+'/'+str(now.day)

        i=0
        mutex.acquire()
        while i<len(post_list):
            if post_list[i][0]==indata[1]:
                post_list[i].append([s_n,title,content,author,date])
                break
            i+=1
        mutex.release()     
        return "Create post successfully.",author

        
def list_post(indata):
    if len(indata)!=2:
        return "Usage list-post <board-name>."
    elif indata[1] not in board_list:
        return "Board does not exist."
    else:
        str1="S/N Title Author Date "
        i=0
        mutex.acquire()
        while i<len(post_list):
            if post_list[i][0]==indata[1]:
                #print(post_list[i][1:])
                j=1
                while j<len(post_list[i]):
                    str1+="\n"+str(post_list[i][j][0])+" "+post_list[i][j][1]+" "+post_list[i][j][3]+" "+post_list[i][j][4]
                    j+=1
                break
            i+=1
        mutex.release()
        
        return str1

def read_post_i(indata):
    if len(indata)!=2:
        return "Usage read <post-S/N>."
    else:
        i=0
        j=1
        find=False
        mutex.acquire()
        while i<len(post_list):
            while j<len(post_list[i]):
                if str(post_list[i][j][0])==indata[1]:
                    find=True #break
                    break
                else :
                    j+=1
            if find==True:
                break
            else:
                i+=1
        mutex.release()
        if find==False:
            return "Post does not exist."
        else: 
            str1=""
            mutex.acquire()
            str1+="Author: "+post_list[i][j][3]+"\n"+"Title: "+post_list[i][j][1]+"\n"+"Date: "+post_list[i][j][4]+"\n--\n"+post_list[i][j][2]+"\n--"
            k=5
            while k<len(post_list[i][j]):
                str1+="\n"+post_list[i][j][k]
                k+=1
            mutex.release()
            return str1

def delete_post(indata,author):
    if len(indata)!=2:
        return "Usage delete-post <post-S/N>."
    elif author=='logout':
        return "Please login first."
    else:
        i=0
        j=1
        find=False
        mutex.acquire()
        while i<len(post_list):
            while j<len(post_list[i]):
                if str(post_list[i][j][0])==indata[1]:
                    find=True #break
                    break
                else :
                    j+=1
            if find==True:
                break
            else:
                i+=1
        mutex.release()
        if find==False:
            return "Post does not exist."
        else:
            mutex.acquire()
            if post_list[i][j][3]!=author:
                mutex.release()
                return "Not the post owner."
            else:
                del post_list[i][j]
                mutex.release() 
                return "Delete successfully."


def update_post(indata,author):
    if indata[1]=="--title" or indata[1]=="--content" or (indata[2]!="--title" and indata[2]!="--content") or indata[len(indata)-1]=="--title" or indata[len(indata)-1]=="--content" :
        return "Usage update-post <post-S/N> --title/content <new>."
    elif author=='logout':
        return "Please login first."
    else:
        i=0
        j=1
        find=False
        mutex.acquire()
        while i<len(post_list):
            while j<len(post_list[i]):
                if str(post_list[i][j][0])==indata[1]:
                    find=True #break
                    break
                else :
                    j+=1
            if find==True:
                break
            else:
                i+=1
        mutex.release()
        if find==False:
            return "Post does not exist."
        else:
            mutex.acquire() 
            if post_list[i][j][3]!=author:
                mutex.release() 
                return "Not the post owner."
            else:
                mutex.release() 
                k=3
                tmp=""
                if indata[2]=="--title":
                    while k<len(indata):
                        tmp+=indata[k]+" "
                        k+=1 
                    mutex.acquire() 
                    post_list[i][j][1]=tmp
                    mutex.release() 
                else:
                    while k<len(indata):
                        m=0
                        while m<len(indata[k]):
                            if indata[k][m]=='<' and indata[k][m+1]=='b' and indata[k][m+2]=='r' and indata[k][m+3]=='>':
                                tmp+='\n'
                                m+=4
                            else:
                                tmp+=indata[k][m]
                                m+=1
                        tmp+=" "
                        k+=1
                    mutex.acquire()
                    post_list[i][j][2]=tmp
                    mutex.release() 
                
                return "Update successfully."

def comment(indata,author):
    if len(indata)<3:
        return "Usage comment <post-S/N> <comment>."
    elif author=='logout':
        return "Please login first."
    else:
        i=0
        j=1
        find=False
        mutex.acquire()
        while i<len(post_list):
            while j<len(post_list[i]):
                if str(post_list[i][j][0])==indata[1]:
                    find=True #break
                    break
                else :
                    j+=1
            if find==True:
                break
            else:
                i+=1
        mutex.release() 
        if find==False:
            return "Post does not exist."
        else:
            k=2
            comment=author+": "
            while k<len(indata):
                comment+=indata[k]+" "
                k+=1
            mutex.acquire()
            post_list[i][j].append(comment)
            mutex.release() 
            return "Comment successfully."

    





def tcp_job(conn):
    status = 0  #logout
    author="logout"
    id=-1
    while True:
        indata = conn.recv(4096)
        #print(indata.decode())
        command=indata.decode().split()
        if command[0]=='login':
            result,author=login(command,status,author)
            status=result[1]
            if result[2]>0:
                id=result[2]
                conn.sendall((str(result[0])+"."+"&"+str(result[2])).encode())
            else:
                conn.sendall(str(result[0]).encode())
        elif command[0]=='logout':
            result,status,author=logout(status,id,author)
            result+="."
            conn.sendall(result.encode())
        elif command[0]=='list-user':
            result=list_user()
            conn.sendall(result.encode())
        elif command[0]=='create-board':
            result,status,author=create_board(command,status,id,author)
            conn.sendall(result.encode())
        elif command[0]=='list-board':
            result=list_board(command)
            conn.sendall(result.encode())
        elif command[0]=='create-post':
            result,author=create_post(command,author)
            conn.sendall(result.encode())
        elif command[0]=='list-post':
            result=list_post(command)
            conn.sendall(result.encode())
        elif command[0]=='read':
            result=read_post_i(command)
            conn.sendall(result.encode())
        elif command[0]=='delete-post':
            result=delete_post(command,author)
            conn.sendall(result.encode())
        elif command[0]=='update-post':
            result=update_post(command,author)
            conn.sendall(result.encode())
        elif command[0]=='comment':
            result=comment(command,author)
            conn.sendall(result.encode())

        elif command[0]=='exit':
            break
                      
    if command[0]=="exit":
            conn.close()
           
       # conn.sendall(result.encode())

#main
#delete_database()    
create_database()


mutex = threading.Lock()
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






         





            
           
            
        

        
