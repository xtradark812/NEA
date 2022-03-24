#MAIN TODO:
# - finish menu screen and properly load into game
# - UI for in game, health bar, and register hits
# - database for login
# - offline AI enemy



from typing import Counter

import pygame
import sys

import threading

from sympy import re

from ui import Button, InputBox, Textures, OnlineList

from client_network import Network

def log(event):
    print("log: ", event)
    #TODO save to file

class Controls():
    def __init__(self):
        self.jump = pygame.K_UP
        self.crouch = pygame.K_DOWN
        self.left = pygame.K_LEFT
        self.right = pygame.K_RIGHT

    def change(): #TODO change controls 
        pass

    def loadSettings():
        pass #TODO load settings saved?    

     

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,r,g,b,game):
        self.playerWidth = 120
        self.playerHeight = 240
        self.game = game

        pygame.sprite.Sprite.__init__(self) #sprite init function (required by pygame)
        
        self.x = self.game.width/4 #TODO need to check which side to spawn on
        self.y = self.game.height -self.playerHeight/2 

        self.color = r,g,b

        self.vel = 10

        self.hp = 100

        
        #CREATING CHARACHTER
        self.image = pygame.Surface((self.playerWidth, self.playerHeight)) #temporarly a square
        self.image.fill(self.color)  #temporarily a square
        self.rect = self.image.get_rect() #will  define players hitbox as size of the image
        self.rect.center = (self.x, self.y)

        #FOR JUMPING
        self.jumpcount = 10
        self.doubleJumpCount = 10
        self.doubleJumpsAllowed = 3
        self.jumpsize = 4 # THE BIGGER THE VALUE THE SMALLER THE JUMP

        #CONSTANTS (do not change)
        self.jumping = False
        self.doubleJumps = 0
        self.readyForDoubleJump = False
        self.startingY = game.height -self.playerHeight/2 
        self.changeList = []
        self.counter = 0

    #def draw(self,win):
    #    pygame.draw.rect(win,self.color,self.rect)

    def reudceHp(self, ammount):
        self.hp -= ammount
        print("i took",ammount,"damage") #for debugging
    
    def resetHp(self):
        self.hp = 100


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
            self.counter +=1
            if self.jumpcount > 0 and self.counter%2 == 0: #replace with jumpcount original
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

            
            if self.jumpcount == 0 and self.y != self.startingY and self.counter%2 == 0: #player goes back to the ground
                self.y += self.changeList.pop(self.changeList.index(min(self.changeList)))

            if self.jumpcount == 0 and not self.changeList: #once player is on the ground
                if self.y != self.startingY:
                    print("error")
                    print(self.startingY-self.y)
                    self.y = self.startingY
                self.jumpcount = 10 #reset jump count
                self.doubleJumps = 0
                self.counter = 0
                self.readyForDoubleJump = False
                self.jumping = False
                


        self.rect.center = (self.x, self.y)


    
    def dataUpdate(self,data):
        if "reduceHp" in data:
            self.reudceHp(data["reduceHp"])
            
        self.x = data["x"]
        self.y = data["y"]
        self.rect.center = (self.x, self.y)

    def getPos(self):
        return {"requestType":"posData","x":self.x,"y":self.y}


    



