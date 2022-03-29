
from json.decoder import JSONDecoder
import socket
import threading
import json
import sqlite3

from ui import OnlineList



#Set up TCP connection
server = "127.0.0.1"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


clients = []
battles = []


def log(event,e=None): #Log function for debugging
    if e != None:
        print("ERROR |", event, e )
    else:
        print("log:", event)
    #Possibly save to file?


#Start server
try:
    s.bind((server,port))
    s.listen(2)
    log("Waiting for a connection")
except socket.error as e:
    str(e)
    log("error connecting",e)


class Database():
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cursor = self.con.cursor()

        self.initDatabase()
    
    def initDatabase(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
               (user_name text NOT NULL, password text, acsess text)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS acsessTextures
               (acsess text NOT NULL, serializedData text)''')

        #self.createAcsess("test",json.dumps({"standing":"","enemyStanding":"","background":"background01","crouching":"","enemyCrouching":"","walking":"","enemyWalking":"","jumping":"","enemyJumping":""}))

    def createUser(self,username,password,acsess):
        self.cursor.execute("INSERT INTO users VALUES (?,?,?)",[username,password,acsess])
        self.con.commit()
    
    def createAcsess(self,name,data):
        self.cursor.execute("INSERT INTO acsessTextures VALUES (?,?)",[name,data])
        self.con.commit()

    def getAcsess(self,username):
        self.cursor.execute("SELECT acsessTextures.serializedData FROM acsessTextures INNER JOIN users WHERE users.acsess = acsessTextures.acsess AND users.user_name = (?)",[username])

        serializedData = self.cursor.fetchone()

        return serializedData[0]
    
        

    def checkCredintials(self,username,password):
        self.cursor.execute("SELECT user_name, password FROM users")
        data = self.cursor.fetchall()
        for user in data:

            if user[0] == username and user[1] == password:
                return True
        return False

    def close(self):
        pass


    
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
 

        self.x = 0
        self.y = 0 
        self.click = None
        self.state = "standing"
        self.orientation = "R"
        self.hp = 100

        mainThread = threading.Thread(target=self.main)
        mainThread.start()


    def clientLog(self,events,e=None):
        if e != None:
            print(self.addr," ERROR |", events, e )
        else:
            print(self.addr," log:", events)

    def send(self,data):
        try:
            serialized_data = json.dumps(data) #serialize data
            self.user.sendall(bytes(serialized_data, "utf8"))
        except Exception as e:
            self.clientLog("send error",e)

    def recive(self):
        
        decoder = JSONDecoder()
        try:
            data = self.user.recv(self.BUFSIZ).decode("utf8")
            if not data:
                return {"requestType":"clientDisconnect"}
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
                if response != None:
                    return response
                else:
                    log("error: No data recived")
                    return {"requestType":None}
            
        except socket.timeout:
            return {"requestType":"error","error":"socketTimeout"}
        except Exception as e:
            self.clientLog("recive error",e)
            return {"requestType":"error","error":e}
            
    def requestHandler(self):
        self.user.settimeout(1) 
                
        if self.pendingClient != None and self.battleAccepted == False:
            accept = self.pendingClient.checkIfAccepted()
            if accept:
                    self.clientLog("Both players have accepted the battle")
                    self.send({"requestType":"battleConfirm","battleAccepted":True,"enemyU":self.pendingClient.getUsername(),"startSide":"L"})
                    self.pendingClient.send({"requestType":"battleConfirm","battleAccepted":True,"enemyU":self.username,"startSide":"R"})
                    self.battleAccepted = True
                    self.clientLog("creating battle")
                    startBattle(self.pendingClient,self) #starts battle
        
        data = self.recive() 

        if type(data) != dict or data["requestType"] == "error":
            self.ecounter +=1
        else:
            self.ecounter = 0 
        
        if self.ecounter > 30:
            self.clientLog("maximum recive errors, shutting down connection")
            return False
    
        if data["requestType"] == "clientDisconnect":
            return False
        

        if self.battleAccepted == True: 
            if data["requestType"] == "posData":
                self.x = data["x"]
                self.y = data["y"]
                self.state = data["state"]
                self.orientation = data["orientation"]
                self.hp = data["hp"]
                if "clickPos" in data:
                    self.click = data["clickPos"]
        else:
            if data["requestType"] == "posData": #If user is still sending pos data when no battle exists, attempts to end the game
                self.send({"requestType":"gameOver"})

        if self.battleSent == True and self.battleAccepted == False:
            if data["requestType"]=="battleReq" and data["battleAccepted"]==True: 
                self.clientLog(self.username+" has accepted the battle")
                self.battleAccepted = True
        if data["requestType"] == "startBattle":
            self.clientLog("Battle reqest recieved")
            opponentU = data["enemyU"]
            for client in clients: #Searches list of connected clients
                if client.getUsername() == opponentU and client.isconnected() == True and client.isLoggedIn() == True:
                    self.clientLog("attempting to start battle")
                    client.sendBattleRequest(self.username)
                    self.pendingClient = client
        if data["requestType"] == "getOnlineUsers":
            clientList = []
            for client in clients:
                if client.isconnected() == True and client.isLoggedIn() == True:
                    clientList.append(client.getUsername())
            self.send({"requestType":"getOnlineUsers","onlineUsers":clientList})


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
            clients.remove(self)
            self.connected = False
            self.clientLog([self.addr,"client disconnected"])
            self.user.close()
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
        db = Database()
        if loginData["requestType"] == "loginRequest" and loginData["username"]!= "" and loginData["username"] not in [client.username for client in clients]: #Makes sure username is not blank or already connected
            username = loginData["username"]
            password = loginData["password"]

            if db.checkCredintials(username,password):
                acsess = db.getAcsess(username)

                loginReq = {"requestType":"loginRequest","loginR":True,"acsess":acsess}
                self.send(loginReq)
                self.clientLog("confirmed login: "+username+" at"+"%s:%s" % self.addr)
                self.username = username
                self.loggedIn = True
                self.connected = True
                
                db.close()
                return True
            else:
                loginReq = {"requestType":"loginRequest","loginR":False,"reason":"Invalid username/password"}
                self.send(loginReq)
                return False

 
 
    def getPos(self):
        if self.click != None:
            data = {"requestType":"posData","x":self.x,"y":self.y,"clickPos":self.click,"state":self.state,"orientation":self.orientation,"hp":self.hp}
            self.click = None
            return data
        else:
            return {"requestType":"posData","x":self.x,"y":self.y,"state":self.state,"orientation":self.orientation,"hp":self.hp}

    def getUsername(self):
        return self.username

    def endBattle(self):
        self.send({"requestType":"gameOver"})
        self.battleAccepted = False
        self.battleSent =  False
        self.pendingBattle = False
        self.pendingClient = None
        self.requestedEnemy = None

        self.x = 0
        self.y = 0 
        self.click = None
        self.state = "standing"
        self.orientation = "R" 
        self.hp = 100


def startBattle(client1,client2):
    battle = Battle(client1,client2)
    battles.append(battle)



class Battle:
    def __init__(self,client1,client2):
        print("initializing battle.")
        self.client1 = client1
        self.client2 = client2

        self.width = 120
        self.height = 240
        battleThread = threading.Thread(target=self.sendPos)
        battleThread.start()

        





    def sendPos(self):
        self.battle =  True
        while self.client1.isconnected() == True and self.client2.isconnected() == True and self.battle == True:
            data1 = self.client1.getPos()
            self.client2.send(data1)

            data2 = self.client2.getPos()
            self.client1.send(data2)


            # if "clickPos" in data1: OLD
            #     data2["reduceHp"] = self.checkClick(data1,data2)
            # elif "clickPos" in data2:
            #     data1["reduceHp"] = self.checkClick(data2,data1)
            if data1["hp"] <= 0 or data2["hp"] <= 0:
                self.battle = False
            
        self.endBattle()

    
    # def checkClick(self,data1,data2): OLD 
    #     pos = data1["clickPos"]
    #     print(pos)
    #     x1 = pos[0]
    #     y1 = pos[1]
    #     x = data2["x"]
    #     y = data2["y"]
    #     state = data2["state"]
    #     if state != "crouching":
    #         if  x-(self.width/2) <= x1 <= x + (self.width/2) and y-(self.height/2) <= y1 <= y + (self.height/2):
    #             return 10
    #         else:
    #             return 0
    #     if state == "crouching":
    #         if  x-(self.width/2) <= x1 <= x + (self.width/2) and y-((self.height/2)/2) <= y1 <= y + ((self.height/2)/2):
    #             return 10
    #         else:
    #             return 0

    def endBattle(self):
        self.client1.endBattle()
        self.client2.endBattle()
        print("battle over")
        #send enemy disconnect to all connected clients
    


#OLD
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




    