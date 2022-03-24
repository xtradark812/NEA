import pygame
import os
class Button:
    def __init__(self, text, midx, midy, color,width,height):
        self.text = text

        self.color = color
        self.width = width
        self.height = height

        self.x = midx-(self.width/2)
        self.y = midy-(self.height/2)

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

    def changeText(self,text):
        self.text = text

class OnlineList():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.buttons = []

    def updateUsers(self,users):
        self.buttons = []
        listSpace = 15
        for user in users:
            self.buttons.append(Button(user,self.x,self.y+listSpace,(0,0,0),100,30))
            listSpace+= 45

    def click(self,pos):
        for button in self.buttons:
            if button.click(pos):
                return button.text
        return None
            

    def draw(self,win):
        for button in self.buttons:
            button.draw(win)



class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
        self.rect = pygame.Rect(x-(w/2), y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.font = font = pygame.font.Font('freesansbold.ttf',30)
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

class Textures:
    def __init__(self,width,height): #TODO recive acsess in this method and load proper textures
        self.loginBackground = pygame.image.load(os.path.join("textures", "background.png"))
        self.loginBackground = pygame.transform.scale(self.loginBackground,(width, height))

    def getLoginBackground(self):
        return self.loginBackground

    def loadTextures(self,acsess):
        textures = ["standing","enemyStanding","background","crouching","enemyCrouching","walking","enemyWalking","jumping","enemyJumping"]
        loadedTextures = {}
        
        for texture in textures:
            try:
                loadedTextures[texture] = pygame.image.load(os.path.join("textures", acsess[texture]+".png"))
            except KeyError:
                print("texture not found: ",texture)

        return loadedTextures