class Game():
    def __init__(self):
        log("Initializing game")
        pygame.init()
        self.controls = Controls()
        self.n = Network()
        self.width = 1280
        self.height = 720
        
        self.textureObject = Textures(self.width,self.height)

        self.win = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Client")
        log("Game initialized")


    

    def renderBattle(self,win,all_sprites):
        all_sprites.update() #update sprites
        pygame.display.update()
        win.fill((255,255,255))
        all_sprites.draw(win) #DRAW SPRITES
    

    #TODO load textures method

    def renderUI(self):
        pass #TODO use this method to render HP bar
    
    def loginScreen(self):
        #Menu UI
        buttons = [Button("Login",self.width/2,self.height/2+70,(0,0,0),150,100)]
        inputBoxes = [InputBox(self.width/2-30, (self.height/2)-100+25, 140, 32),InputBox(self.width/2-30, (self.height/2)-100-25, 140, 32)]
 

        #Menu loop
        loginScreen = True
        log("Login Screen loaded")
        while loginScreen:
        
            for event in pygame.event.get(): #Event handler

                if event.type == pygame.QUIT: 
                    loginScreen = self.exit()
                    break
                
                for box in inputBoxes: 
                    box.handle_event(event) #handle input box events

                if event.type == pygame.MOUSEBUTTONDOWN: #handle button events
                    pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.click(pos): #if a button is clicled chech which one

                            if button.text == "Login":
                                log("Attempting to connect to server")
                                if self.n.connect(inputBoxes[1].text,inputBoxes[0].text): #attempts to connect with given username and password)
                                    log("Connected")
                                    self.acsess = self.n.getAcsess()
                                    self.mainMenu()

                                    
            #Draw Login screen
            self.win.fill((255,255,255))
            background = self.textureObject.getLoginBackground()
            self.win.blit(background,(0, 0))

            font = pygame.font.Font('freesansbold.ttf',115)
            textSurface = font.render('Login', True, (0,0,0))
            TextRect = textSurface.get_rect()
            TextRect.center = ((self.width/2),(self.height/6))
            self.win.blit(textSurface, TextRect)

            #Update input boxes
            for box in inputBoxes:
                box.update()

            #Draw Buttons
            for button in buttons:
                button.draw(self.win)

            #Draw input boxes
            for box in inputBoxes:
                box.draw(self.win)
            



            #Update Display
            pygame.display.update()


    def mainMenu(self):
        #Menu UI
        self.textures = self.texture.loadTextures(self.acsess)
        
        onlineList = OnlineList(self.width/8,70)
        requestBox = None
        #Menu loop
        self.n.startLoop("menu")
        onlineUsers = self.n.getOnlineUsers()
        onlineList.updateUsers(onlineUsers)
        menuScreen = True


        log("Menu loaded")
        while menuScreen:
        
            for event in pygame.event.get(): #Event handler

                if event.type == pygame.QUIT: 
                    menuScreen = self.exit()
                    break
    

                if event.type == pygame.MOUSEBUTTONDOWN: #handle button events

                    onlineUsers = self.n.getOnlineUsers()

                    onlineList.updateUsers(onlineUsers)
                    
                    pos = pygame.mouse.get_pos()
                    
                    if requestBox != None:
                        if requestBox.click(pos):
                            self.n.acceptBattle() 
                            
                    eRequest = onlineList.click(pos)
                    if eRequest != None and self.n.isConnected():

                        log("Attempting to start battle")
                        self.n.sendBattleReq(eRequest)
                                


                                    
                           

            if self.n.isConnected():
                if self.n.checkPendingBattle() == True:
                    requestBox = Button("Battle request from: "+ self.n.checkPendingEnemy(),900,600,(256,0,0),300,100)
                enemyU, startSide = self.n.getEnemyStartside()
                if enemyU != None: #if a request has been recived
                    log("Loading battle")
                    self.battle(enemyU,startSide)


                    
    
            # if self.n.enemyConnected() != None and self.n.isConnected() and self.n.getEnemyData() != None: #if enemy is ready then load battle
            #     self.battle() #START GAME
        

            #Draw Menu screen
            self.win.fill((255,255,255))
            self.win.blit(self.textures["background"], (0, 0))


            
            font = pygame.font.Font('freesansbold.ttf',20)
            textSurface = font.render('Online Users', True, (0,0,0))
            TextRect = textSurface.get_rect()
            TextRect.center = ((self.width/8),(50))
            self.win.blit(textSurface, TextRect)


            #Draw reuqests
            if requestBox != None:
                requestBox.draw(self.win)


            #Draw online list
            onlineList.draw(self.win)

            #Update Display
            pygame.display.update()
        


    def battle(self,enemyU,startSide):


        #initiate sprites
        all_sprites = pygame.sprite.Group()
        p = Player(50,50,0,255,0,self)
        e = Player(50,50,255,0,0,self) #TODO: need to pick which side each player spawns on using startside
        all_sprites.add(p)
        all_sprites.add(e)

        
        run = True
        log("Battle loaded")
        self.n.startLoop("battle")

        while run and self.n.isConnected() and self.n.enemyConnected():
            clickPos = None
            pygame.time.delay(20)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = not self.exit()
                    #return back to menu screen?
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clickPos = pygame.mouse.get_pos()
                    
            

            
            p.move() #checks for key prsses, and moves charachter

           #Network handler

            try:  #network things have exception handling

                #Send player data
                playerData = p.getPos()
                if clickPos != None:
                    playerData["clickPos"] = clickPos
                self.n.send(playerData)

                #Update enemy data
                enemyData = self.n.getEnemyData()
                if enemyData != None:   
                    e.dataUpdate(enemyData)

            except Exception as exc:
                #TODO check when this happens
                log(exc)


            self.renderBattle(self.win,all_sprites) #Render battle
        
    def exit(self):
        pygame.quit()
        sys.exit()
        #TODO disable network
        #TODO save anything?
        return True


g = Game()
g.loginScreen()