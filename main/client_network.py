from json.decoder import JSONDecoder

import socket
import json

def log(event,e=None):
    if e != None:
        print("ERROR |", event, e )
    else:
        print("log:", event)
    #TODO save to file

class Network(): #TODO reciving should be done outside of the network
    def __init__(self):
        log("Initializing network")
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server,self.port)
        self.BUFSIZ = 1024
        self.connected = False
        self.enemyUsername = None
        self.enemyData = None
        self.onlineUsers = []
        self.requestedEnemy = None
        self.username = None #If username is none, user is not logged in
        self.reduceHp = None


    def send(self,data):
        print("send:",data)
        serialized_data = json.dumps(data) #serialize data
        self.client.sendall(bytes(serialized_data, "utf8")) ### SENDS DATA TO SERVER 


    def recive(self):
        decoder = JSONDecoder()
        try:
            data = self.client.recv(self.BUFSIZ).decode("utf8")
            if not data:
                self.connected = False
                print("disconnected")
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
                print("recive:",response)
                return response

        except socket.timeout:
            return {"requestType":None}

        except Exception as e:
            print("error",e)
            return {"requestType":None}
        
        

    def connect(self,username): #Connects to the server and attempts to login. Returns true if logged in.
        log("Attempting to connect to server")
        try:
            self.client.connect(self.addr)
            self.client.settimeout(.5)
            self.connected = True
            log("Sucsessfully connected to server")
        except Exception as e:
            log("Failed to connect to server",e)
            return False

        log("Attempting login")
        self.username = self.login(username)

        if self.username == None:
            log("Login failed")
            return False
        elif self.username != None:
            log("Login sucsessful, gathering online users")
            self.getOnlineUsers()
            return True

    def getOnlineUsers(self):
        self.send({"requestType":"getOnlineUsers"})

    def reciveRequest(self):
        response = self.recive()

        if response["requestType"]=="battleReq":
            log("Battle request recived, accepting...")
            self.acceptBattle(response["enemyU"]) #TODO this atomatically accepts battle request, should be in game loop
            return None

        if response["requestType"] == "battleConfirm" and response["battleAccepted"] == True:
            log("Starting battle")
            self.enemyUsername = response["enemyU"]
            return self.enemyUsername

        if response["requestType"] == "getOnlineUsers":
            self.onlineUsers = response["onlineUsers"]
            return None

        return None
    
    def sendBattleReq(self,enemyU): #gets a list of online users then sends battle request with provided username if user is online
        sent = False
        self.requestedEnemy = enemyU
        log("Enemy request ready")
        for username in self.onlineUsers: #Checks if user is online
            if self.requestedEnemy.lower() == username.lower():
                log("Sending battle request")
                self.send({"requestType":"startBattle","enemyU":self.requestedEnemy})
                sent = True
        if sent == False:
            log("Requested user not online")
            self.requestedEnemy = None


                    
            
    def login(self,username): #function pulled from previous messaging project

        loginReq = {"requestType":"loginRequest","username":username}

        self.send(loginReq)
        response = self.recive()

        if response["requestType"]=="loginRequest" and response["loginR"]==True: 
            log("Server accepted login response")
            return username
        
        else:
            return None

    def enemyConnected(self):
        if self.enemyUsername != None:
            return True
        else:
            return False

    
    def acceptBattle(self,enemyU):
        log("Accepting battle")
        self.requestedEnemy = enemyU
        accept = {"requestType":"battleReq","battleAccepted":True,"enemyU":enemyU} 
        self.send(accept)



    def reciveData(self):
        data = self.recive()
        if data != None:
            if data["requestType"] == "posData":
                if "reduceHp" in data:  #game loop might fetch pos data and miss this data, so it is stored in network as variables 
                    if self.reduceHp != None:
                        self.reduceHp += data["reduceHp"]
                    else:
                        self.reduceHp = data["reduceHp"]

                    self.enemyData = data

            if data["requestType"] == "opponentDisconnect":
                self.enemyUsername = None
            
            


        else:
            print("error")
                        
            

    def getEnemyData(self):
        if self.reduceHp != None:
            self.enemyData["reduceHp"] = self.reduceHp
            self.reduceHp = None
        return self.enemyData
            

    
    def isConnected(self):
        return self.connected
    