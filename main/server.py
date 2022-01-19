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

def log(event,e=None):
    if e != None:
        print("ERROR |", event, e )
    else:
        print("log:", event)
    #TODO save to file

try:
    s.bind((server,port))
    s.listen(2)
    log("Waiting for a connection")
except socket.error as e:
    str(e)
    log("error connecting",e)



class Client:
    def __init__(self,user,addr):
        self.user = user
        self.addr = addr
        self.clientLog("initializing user "+"%s:%s" % addr)


        self.connected = False
        self.BUFSIZ = 1024
        self.username = None
        self.loggedIn = False

        self.pendingBattle = False
        self.enemyUsername = None
        self.battleAccepted = False

        self.x = 0
        self.y = 0 
        self.click = None
        mainThread = threading.Thread(target=self.main)
        mainThread.start()

        #self.sendThread = threading.Thread(target=self.send)

    def clientLog(self,event,e=None):
        if e != None:
            print(self.addr," ERROR |", event, e )
        else:
            print(self.addr," log:", event)
            #TODO save to file

    def send(self,data):
        # print("send:",data)
        serialized_data = json.dumps(data) #serialize data
        self.user.sendall(bytes(serialized_data, "utf8")) ### SENDS LOGIN DATA TO SERVER [loginRequest,username]

    def recive(self):
        
        decoder = JSONDecoder()
        try:
            data = self.user.recv(self.BUFSIZ).decode("utf8")
            if not data:
                self.disconnect()
            else:

                #this part of the function will fix broken pakets.
                #when the client tries to send hundreds of json objects a seccond, sometimes the objects get stuck together
                #to solve this problem, this algorithim find exactly the data that is needed from each sent item, and strips off everything else
                #if it does not work (e.g. the server recives incomplete data like "123}"), it will call itself and try again
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
                # print("response",response)
                return response
            
        except socket.timeout:
            self.clientLog("socket timeout")
            return {"requestType":"timeout"}
        except Exception as e:
            self.clientLog("recive error",e)
            return {"requestType":e}
            
    def requestHandler(self):
        self.user.settimeout(1) 
        data = self.recive() 

        if data["requestType"] == "startBattle":
            opponentU = data["enemyU"]
            for client in clients: #Searches list of connected clients
                if client.getUsername() == opponentU and client.isconnected() == True and client.isLoggedIn() == True:
                    self.clientLog("starting battle")
                    battle = Battle(client,self) #starts battle (TODO should be a battle request )

        elif data["requestType"] == "getOnlineUsers":
            clientList = []
            for client in clients:
                if client.isconnected() == True and client.isLoggedIn() == True:
                    clientList.append(client.getUsername())
            self.send({"requestType":"getOnlineUsers","onlineUsers":clientList})
        
        battleSent = False

        if self.pendingBattle == True and self.battleAccepted == False and battleSent == False:
            print("preparing to send battle request")
            battleReq = {"requestType":"battleReq","enemyU":self.enemyUsername}
            self.send(battleReq)
            self.clientLog("sent battle request to "+self.username)
            battleSent = True

        if battleSent == True and self.battleAccepted == False and self.pendingBattle == True:
            response = self.recive()
            if response["requestType"]=="battleReq" and response["battleAccepted"]==True: 
                self.clientLog(self.getUsername()+" has accepted the battle")
                self.send({"requestType":"battleReq","battleAccepted":True})
                self.battleAccepted = True
                self.clientLog("reciving pos data")

        if self.battleAccepted == True:
            data = self.recive()
            if data["requestType"] == "posData":
                self.x = data["x"]
                self.y = data["y"]
                if "clickPos" in data:
                    self.click = data["clickPos"]


    def main(self):
        print("client initialised. beginning main loop",self.addr)
        if self.loggedIn != True: #TODO while loop?
            self.login()
        if self.loggedIn == True:
            self.requestHandler()



    def startBattle(self,enemyU):
        self.enemyUsername = enemyU
        self.pendingBattle = True

    def checkBattleAccepted(self):
        return self.battleAccepted

    def disconnect(self):
            self.connected = False
            self.clientLog(self.addr+" client disconnected")
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
            
            #TODO CHECK PASSWORD WITH DATABASE
            
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
            self.clientLog("confirmed login: "+username+" at"+"%s:%s" % self.addr)
            self.username = username
            self.loggedIn = True
            self.connected = True
            return True

                #pass


    # def send(self,data):
    #     #takes in dict as data, jason encodes, and sends
    #     self.user.send(str.encode(data))
    #     self.reply = ""

            
 
    def getPos(self):
        if self.click != None:
            data = {"requestType":"posData","x":self.x,"y":self.y,"clickPos":self.click}
            self.click = None
            return data
        else:
            return {"requestType":"posData","x":self.x,"y":self.y}

    def getUsername(self):
        return self.username






class Battle:
    def __init__(self,client1,client2):
        print("2 players connected. initializing battle.")
        
        self.client1 = client1
        self.client2 = client2

        self.width = 120
        self.height = 240

        battlethread = threading.Thread(target=self.initBattle)
        battlethread.start()



    def initBattle(self):
        while True:
            self.client1.startBattle(self.client2.getUsername())
            self.client2.startBattle(self.client1.getUsername())

            if  self.client1.checkBattleAccepted() == True and self.client2.checkBattleAccepted() == True:
                self.sendPos(self.client1,self.client2)
                break


    def sendPos(self,p1,p2):
        while p1.isconnected() == True and p2.isconnected() == True:
            data1 = p1.getPos()
            data2 = p2.getPos()
            
            if "clickPos" in data1:
                data2["reduceHp"] = self.checkClick(data1,data2)
            elif "clickPos" in data2:
                data1["reduceHp"] = self.checkClick(data2,data1)
                

            p2.send(data1)
            p1.send(data2)

    def checkClick(self,data1,data2):
        pos = data1["clickPos"]
        print(pos)
        x1 = pos[0]
        y1 = pos[1]
        x = data2["x"]
        y = data2["y"]
        if  x-(self.width/2) <= x1 <= x + (self.width/2) and y-(self.height/2) <= y1 <= y + (self.height/2):
            print("hit!")
            return 10
        else:
            return 0

        
    



# def battleWait():
#     flag = False
#     while flag == False:
#         if len(clients) == 2 and clients[0].isLoggedIn() == True and clients[1].isLoggedIn() == True:
#             battle = Battle(clients[0],clients[1])
#             battle.initBattle()
#             flag = True


# battlestart = threading.Thread(target=battleWait)
# battlestart.start()
while True:
    user, addr = s.accept()
    print("Incoming connection from:",addr)
    client = Client(user,addr) #client should not be a thread
    clients.append(client)




    