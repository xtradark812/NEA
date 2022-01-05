from typing import Counter

import pygame
import sys

import threading

from ui import Button 
from ui import InputBox
from client_network import Network


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
        pygame.init()
        self.controls = Controls()
        self.n = Network()
        self.width = 1280
        self.height = 720
        
        self.win = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Client")
        self.connected = False

    
    def loadNetwork(self,username):
        connect = self.n.connect(username)
        if connect:
            thread = threading.Thread(target=self.n.main)
            thread.start()
            return True
        else:
            return False

    def renderBattle(self,win,all_sprites):
        all_sprites.update() #update sprites
        pygame.display.update()
        win.fill((255,255,255))
        all_sprites.draw(win) #DRAW SPRITES
    

    #TODO load textures method

    def renderUI(self):
        pass
    
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
                            self.connected = self.loadNetwork(inputBoxes[0].text)
                            if self.connected:
                                self.n.startBattle()
    
            if self.n.enemyConnected() != None and self.connected and self.n.getEnemyPos() != None:
                self.battle() #START GAME
        
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
        e = Player(50,50,255,0,0,self) #TODO: need to pick which side each player spawns on
        all_sprites.add(p)
        all_sprites.add(e)

        

        while run and self.connected:
            pos = None
            pygame.time.delay(20)
            self.connected = self.n.isConnected()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or self.connected == False:
                    run = self.exit()
                    #return back to menu screen?
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
            

            
            p.move() #checks for key prsses, and moves charachter

           
            try:  #network things have exception handling
                info = p.getPos()
                
                if pos != None:
                    info["clickPos"] = pos
                    print(pos)
                
                self.n.send(info)
                enemyData = self.n.getEnemyPos()
                e.dataUpdate(enemyData)
            except Exception as exc:
                #TODO check when this happens
                print(exc)


            self.renderBattle(self.win,all_sprites) #RENDER
        
    def exit(self):
        pygame.quit()
        sys.exit()
        #TODO disable network
        #TODO save anything?
        return False


g = Game()
g.mainMenu()


