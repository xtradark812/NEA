from json.decoder import JSONDecoder

import socket
import json

class Network(): #TODO reciving should be done outside of the network
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server,self.port)
        self.BUFSIZ = 1024
        self.connected = False
        self.enemyUsername = None
        self.enemyPos = None
        self.onlineUsers = []

        self.reduceHp = None


    def send(self,data):
        # print("send:",data)
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
                # print("response:",response)
                return response

        except Exception as e:
            print("error",e)
        

    def connect(self,username):
        try:
            self.client.connect(self.addr)
            self.connected = True

        except Exception as e:
            print("Error connecting to server:",e)
            return False

        
        self.username = self.login(username)
        if self.username == None:
            return False
        elif self.username != None:
            print("connected")
            return True

    def main(self):
        if self.connected == True:
            self.enemyUsername = None
            self.enemyPos = None
        while self.connected:
            response = self.recive()
            if response["requestType"]=="battleReq":
                self.waitForBattle(response)
            if response["requestType"] == "getOnlineUsers":
                self.onlineUsers = response["onlineUsers"]
    
    def startBattle(self):
        self.send({"requestType":"getOnlineUsers"})
        while bool(self.onlineUsers) == False:
            pass
        #TEMPORARILY JUST PICKS ANY PERSON
        for enemyU in self.onlineUsers:
            if enemyU != self.username:
                print("sending battle request")
                self.send({"requestType":"startBattle","enemyU":enemyU})
                    
            
    def login(self,username): #function pulled from previous messaging project

        loginReq = {"requestType":"loginRequest","username":username}

        self.send(loginReq)
        response = self.recive()

        if response["requestType"]=="loginRequest" and response["loginR"]==True: 
            print("logged in as", username)
            return username
        
        else:
            return None

    def enemyConnected(self):
        return self.enemyUsername

    
    def waitForBattle(self,response):
            accept = {"requestType":"battleReq","battleAccepted":True}    
            self.send(accept)
            confirm = self.recive()
            if confirm == accept:
                print("starting a battle with", response["enemyU"])
                self.enemyUsername = response["enemyU"]
                while True:
                    data = self.recive()
                    if data != None:
                        if data["requestType"] == "posData":

                            if "reduceHp" in data: #added here just in case it gets lost
                                self.reduceHp = data["reduceHp"] #TODO if takes multiple damage needs to add it up
                                

                            self.enemyPos = data #TODO seperate pos data from other data and fix variable names
                        if data["requestType"] == "opponentDisconnect":
                            self.enemyUsername = None
                            break
                    elif data == None:
                        print("no data")


            

    def getEnemyPos(self):
        if self.reduceHp != None:
            self.enemyPos["reduceHp"] = self.reduceHp
            self.reduceHp = None
        
        return self.enemyPos
            

        #this waits for an enemy to connect, and once it connects it will constantly receive pos
    
    def isConnected(self):
        return self.connected
    