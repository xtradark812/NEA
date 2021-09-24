import socket
import threading
import sys
import json
server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = []

try:
    s.bind((server,port))
    s.listen(2)
    print("Waiting for a connection")
except socket.error as e:
    str(e)
    print(e)



class Client:
    def __init__(self,user,addr):
        self.user = user
        self.addr = addr
        self.BUFSIZ = 2048
        self.login(user,addr)
        clients.append(self)
        print(clients)
        self.x = 0
        self.y = 0 
        self.reciveThread = threading.Thread(target=self.recivePos)
        self.reciveThread.start()
        #self.sendThread = threading.Thread(target=self.send)

    def login(self,client,client_address): #pulled from previous messaging project
        #Then wait for login
        loginData = client.recv(self.BUFSIZ).decode("utf8")
        data = json.loads(loginData)

        if data["requestType"] != "loginRequest":
            print("%s:%s invalid login request." % client_address)
            return False

        else:
            username = data["username"]
            #password = data["password"]
            #if username in clients.keys():
            #    loginReq = json.dumps({"requestType":"loginRequest","loginR":False,"reason":"Already logged in"})
            #    client.send(bytes(loginReq, "utf8")) #add excpetion whch logs out old user
            #    return False
            #else:
                #database lookup here!
                #if username and pass dont mach
                    #loginReq = json.dumps({"requestType":"loginRequest","loginR":False,"reason":"Invalid username/password"})
                    #client.send(bytes(loginReq, "utf8"))
                    #return False
                #elseif username and pass mach
            
            loginReq = json.dumps({"requestType":"loginRequest","loginR":True})
            client.send(bytes(loginReq, "utf8"))
            print("confirmed login:",username,"at","%s:%s" % client_address)
            return username
                #pass


    # def send(self,data):
    #     #takes in dict as data, jason encodes, and sends
    #     self.user.send(str.encode(data))
    #     self.reply = ""


    def recivePos(self):
        #takes in jason data and decodes, then uses data to update player attributes stored within this class.
        while True:
            self.recv = self.user.recv(self.BUFSIZ).decode("utf8")
            self.data = json.loads(self.recv)
            if not self.recv:
                print("Disconnected")
                print(self.addr, "has lost connection")
                self.user.close()
                break
            self.x = self.data["x"]
            self.y = self.data["y"]

    def getPos(self):
        return {"x":self.x,"y":self.y}





class Battle:
    def __init__(self):
        pass
    


#another class which takes 2 clients and battles them



    
while True:
    user, addr = s.accept()
    print("Incoming connection from:",addr)
    thread = threading.Thread(target=Client, args=(user,addr,))
    thread.start()
    if len(clients) == 2:
        threadBattle = threading.Thread(target=Battle, args=(clients[0],clients[1],))
        threadBattle.start() 
    