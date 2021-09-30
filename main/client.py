import pygame
from client_network import Network
import sys

width = 500
height = 500

win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Client")

clientnumber = 0
  
        

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
            self.rect.x == data["x"]
            self.rect.y == data["y"]
        
        self.rect.center = (self.x, self.y)

    def getPos(self):
        return {"x":self.x,"y":self.y}


    
     


def redrawWindow(win,all_sprites):
    all_sprites.update() #update sprites
    pygame.display.update()
    win.fill((255,255,255))
    all_sprites.draw(win) #DRAW SPRITES
    


def main():

    run = True
    n = Network()

    # #startPos = n.getPos()
    # p = Player(50,50,100,100,(0,255,0)) #player should be init fron network?

    elapsedTime = 0 #variable for counting ticks since init
    clock = pygame.time.Clock() #keep track of ticks
    p2Connected = False
    enemyUsername = None

    all_sprites = pygame.sprite.Group()
    p = Player(50,50,0,255,0)
    all_sprites.add(p)

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
                break

        

        

        n.sendPos(p.getPos())
        dt = clock.tick() #the following method returns the time since its last call in milliseconds
        elapsedTime += dt
        
        
        p.move() #checks for key prsses, and moves charachter
        redrawWindow(win,all_sprites) #RENDER
       
        
        
        
        

        if n.checkEnemyConnected() != False and p2Connected == False:
            enemyUsername = n.checkEnemyConnected()
            p2 = Player(50,50,100,100,(0,0,255))
            p2Connected = True
        
        if p2Connected == True:
           p2.move(n.getEnemyPos())
        
        # redrawWindow(win,p)

main()