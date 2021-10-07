#HAVE CLIENT ALWAYS RECIVE THINGS, AND ITS ABLE TO CHECK WHATS BEING RECIVED WITH START THRED
#REDUCE THE AMMOUNT OF THREADS


from json.decoder import JSONDecoder
import socket
import threading
import sys
import json
import pickle
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
        print("initializing connection with",addr)
        self.connected = True
        self.user = user
        self.addr = addr
        self.BUFSIZ = 1024
        self.username = None
        self.loggedIn = False

        self.pendingBattle = False
        self.enemyUsername = None
        self.battleAccepted = False

        self.x = 0
        self.y = 0 

        #self.sendThread = threading.Thread(target=self.send)

    def send(self,data):
        print(data)
        serialized_data = json.dumps(data) #serialize data
        self.user.sendall(bytes(serialized_data, "utf8")) ### SENDS LOGIN DATA TO SERVER [loginRequest,username]

    def recive(self):
        
        decoder = JSONDecoder()
        try:
            data = self.user.recv(self.BUFSIZ).decode("utf8")
            if not data:
                print("disconnected")
            else:
                i = 0
                string = False
                isdict = False
                newData = ""
                finalData = ""
                for char in data:
                    if char == "{" and string == False:
                        newData = data[i:]
                        isdict = True
                    if char == "}" and isdict == True and string == False:
                        finalData = newData[:i+1]
                        string = True
                    i+=1
                if string == False:
                    tryAgain = self.recive()
                    return tryAgain
                
                response, index = decoder.raw_decode(finalData) ### WAITS FOR DATA TO BE RETURNED
                print(response)
                return response
            

        except Exception as e:
            print("error",e)
            
        
            
    def main(self):
        battleSent =  False
        print("client initialised. beginning main loop",self.addr)
        while self.loggedIn != True:
            self.login()
        while self.loggedIn == True:
            if self.pendingBattle == True and self.battleAccepted == False and battleSent == False:
                print("preparing to send battle request")
                battleReq = {"requestType":"battleReq","enemyU":self.enemyUsername}
                self.send(battleReq)
                print("sent battle request to",self.username)
                battleSent = True
            if battleSent == True and self.battleAccepted == False and self.pendingBattle == True:
                response = self.recive()
                if response["requestType"]=="battleReq" and response["battleAccepted"]==True: 
                    print(self.getUsername(), "has accepted the battle")
                    self.send({"requestType":"battleReq","battleAccepted":True})
                    self.battleAccepted = True
                    print("reciving pos data")
            if self.battleAccepted == True:
                data = self.recive()
                if data["requestType"] == "posData":
                    self.x = data["x"]
                    self.y = data["y"]
            


    def startBattle(self,enemyU):
        self.enemyUsername = enemyU
        self.pendingBattle = True

    def checkBattleAccepted(self):
        return self.battleAccepted

    def disconnect(self):
            self.connected = False
            print(self.addr, "client disconnected")
            self.user.close()
            clients.remove(self)
            self.loggedIn =  False
            self.username = None

    def isconnected(self):
        return self.connected
    
    def isLoggedIn(self):
        return self.loggedIn

    

    def login(self): #pulled from previous messaging project
        #Then wait for login
        loginData = self.recive()

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
            print("confirmed login:",username,"at","%s:%s" % self.addr)
            self.username = username
            self.loggedIn = True
            return True

                #pass


    # def send(self,data):
    #     #takes in dict as data, jason encodes, and sends
    #     self.user.send(str.encode(data))
    #     self.reply = ""

            
 
    def getPos(self):
        return {"x":self.x,"y":self.y}

    def getUsername(self):
        return self.username






class Battle:
    def __init__(self,client1,client2):
        print("2 players connected. initializing battle.")
        
        self.client1 = client1
        self.client2 = client2



    def initBattle(self):
        while True:
            self.client1.startBattle(self.client2.getUsername())
            self.client2.startBattle(self.client1.getUsername())

            if  self.client1.checkBattleAccepted() == True and self.client2.checkBattleAccepted() == True:
                self.sendPos(self.client1,self.client2)
                break


    def sendPos(self,p1,p2):
        while p1.isconnected() == True and p2.isconnected() == True:
            data1 = (p1.getPos().update({"requestType":"posData"}))
            p2.send(data1)
            data2 = (p2.getPos().update({"requestType":"posData"}))
            p1.send(data2)


        
    



def battleWait():
    flag = False
    while flag == False:
        if len(clients) == 2 and clients[0].isLoggedIn() == True and clients[1].isLoggedIn() == True:
            battle = Battle(clients[0],clients[1])
            battle.initBattle()
            flag = True


battlestart = threading.Thread(target=battleWait)
battlestart.start()
while True:
    user, addr = s.accept()
    print("Incoming connection from:",addr)
    client = Client(user,addr) #client should not be a thread
    clients.append(client)
    thread = threading.Thread(target=client.main)
    thread.start()



    