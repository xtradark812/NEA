import pygame
import sys
import socket
import json
import threading

width = 500
height = 500

win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Client")

clientnumber = 0



class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server,self.port)
        self.BUFSIZ = 3000
        self.connected = False
        self.enemyUsername = None

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
        try:
            serialized_data = json.dumps(data) #serialize data
            self.client.sendall(bytes(serialized_data, "utf8")) ### SENDS DATA TO SERVER 
            return True
        except socket.error as e:
            print("server disconnected")
            self.client.close()
            self.connected = False
            self.enemyUsername = None
            return False
        except Exception as e:
            print("Invalid response from server", e)
            return False

    def recive(self):
        try:
            response = self.client.recv(self.BUFSIZ) ### WAITS FOR DATA TO BE RETURNED
            if not self.client.recv:
                print("Disconnected")
                self.client.close()
                self.connected = False
                self.enemyUsername = None
                return {"requestType":"disconnected"}
            else:
                deserialized = json.loads(response.decode("utf8"))
                return deserialized
        except Exception as e:
            print("Invalid response from server", e)
            return {"requestType":"reciveError"}
        

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.connected = True

        except Exception as e:
            print("Error connecting to server:",e)
            return False

        self.username = self.login("test")
        if self.username == None:
            return False
        elif self.username != None:
            return True

    def startMatch(self):
        if self.connected == True:
            self.enemyUsername = None
            self.enemyPos = None
            self.waitForEnemyThread = threading.Thread(target=self.waitForBattle)
            self.waitForEnemyThread.start()
            return True
        else:
            return False

    #def getPos(self):
     #   return self.pos
    
    def login(self,username): #function pulled from previous messaging project

        loginReq = {"requestType":"loginRequest","username":username}

        self.send(loginReq)
        response = self.recive()

        if response["requestType"] == "disconnected":
            return None
            
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

    
    def waitForBattle(self):
        while True:
            response = self.recive()

            if response["requestType"] == "disconnected":
                break

            if response["requestType"]=="battleReq": 
                print("starting a battle with", response["enemyU"])
                accept = {"requestType":"battleReq","battleAccepted":True}
                self.send(accept)
                self.enemyUsername = response["enemyU"]
                recivePosThread = threading.Thread(target=self.recivePosData)
                recivePosThread.start()
                break


    def recivePosData(self):
        while True:
            data = self.recive()

            if data["requestType"] == "disconnected":
                break

            if data["requestType"] == "posData":
                self.enemyPos = data #check if data being recived is pos data
            if data["requestType"] == "opponentDisconnect":
                self.enemyUsername = None
                break
            

    def enemyPos(self):
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
    
    def move(self,data=None):
        
        if data == None:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                self.x -= self.vel

            if keys[pygame.K_RIGHT]:
                self.x += self.vel

            if keys[pygame.K_UP]:
                self.y -= self.vel

            if keys[pygame.K_DOWN]:
                self.y += self.vel
        else:
            self.x = data["x"]
            self.y = data["y"]
        
        self.rect.center = (self.x, self.y)

    def getPos(self):
        return {"x":self.x,"y":self.y}


    
     


def render(win,all_sprites):
    all_sprites.update() #update sprites
    pygame.display.update()
    win.fill((255,255,255))
    all_sprites.draw(win) #DRAW SPRITES
    


def main():

    run = True
    
    n = Network()
    connected = n.connect()
    n.startMatch()

    # #startPos = n.getPos()
    # p = Player(50,50,100,100,(0,255,0)) #player should be init fron network?

    elapsedTime = 0 #variable for counting ticks since init
    clock = pygame.time.Clock() #keep track of ticks
    # p2Connected = False
    enemyUsername = None

    all_sprites = pygame.sprite.Group()
    p = Player(50,50,0,255,0)
    all_sprites.add(p)

    while run:

        if n.isConnected() == False:
            break

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
        render(win,all_sprites) #RENDER

        pos = p.getPos().update({"requestType":"posData"})
        n.send(pos)
        

        if n.enemyConnected() != False and enemyUsername == None:
            enemyUsername = n.enemyConnected()
            p2 = Player(50,50,255,0,0)
            all_sprites.add(p2)
        elif n.enemyConnected() != False and enemyUsername != None:
            p2.move(n.enemyPos())



        

        # if n.checkEnemyConnected() != False and p2Connected == False:
        #     enemyUsername = n.checkEnemyConnected()
        #     p2 = Player(50,50,100,100,(0,0,255))
        #     p2Connected = True
        
        # if p2Connected == True:
        #    p2.move(n.getEnemyPos())
        
        # redrawWindow(win,p)

main()





