import os
import pygame
import sys

from ui import Button, HealthBar, InputBox, OnlineList
from client_network import Network

def log(event):
    print("log: ", event)


class Controls():
    def __init__(self):
        #Currently set to arrow keys as default
        self.jump = pygame.K_UP
        self.crouch = pygame.K_DOWN
        self.left = pygame.K_LEFT
        self.right = pygame.K_RIGHT

    def change():
        #This can be expanded later if necessary 
        pass

    def loadSettings():
        #This can be expanded later if necessary 
        pass    

class Textures:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        #Login background will be loaded seperatley, because access is not available untill after login
        self.loginBackground = pygame.image.load(os.path.join("textures", "background.png"))
        self.loginBackground = pygame.transform.scale(self.loginBackground,(width, height))

    def getLoginBackground(self):
        #Returns login background
        return self.loginBackground

    def loadTextures(self,access):
        #Textures and animations that are required
        textures = ["standing","enemyStanding","background","crouching","enemyCrouching","jumping","enemyJumping"]
        animations = ["walking","enemyWalking"]

        #Empty dictionaries for loaded textures
        loadedTextures = {}
        loadedAnimations = {}

        #This loop will load each texture depending on the access given 
        for texture in textures: 
            try:
                loadedTextures[texture] = pygame.image.load(os.path.join("textures", access[texture]+".png"))
            except:
                log("texture not found: "+texture)
            
        #This loop will load each animation depending on the access given
        for animation in animations:
            loadedAnimations[animation] = []
            #animations will always have 4 images
            for i in range(4):
                try:
                    loadedAnimations[animation].append(pygame.image.load(os.path.join("textures",access[animation], str(i)+".gif")))
                except:
                    log("animation not found: "+animation)
        
        #Resize background to window size
        try:
            loadedTextures["background"] = pygame.transform.scale(loadedTextures["background"],(self.width, self.height))
        except:
            log("No background")

        #Return loaded textures
        return loadedTextures, loadedAnimations     

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,r,g,b,game,cType,startside):

        #sprite init function (required by pygame)
        pygame.sprite.Sprite.__init__(self) 

        #set attributes
        self.playerWidth = 120
        self.playerHeight = 240
        self.game = game
        self.state = "standing"
        self.y = self.game.height - 140 -self.playerHeight/2 
        self.color = r,g,b
        self.vel = 10
        self.hp = 100

        #Charachter must be spawned in the correct location which is decided by the server
        if startside == "L":
            self.orientation = "R" 
            self.x = self.game.width/4
        else:
            self.orientation = "L"
            self.x = self.game.width*3/4         

        
        #CREATING CHARACHTER
        if cType == "p":
            self.image = self.game.textures["standing"]
        if cType == "e":
            self.image = self.game.textures["enemyStanding"]
        if self.orientation == "L":
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect() #will  define players hitbox as size of the image
        self.rect.center = (self.x, self.y)

    
        #FOR JUMPING (can be changed)
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
        self.walkcounter = 0

    def reudceHp(self, ammount):
        #Reduce hp by given ammount
        self.hp -= ammount
    

    def move(self):
        wait = 1

        keys = pygame.key.get_pressed()

        #state is reset to standing after each loop
        self.state = "standing"

        #Left movment
        if keys[self.game.controls.left] and self.x > self.vel + self.playerWidth/2:
            self.x -= self.vel
            self.state = "walking"
            self.orientation = "L"

        #Right movment
        if keys[self.game.controls.right] and self.x < g.width - self.vel - self.playerWidth/2 :
            self.x += self.vel
            self.state = "walking"
            self.orientation = "R"

        #Initiate a jump
        if keys[self.game.controls.jump] and self.y > self.vel + self.playerHeight/2 and self.jumping == False:
            self.jumping = True
            self.startingY = self.y
            wait = 0

        #Crouch
        if keys[pygame.K_DOWN] and self.jumping == False:
            self.state = "crouching"
            pass
        
        #Jump mechanics
        if self.jumping == True and wait == 1:

            #for jumping texture
            self.state = "jumping"

            #increment jump counter
            self.counter +=1

            #while the player is increasing height
            if self.jumpcount > 0 and self.counter%2 == 0: 
                #Quadradic formula for jump used to calculate correct position changfe
                change = self.jumpcount * self.jumpcount/self.jumpsize 

                #Apply change
                self.y -= change
                
                #Record change on change list
                self.changeList.append(change)
                
                #reduce jumpcount
                self.jumpcount -= 1

            #arm double jump
            if not keys[pygame.K_UP]:
                self.readyForDoubleJump = True

            #Double jump
            if self.doubleJumps < self.doubleJumpsAllowed and keys[pygame.K_UP] and self.readyForDoubleJump == True:
                self.doubleJumps += 1
                self.jumpcount = self.doubleJumpCount
                self.readyForDoubleJump = False

            #once player has reached highest point, reverse the changes made to return player to the ground
            if self.jumpcount == 0 and self.y != self.startingY and self.counter%2 == 0:
                self.y += self.changeList.pop(self.changeList.index(min(self.changeList)))

            #Reset everything once player is on the ground
            if self.jumpcount == 0 and not self.changeList: 
                self.jumpcount = 10 
                self.doubleJumps = 0
                self.counter = 0
                self.readyForDoubleJump = False
                self.jumping = False
        
        #Load correct texture depending on state
        if self.state == "jumping":
            self.image = self.game.textures["jumping"]
        if self.state == "crouching":
            self.image = self.game.textures["crouching"]
        if self.state == "standing":
            self.image = self.game.textures["standing"]
        if self.state == "walking":
            #Play walk animation
            if self.walkcounter >= 3:
                self.walkcounter = 0
            self.image = self.game.animations["enemyWalking"][self.walkcounter]
            self.walkcounter += 1

        #Adjust texture based on orientation
        if self.orientation == "L":
            self.image = pygame.transform.flip(self.image, True, False)

        #Finalise chanegs to charachter rect
        self.rect.center = (self.x, self.y)


    
    def dataUpdate(self,data):
        #Takes the enemys data as a paramater and updates charachter accoordingly    
        self.x = data["x"]
        self.y = data["y"]
        self.state = data["state"]
        self.orientation = data["orientation"]
        self.hp = data["hp"]
        
        if self.state == "jumping":
            self.image = self.game.textures["enemyJumping"]
        if self.state == "crouching":
            self.image = self.game.textures["enemyCrouching"]
        if self.state == "standing":
            self.image = self.game.textures["enemyStanding"]
        if self.state == "walking":
            if self.walkcounter >= 3:
                self.walkcounter = 0
            self.image = self.game.animations["enemyWalking"][self.walkcounter]
            self.walkcounter += 1

        if self.orientation == "L":
            self.image = pygame.transform.flip(self.image, True, False)

        #Finalise chanegs to charachter rect
        self.rect.center = (self.x, self.y)

    def getPos(self):
        #return player data to be sent to the server
        return {"requestType":"posData","x":self.x,"y":self.y,"state":self.state,"orientation":self.orientation,"hp":self.hp}


    def getHP(self):
        #return hp
        return self.hp

    def checkClick(self,clickpos,enemyPos):
        #Check if the click was on the sprite
        if self.rect.collidepoint(clickpos):

            #check how close enemy is
            xDistance = abs(self.x-enemyPos[0])
            yDistance = abs(self.y-enemyPos[1])

            if xDistance < 200 and yDistance < 200:
                #reduce hp
                self.reudceHp(10)

        #check if user has died
        if self.hp <= 0:
            return False
        else:
            return True

