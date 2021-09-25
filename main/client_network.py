import socket
import json
import threading

class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server,self.port)
        self.BUFSIZ = 2048
        self.client.connect(self.addr)
        self.username = self.connectionInit("test")
        self.enemyUsername = None
        self.enemyPos = None
        self.waitForEnemyThread = threading.Thread(target=self.waitForBattle)
        self.waitForEnemyThread.start()


    #def getPos(self):
     #   return self.pos
    
    def connectionInit(self,username): #function pulled from previous messaging project

        self.loginReq = {"requestType":"loginRequest","username":username}
        self.serialized = json.dumps(self.loginReq) #serialize data
        self.client.sendall(bytes(self.serialized, "utf8")) ### SENDS LOGIN DATA TO SERVER [loginRequest,username]
        try:
            response = json.loads(self.client.recv(self.BUFSIZ).decode("utf8")) ### WAITS FOR DATA TO BE RETURNED

            if response["requestType"]=="loginRequest" and response["loginR"]==True: 
                print("logged in as", username)
                return username
            else:
                return False      
        except:
            print("Invalid response from server")
            return False



    def sendPos(self,pos):
        try:
            self.serialized = json.dumps(pos) #serialize data
            self.client.sendall(bytes(self.serialized, "utf8")) ### SENDS DATA
        except socket.error as e:
            print ("Send error:", e)
    
    def waitForBattle(self):
        while True:
            try:
                response = json.loads(self.client.recv(self.BUFSIZ).decode("utf8")) ### WAITS FOR DATA TO BE RETURNED
                if response["requestType"]=="battleReq": 
                    print("starting a battle with", response["enemyU"])
                    self.accept = {"requestType":"battleReq","battleAccepted":True}
                    self.serialized = json.dumps(self.accept) #serialize data
                    self.client.sendall(bytes(self.serialized, "utf8")) 
                    self.enemyUsername = response["enemyU"]
                    getEnemyPosThread = threading.Thread(target=self.recivePosData)
                    break
            except:
                print("Invalid response from server")

    def checkEnemyConnected(self):
        if self.enemyUsername != None:
            return self.enemyUsername
        else:
            return False

    def recivePosData(self):
        self.data = {}
        while True:
            try: 
                self.recv = self.client.recv(self.BUFSIZ).decode("utf8")
                self.data = json.loads(self.recv)
                if self.data["requestType"] == "enemyLoc":
                    self.enemyPos = self.data

                #check if data being recived is pos data?
            except Exception as e:
                print("error:",e)
            
            # if not self.recv:
            #     print("Disconnected")
            #     print(self.addr, "has lost connection")
            #     self.client.close()
            #     break
    def getEnemyPos(self):
        return self.enemyPos
            

        #this waits for an enemy to connect, and once it connects it will constantly receive pos
    

