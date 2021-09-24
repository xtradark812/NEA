import socket
import json

class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server,self.port)
        self.BUFSIZ = 2048
        self.client.connect(self.addr)
        self.username = self.connectionInit("test")

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

