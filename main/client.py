import pygame
from client_network import Network

width = 500
height = 500

win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Client")

clientnumber = 0

class Fight():
    def __init__(self,p1,p2):
        pass
        
        
        

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
    p = Player(50,50,100,100,(0,255,0))

    elapsedTime = 0 #variable for counting ticks since init
    clock = pygame.time.Clock() #keep track of ticks
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        dt = clock.tick() #the following method returns the time since its last call in milliseconds
        elapsedTime += dt

        p.move() #checks for key prsses, and moves charachter

        n.sendPos(p.getPos())
        
        redrawWindow(win,p)

main()