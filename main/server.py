import socket
import threading
import sys

server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    s.bind((server,port))
    s.listen(2)
    print("Waiting for a connection")
except socket.error as e:
    str(e)
    print(e)



def client(user,addr):
    user.send(str.encode("connected"))
    reply = ""
    while True:
        try:
            data = user.recv(2048)
            reply = data.decode("utf-8")

            if not data:
                print("Disconnected")
                break
            else:
                print("Received:",reply)
                print("Sending:",reply)

            user.sendall(str.encode(reply))
        except:
            break

    print("has lost connection")
    user.close()



    
while True:
    user, addr = s.accept()
    print("Incoming connection from:",addr)
    thread = threading.Thread(target=client, args=(user,addr,))
    thread.start()