class Game():
    def __init__(self):
        log("Initializing game")
        #init pygame
        pygame.init()
        #init controls object
        self.controls = Controls()
        #init network object
        self.n = Network()
        #init textures  object
        self.textureObject = Textures(self.width,self.height)

        #game attributes
        self.width = 1280
        self.height = 720

        #pygame window
        self.win = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Client")


        log("Game initialized")


    

    def renderBattle(self,win,all_sprites):
        all_sprites.update() #update sprites
        pygame.display.update() #uptade display
        win.fill((255,255,255))
        self.win.blit(self.textures["background"], (0, 0)) #draw background
        all_sprites.draw(win) #DRAW SPRITES
    

    
    def loginScreen(self):
        #Menu UI
        buttons = [Button("Login",self.width/2,self.height/2+70,(0,0,0),150,100)]
        inputBoxes = [InputBox(self.width/2-30, (self.height/2)-100+25, 140, 32),InputBox(self.width/2-30, (self.height/2)-100-25, 140, 32)]


        #Menu loop
        loginScreen = True
        log("Login Screen loaded")
        while loginScreen:
            for event in pygame.event.get(): #Event handler

                if event.type == pygame.QUIT: #check if user has closed the game
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
                                    self.access = self.n.getaccess()
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
        self.textures,self.animations = self.textureObject.loadTextures(self.access)
        
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

                    onlineUsers = self.n.getOnlineUsers() #done when mouse clicked only to avoid too many requests

                    onlineList.updateUsers(onlineUsers)
                    
                    pos = pygame.mouse.get_pos()
                    
                    #if there is a request box, and it is clicked, accept pending battle
                    if requestBox != None:
                        if requestBox.click(pos):
                            self.n.acceptBattle() 

                    #check if a request has been made        
                    eRequest = onlineList.click(pos)
                    if eRequest != None and self.n.isConnected():
                        #if a request was made, attempt to send to server
                        log("Attempting to start battle")
                        self.n.sendBattleReq(eRequest)
                                


                                    
            if self.n.isConnected():
                #Check if a battle request whas been recived
                if self.n.checkPendingBattle() == True:
                    #Display battle request
                    requestBox = Button("Battle request from: "+ self.n.checkPendingEnemy(),900,600,(255,0,0),350,100)
                
                #check if enemy user is ready to battle
                enemyU, startSide = self.n.getEnemyStartside()
                if enemyU != None: #if user is ready to battle
                    log("Loading battle")
                    self.battle(enemyU,startSide)

                    #after battle is complete, reset all variables
                    enemyU = None
                    startSide = None
                    requestBox = None


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
        if startSide == "L":
            p = Player(50,50,0,255,0,self,"p","L")
            e = Player(50,50,255,0,0,self,"e","R")
            healthbarP = HealthBar(50,50,50)
            healthbarE = HealthBar(50,1020,50)
        else:
            p = Player(50,50,0,255,0,self,"p","R")
            e = Player(50,50,255,0,0,self,"e","L")
            healthbarE = HealthBar(50,50,50)
            healthbarP = HealthBar(50,1020,50)

        #add sprites to sprite list
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
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clickPos = pygame.mouse.get_pos()
                            

            
            p.move() #checks for key prsses, and moves charachter

           #Network handler

            try:
                #Get player data 
                playerData = p.getPos()

                #if player clicked, add click pos to data
                if clickPos != None:
                    playerData["clickPos"] = clickPos

                #pass player data to network to be sent
                self.n.updateData(playerData)

                #Update enemy data
                enemyData = self.n.getEnemyData()
                if enemyData != None:   
                    e.dataUpdate(enemyData)
                    if "clickPos" in enemyData: #check if enemy has dine damage to you
                        p.checkClick(enemyData["clickPos"],(enemyData["x"],enemyData["y"]))


            except Exception as exc:
                log(exc)

            #Update health bar
            healthbarP.updateHealth(p.getHP())
            healthbarE.updateHealth(e.getHP())

            #Draw health bar
            healthbarP.draw(self.win)
            healthbarE.draw(self.win)

            #Render battle
            self.renderBattle(self.win,all_sprites) #Render battle


        
    def exit(self):
        pygame.quit()
        sys.exit()
        return True


g = Game()
g.loginScreen()