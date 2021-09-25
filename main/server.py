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
        self.username = None
        self.loggedIn = False
        self.loginThread = threading.Thread(target=self.login, args=(self.user,self.addr,))
        self.loginThread.start()
        
        self.x = 0
        self.y = 0 
        self.reciveThread = threading.Thread(target=self.recivePos)
        self.reciveThread.start()
        #self.sendThread = threading.Thread(target=self.send)

    def login(self,client,client_address): #pulled from previous messaging project
        #Then wait for login
        while True:
            loginData = client.recv(self.BUFSIZ).decode("utf8")
            data = json.loads(loginData)

            if data["requestType"] != "loginRequest":
                print("%s:%s invalid login request." % client_address)

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
                self.username = username
                self.loggedIn = True
                break

                #pass


    # def send(self,data):
    #     #takes in dict as data, jason encodes, and sends
    #     self.user.send(str.encode(data))
    #     self.reply = ""


    def recivePos(self):

        #takes in jason data and decodes, then uses data to update player attributes stored within this class.
        self.data = {}
        while True:
            while self.loggedIn == True:
                try:
                    self.recv = self.user.recv(self.BUFSIZ).decode("utf8")
                    self.data = json.loads(self.recv)
                    self.x = self.data["x"]
                    self.y = self.data["y"]
                except Exception as e:
                    print("error:",e)
            
                if not self.recv:
                    print("Disconnected")
                    print(self.addr, "has lost connection")
                    self.user.close()
                    break
                

            
    
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
            if self.sendReq(self.client1,self.client2) == True and self.sendReq(self.client2,self.client1) == True:
                t1 = threading.Thread(target=self.sendpos,args=(self.client1,self.client2))
                t2 = threading.Thread(target=self.sendpos,args=(self.client2,self.client1))
                t1.start()
                t2.start()
                break

        
    
    def sendReq(self,player1,player2):
        self.battleReq = {"requestType":"battleReq","enemyU":player2.getUsername()}
        self.serialized = json.dumps(self.battleReq) #serialize data
        try:
            player1.user.sendall(bytes(self.serialized, "utf8")) ### SENDS LOGIN DATA TO SERVER [battleRequest,enemyu]
        except Exception as e:
            print("error",e)

        try:
            response = json.loads(self.player1.user.recv(self.BUFSIZ).decode("utf8")) ### WAITS FOR DATA TO BE RETURNED

            if response["requestType"]=="battleReq" and response["battleAccepted"]==True: 
                print(player1.getUsername(), "has accepted the battle")
                return True
            else:
                return False      
        except:
            print("Invalid response from server")
            return False

    def sendPos(self,sender,reciver):
        while True:
            try:
                self.serialized = json.dumps(sender.getPos().update({"requestType":"enemyLoc"})) #serialize data
                reciver.sendall(bytes(self.serialized, "utf8")) ### SENDS DATA
            except socket.error as e:
                print ("Send error:", e)


        
    





    
while True:
    user, addr = s.accept()
    print("Incoming connection from:",addr)
    client = Client(user,addr) #client should not be a thread
    clients.append(client)
    if len(clients) == 2:
        threadBattle = threading.Thread(target=Battle, args=(clients[0],clients[1],))
        threadBattle.start() 

    