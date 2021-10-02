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
        self.connected = True
        self.user = user
        self.addr = addr
        self.BUFSIZ = 3000
        self.username = None
        self.loggedIn = False
        self.loginThread = threading.Thread(target=self.login, args=(self.user,self.addr,))
        self.loginThread.start()
        
        self.x = 0
        self.y = 0 

        #self.sendThread = threading.Thread(target=self.send)

    def disconnect(self):
            self.connected = False
            print(self.addr, "client disconnected")
            self.user.close()
            clients.remove(self)
            self.loggedIn =  False
            self.username = None

    def isconnected(self):
        return self.connected

    def send(self,data):
        serialized_data = json.dumps(data) #serialize data
        self.user.sendall(bytes(serialized_data, "utf8")) ### SENDS LOGIN DATA TO SERVER [loginRequest,username]

    def recive(self):
        try:
            response = json.loads(self.user.recv(self.BUFSIZ).decode("utf8")) ### WAITS FOR DATA TO BE RETURNED
            if not response:
                print("disconnected")
            else:
                return response
        except:
            print("error")
            
        
            

    def login(self,client,client_address): #pulled from previous messaging project
        #Then wait for login
        while True:
            loginData = self.recive()
            if loginData["requestType"] == "disconnected":
                break

            if loginData["requestType"] == "loginRequest":
                username = loginData["username"]
            
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
            
                loginReq = {"requestType":"loginRequest","loginR":True}
                self.send(loginReq)
                print("confirmed login:",username,"at","%s:%s" % client_address)
                self.username = username
                self.loggedIn = True

                self.reciveThread = threading.Thread(target=self.recivePos)
                self.reciveThread.start()

                break

                #pass


    # def send(self,data):
    #     #takes in dict as data, jason encodes, and sends
    #     self.user.send(str.encode(data))
    #     self.reply = ""


    def recivePos(self):
        while True:
            data = self.recive()
            print(data)

            if data["requestType"] == "posData":
                self.x = data["x"]
                self.y = data["y"]
            
 
                

            
    
    def getPos(self):
        return {"x":self.x,"y":self.y}

    def getUsername(self):
        return self.username






class Battle:
    def __init__(self,client1,client2):
        print("2 players connected. initializing battle.")
        
        self.client1 = client1
        self.client2 = client2
        battleThread = threading.Thread(target=self.initBattle)
        battleThread.start()


    def initBattle(self):
        while True:
            c1req = self.sendReq(self.client1,self.client2)
            c2req = self.sendReq(self.client2,self.client1)
            if c1req == "disconnected" or c2req == "disconnected":
                break
            if  c1req == True and c2req == True:
                t1 = threading.Thread(target=self.sendPos,args=(self.client1,self.client2))
                t2 = threading.Thread(target=self.sendPos,args=(self.client2,self.client1))
                t1.start()
                t2.start()
                break

        
    
    def sendReq(self,player1,player2):
        battleReq = {"requestType":"battleReq","enemyU":player2.getUsername()}
        player1.send(battleReq)
        response = player1.recive()

        if response["requestType"] == "disconnected":
            return 'disconneted'

        if response["requestType"]=="battleReq" and response["battleAccepted"]==True: 
            print(player1.getUsername(), "has accepted the battle")
            return True
            
        else:
            return False      


    def sendPos(self,sender,reciver):
        while sender.isconnected() == True and reciver.isconnected() == True:
            data = (sender.getPos().update({"requestType":"posData"}))
            reciver.send(data)


        
    





flag = False    
while True:
    user, addr = s.accept()
    print("Incoming connection from:",addr)
    client = Client(user,addr) #client should not be a thread
    clients.append(client)
    
    if len(clients) == 2 and flag == False:
        threadBattle = threading.Thread(target=Battle, args=(clients[0],clients[1],))
        threadBattle.start() 
        flag = True

    