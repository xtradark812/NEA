from json.decoder import JSONDecoder

import pygame
import sys
import socket
import json
import threading


width = 1920
height = 1080
pygame.init()
win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Client")

clientnumber = 0



class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server,self.port)
        self.BUFSIZ = 1024
        self.connected = False
        self.enemyUsername = None
        self.onlineUsers = []

    # def sendAndRecive(self,data):
    #     try:
    #         serialized_data = json.dumps(data) #serialize data
    #         self.client.sendall(bytes(serialized_data, "utf8")) ### SENDS LOGIN DATA TO SERVER [loginRequest,username]
    #         response = json.loads(self.client.recv(self.BUFSIZ).decode("utf8")) ### WAITS FOR DATA TO BE RETURNED
    #         return response
    #     except Exception as e:s
    #         print("Invalid response from server", e)
    #         return False

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
                print("response:",response)
                return response

        except Exception as e:
            print("error",e)
        

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.connected = True

        except Exception as e:
            print("Error connecting to server:",e)
            return False

        givenUsername = str(input("Please enter a username:"))
        self.username = self.login(givenUsername)
        if self.username == None:
            return False
        elif self.username != None:
            print("connected")
            return True

    def main(self):
        if self.connected == True:
            self.enemyUsername = None
            self.enemyPos = None
        while True:
            response = self.recive()
            if response["requestType"]=="battleReq":
                self.waitForBattle(response)
            if response["requestType"] == "getOnlineUsers":
                self.onlineUsers = response["onlineUsers"]
    
    def startBattle(self):
        self.send({"requestType":"getOnlineUsers"})
        while bool(self.onlineUsers) == False:
            pass
        print(self.onlineUsers)
        enemyU = input("Please pick a username: ")
        if enemyU in self.onlineUsers:
            print("sending battle request")
            self.send({"requestType":"startBattle","enemyU":enemyU})
                    
            
    #def getPos(self):
     #   return self.pos
    
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
        if self.enemyUsername != None:
            return self.enemyUsername
        else:
            return False

    
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
                            self.enemyPos = data #check if data being recived is pos data
                        if data["requestType"] == "opponentDisconnect":
                            self.enemyUsername = None
                            break
                    elif data == None:
                        print("no data")


            

    def getEnemyPos(self):
        return self.enemyPos
            

        #this waits for an enemy to connect, and once it connects it will constantly receive pos
    
    def isConnected(self):
        if self.connected == True:
            return True
        else:
            return False
    





        

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,r,g,b):

        pygame.sprite.Sprite.__init__(self) #sprite init function (required by pygame)
        
        self.x = x
        self.y = y 

        self.color = r,g,b

        self.vel = .5

        

        self.image = pygame.Surface((50, 50)) #temporarly a square
        self.image.fill(self.color)  #temporarily a square

        self.rect = self.image.get_rect() #will  define players hitbox as size of the image

        self.rect.center = (self.x, self.y)


    #def draw(self,win):
    #    pygame.draw.rect(win,self.color,self.rect)
    
    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel

        if keys[pygame.K_RIGHT]:
            self.x += self.vel

        if keys[pygame.K_UP]:
            self.y -= self.vel

        if keys[pygame.K_DOWN]:
            self.y += self.vel
        self.rect.center = (self.x, self.y)


    
    def dataMove(self,data):
        self.x = data["x"]
        self.y = data["y"]
        self.rect.center = (self.x, self.y)

    def getPos(self):
        return {"requestType":"posData","x":self.x,"y":self.y}


    
     


def renderBattle(win,all_sprites):
    all_sprites.update() #update sprites
    pygame.display.update()
    win.fill((255,255,255))
    all_sprites.draw(win) #DRAW SPRITES



def loadNetwork():
    n = Network()
    n.connect()
    thread = threading.Thread(target=n.main)
    thread.start()
    return n

def mainMenu():
    menuScreen = True
    while menuScreen:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
                break
        
        
        
        win.fill((255,255,255))
        font = pygame.font.Font('freesansbold.ttf',115)
        textSurface = font.render('project-steel', True, (0,0,0))
        TextRect = textSurface.get_rect()
        TextRect.center = ((width/2),(height/2))
        win.blit(textSurface, TextRect)
        pygame.display.update()
        


def main(n):

    run = True
    
    elapsedTime = 0 #variable for counting ticks since init
    clock = pygame.time.Clock() #keep track of ticks

    enemyUsername = None

    all_sprites = pygame.sprite.Group()
    p = Player(50,50,0,255,0)
    all_sprites.add(p)
    

    while run:

        # if n.isConnected() == False:
        #     break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
                break

        

        

        # n.sendPos(p.getPos())
        dt = clock.tick() #the following method returns the time since its last call in milliseconds
        elapsedTime += dt
        
        
        p.move() #checks for key prsses, and moves charachter
        


        

        if n.enemyConnected() != False and enemyUsername == None:
            print("initializing enemy sprite")
            enemyUsername = n.enemyConnected()
            p2 = Player(50,50,255,0,0)
            all_sprites.add(p2)
        if n.enemyConnected() != False and enemyUsername != None and n.getEnemyPos() != None:
            n.send(p.getPos())
            p2.dataMove(n.getEnemyPos())


        renderBattle(win,all_sprites) #RENDER
        

        # if n.checkEnemyConnected() != False and p2Connected == False:
        #     enemyUsername = n.checkEnemyConnected()
        #     p2 = Player(50,50,100,100,(0,0,255))
        #     p2Connected = True
        
        # if p2Connected == True:
        #    p2.move(n.getEnemyPos())
        
        # redrawWindow(win,p)

mainMenu()





