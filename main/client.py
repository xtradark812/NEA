from json.decoder import JSONDecoder

import pygame
import sys
import socket
import json
import threading




class Controls():
    def __init__(self):
        self.jump = pygame.K_UP
        self.crouch = pygame.K_DOWN
        self.left = pygame.K_LEFT
        self.right = pygame.K_RIGHT
        

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
    def __init__(self,x,y,r,g,b,game):
        self.playerWidth = 120
        self.playerHeight = 240
        self.game = game

        pygame.sprite.Sprite.__init__(self) #sprite init function (required by pygame)
        
        self.x = self.game.width/4 #need to check which side to spawn on
        self.y = self.game.height -self.playerHeight/2 #replace 50 with height from real x

        self.color = r,g,b

        self.vel = 10


        

        self.image = pygame.Surface((self.playerWidth, self.playerHeight)) #temporarly a square
        self.image.fill(self.color)  #temporarily a square

        self.rect = self.image.get_rect() #will  define players hitbox as size of the image

        self.rect.center = (self.x, self.y)

        self.jumpcount = 10
        self.doubleJumpCount = 10
        self.doubleJumpsAllowed = 3
        self.jumpsize = 4 # THE BIGGER THE VALUE THE SMALLER THE JUMP

        #DO NOT CHANGE 
        self.jumping = False
        self.doubleJumps = 0
        self.readyForDoubleJump = False
        self.startingY = game.height -self.playerHeight/2
        self.changeList = []

    #def draw(self,win):
    #    pygame.draw.rect(win,self.color,self.rect)
    
    def move(self):
        wait = 1
        keys = pygame.key.get_pressed()

        if keys[self.game.controls.left] and self.x > self.vel + self.playerWidth/2:
            self.x -= self.vel

        if keys[self.game.controls.right] and self.x < g.width - self.vel - self.playerWidth/2 : #replace width
            self.x += self.vel

        if keys[self.game.controls.jump] and self.y > self.vel + self.playerHeight/2 and self.jumping == False:
            self.jumping = True
            self.startingY = self.y
            wait = 0

        # if keys[pygame.K_DOWN] and self.y < height - 100/2 - self.vel: CROUCH
        #     self.y += self.vel

        if self.jumping == True and wait == 1:

            if self.jumpcount > 0: #replace with jumpcount original
                change = self.jumpcount * self.jumpcount/self.jumpsize #Quadradic formula for jump
                self.y -= change
                self.changeList.append(change)
                self.jumpcount -= 1

            if not keys[pygame.K_UP]:
                self.readyForDoubleJump = True
            if self.doubleJumps < self.doubleJumpsAllowed and keys[pygame.K_UP] and self.readyForDoubleJump == True:
                self.doubleJumps += 1
                self.jumpcount = self.doubleJumpCount
                self.readyForDoubleJump = False

            
            if self.jumpcount == 0 and self.y != self.startingY: #player goes back to the ground
                self.y += self.changeList.pop(self.changeList.index(min(self.changeList)))

            if self.jumpcount == 0 and not self.changeList: #once player is on the ground
                if self.y != self.startingY:
                    print("error")
                    print(self.startingY-self.y)
                    self.y = self.startingY
                self.jumpcount = 10 #reset jump count
                self.doubleJumps = 0
                self.jumping = False
                self.readyForDoubleJump = False


        self.rect.center = (self.x, self.y)


    
    def dataMove(self,data):
        self.x = data["x"]
        self.y = data["y"]
        self.rect.center = (self.x, self.y)

    def getPos(self):
        return {"requestType":"posData","x":self.x,"y":self.y}


    
class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False     

class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
        self.rect = pygame.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.font = font = pygame.font.Font('freesansbold.ttf',115)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)




class Game():
    def __init__(self):
        pygame.init()
        self.controls = Controls()

        self.width = 1280
        self.height = 720
        
        self.win = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Client")

    
    def loadNetwork(self,username):
        self.n = Network()
        self.n.connect(username)
        thread = threading.Thread(target=self.n.main)
        thread.start()

    def renderBattle(self,win,all_sprites):
        all_sprites.update() #update sprites
        pygame.display.update()
        win.fill((255,255,255))
        all_sprites.draw(win) #DRAW SPRITES
    



    def mainMenu(self):
        buttons = [Button("Start",self.width/2,self.height/2,(0,255,0))]
        inputBoxes = [InputBox(100, 100, 140, 32)]
        menuScreen = True
        
        while menuScreen:
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menuScreen = self.exit()
                    break
                
                for box in inputBoxes:
                    box.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.click(pos):
                            print(inputBoxes[0].text)
                            self.loadNetwork(inputBoxes[0].text)
                            
                            self.battle()
                        #START GAME
        
            #Draw Menu screen
            self.win.fill((255,255,255))
            font = pygame.font.Font('freesansbold.ttf',115)
            textSurface = font.render('project-steel', True, (0,0,0))
            TextRect = textSurface.get_rect()
            TextRect.center = ((self.width/2),(self.height/6))
            self.win.blit(textSurface, TextRect)

            #Update input boxes
            for box in inputBoxes:
                box.update()

            #Draw Buttons
            for button in buttons:
                button.draw(self.win)

            #draw input boxes
            for box in inputBoxes:
                box.draw(self.win)
                
            #Update Display
            pygame.display.update()
        


    def battle(self):
    
        run = True

        all_sprites = pygame.sprite.Group()

        p = Player(50,50,0,255,0,self)
        all_sprites.add(p)
    

        while run:
            pygame.time.delay(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = self.exit()
                    break

    
            p.move() #checks for key prsses, and moves charachter

            self.renderBattle(self.win,all_sprites) #RENDER
        
    def exit(self):
        pygame.quit()
        sys.exit()
        #disable network
        #save anything?
        return False


g = Game()
g.mainMenu()


