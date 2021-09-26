import pygame
from client_network import Network

width = 500
height = 500

win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Client")

clientnumber = 0
  
        

class Player():
    def __init__(self,x,y,width,height,color):
        self.x = x
        self.y = y 
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel = .5

    def draw(self,win):
        pygame.draw.rect(win,self.color,self.rect)
    
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
            self.x == data["x"]
            self.y == data["y"]
        
        self.rect = (self.x,self.y,self.width,self.height)

    def getPos(self):
        return {"x":self.x,"y":self.y}


    
     


def redrawWindow(win,player):
    win.fill((255,255,255))
    player.draw(win)
    pygame.display.update()


def main():
    run = True
    n = Network()

    #startPos = n.getPos()
    p = Player(50,50,100,100,(0,255,0)) #player should be init fron network?

    #elapsedTime = 0 #variable for counting ticks since init
    #clock = pygame.time.Clock() #keep track of ticks
    p2Connected = False
    enemyUsername = None
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        #dt = clock.tick() #the following method returns the time since its last call in milliseconds
        #lapsedTime += dt

        p.move() #checks for key prsses, and moves charachter

        n.sendPos(p.getPos())
        
        
        if n.checkEnemyConnected() != False and p2Connected == False:
            enemyUsername = n.checkEnemyConnected()
            p2 = Player(50,50,100,100,(0,0,255))
            p2Connected = True
        
        if p2Connected == True:
            p2.move(n.getEnemyPos())
            redrawWindow(win,p2)
        
        redrawWindow(win,p)

main()