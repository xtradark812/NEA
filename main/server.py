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
battles = []

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
        self.ecounter = 0

        self.pendingBattle = False
        self.enemyUsername = None
        self.battleSent = False
        self.battleAccepted = False
        self.pendingClient = None
        self.requestedEnemy = None

        self.inBattle = False

        self.x = 0
        self.y = 0 
        self.click = None

        mainThread = threading.Thread(target=self.main)
        mainThread.start()


    def clientLog(self,events,e=None):
        if e != None:
            print(self.addr," ERROR |", events, e )
        else:
            print(self.addr," log:", events)
            #TODO save to file

    def send(self,data):
        print("send:",data)
        try:
            serialized_data = json.dumps(data) #serialize data
            self.user.sendall(bytes(serialized_data, "utf8")) ### SENDS LOGIN DATA TO SERVER [loginRequest,username]
        except Exception as e:
            self.clientLog("send error",e)

    def recive(self):
        
        decoder = JSONDecoder()
        try:
            data = self.user.recv(self.BUFSIZ).decode("utf8")
            if not data:
                self.disconnect()
            else:

                # #this part of the function will fix broken pakets.
                # #when the client tries to send hundreds of json objects a seccond, sometimes the objects get stuck together
                # #to solve this problem, this algorithim find exactly the data that is needed from each sent item, and strips off everything else
                # #if it does not work (e.g. the server recives incomplete data like "123}"), it will call itself and try again
                # i = 0
                # string = False
                # isdict = False
                # newData = ""
                # finalData = ""
                # for char in data:
                #     if char == "{" and string == False:
                #         newData = data[i:]
                #         isdict = True
                #     if char == "}" and isdict == True and string == False:
                #         finalData = newData[:i+1]
                #         string = True
                #     i+=1
                # if string == False:
                #     tryAgain = self.recive()
                #     return tryAgain
                
                response, index = decoder.raw_decode(data) ### WAITS FOR DATA TO BE RETURNED
                print("recive",response)
                return response
            
        except socket.timeout:
            self.clientLog("socket timeout")
            return {"requestType":"error","error":"socketTimeout"}
        except Exception as e:
            self.clientLog("recive error",e)
            return {"requestType":"error","error":e}
            
    def requestHandler(self):
        # self.user.settimeout(1) 
        
        data = self.recive() 
        if data == None or data["requestType"] == "error":
            self.ecounter +=1
        else:
            self.ecounter = 0 
        
        if self.ecounter > 30:
            self.clientLog("maximum recive errors, shutting down connection")
            return False
        elif self.battleAccepted == True: 
            if data["requestType"] == "posData":
                self.x = data["x"]
                self.y = data["y"]
                if "clickPos" in data:
                    self.click = data["clickPos"]
        elif self.battleSent == True and self.battleAccepted == False:
            if data["requestType"]=="battleReq" and data["battleAccepted"]==True: 
                self.clientLog(self.username+" has accepted the battle, sending confirm")
                self.battleAccepted = True
        elif data["requestType"] == "startBattle":
            self.clientLog("Battle reqest recieved")
            opponentU = data["enemyU"]
            for client in clients: #Searches list of connected clients
                if client.getUsername() == opponentU and client.isconnected() == True and client.isLoggedIn() == True:
                    self.clientLog("attempting to start battle")
                    client.sendBattleRequest(self.username)
                    self.pendingClient = client
        elif data["requestType"] == "getOnlineUsers":
            clientList = []
            for client in clients:
                if client.isconnected() == True and client.isLoggedIn() == True:
                    clientList.append(client.getUsername())
            self.send({"requestType":"getOnlineUsers","onlineUsers":clientList})
        
        if self.pendingClient != None:
            accept = self.pendingClient.checkIfAccepted()
            if accept:
                    self.send({"requestType":"battleConfirm","battleAccepted":True,"enemyU":self.pendingClient.getUsername()})
                    self.pendingClient.send({"requestType":"battleConfirm","battleAccepted":True,"enemyU":self.username})
                    self.battleAccepted = True
                    self.clientLog("creating battle")
                    startBattle(self.pendingClient,self) #starts battle


        return True
                
    def checkIfAccepted(self):
        return self.battleAccepted

    def sendBattleRequest(self,enemyU):
        self.requestedEnemy = enemyU
        battleReq = {"requestType":"battleReq","enemyU":enemyU}
        self.send(battleReq)
        self.clientLog("sent battle request to "+self.username)
        self.battleSent = True

    def main(self):
        print("client initialised. beginning main loop",self.addr)
        if self.loggedIn != True: 
            self.login()
        while self.loggedIn and self.connected:
            self.connected = self.requestHandler()
        
        self.disconnect()


    def disconnect(self):
            self.connected = False
            self.clientLog([self.addr,"client disconnected"])
            self.user.close()
            clients.remove(self)
            self.loggedIn =  False
            self.username = None
            self.enemyUsername = None

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



    def sendPos(self,data):
        self.send(data)      
 
    def getPos(self):
        if self.click != None:
            data = {"requestType":"posData","x":self.x,"y":self.y,"clickPos":self.click}
            self.click = None
            return data
        else:
            return {"requestType":"posData","x":self.x,"y":self.y}

    def getUsername(self):
        return self.username



def startBattle(client1,client2):
    battle = Battle(client1,client2)
    battleThread = threading.Thread(target=battle.sendPos())
    battleThread.start()

    battles.append(battle)
    battle = None


class Battle:
    def __init__(self,client1,client2):
        print("2 players connected. initializing battle.")
        #TODO server decides whos on which side
        self.client1 = client1
        self.client2 = client2

        self.width = 120
        self.height = 240

        





    def sendPos(self):
        while self.client1.isconnected() == True and self.client2.isconnected() == True:
            data1 = self.client1.getPos()
            data2 = self.client2.getPos()
            
            if "clickPos" in data1:
                data2["reduceHp"] = self.checkClick(data1,data2)
            elif "clickPos" in data2:
                data1["reduceHp"] = self.checkClick(data2,data1)
                

            self.client2.sendPos(data1)
            self.client1.sendPos(data2)

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

        
    


#TODO OLD
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




    