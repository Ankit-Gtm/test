import pygame
from pygame.locals import*
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60

screenWidth = 1000
screenHeight = 600

screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('GC')

font = pygame.font.SysFont('Comic Sans', 70)
font_score = pygame.font.SysFont('Comic Sans', 30)

tilesizey = 30
tilesizex = 50
gameOver = 0
mainMenu = True
level = 1
max_levels = 3
score = 0

white = (255,255,255)
black = (0,0,0)

#load images
bgImg = pygame.image.load('Images/bg.jpg')
restart_image = pygame.image.load('Images/restart_btn.png')
start_image = pygame.image.load('Images/start_btn.png')
start_image = pygame.transform.scale(start_image,(135,70))
exit_image = pygame.image.load('Images/exit_btn.png')
exit_image = pygame.transform.scale(exit_image,(135,70))

# def drawgrid():
#     for line in range(0,20):
#         pygame.draw.line(screen,(255,255,255),(0,line*tilesize),(screenWidth,line*tilesize))
#         pygame.draw.line(screen,(255,255,255),(line*tilesize,0),(line*tilesize,screenWidth))

def drawText(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

#level-reset function
def resetLevel(level):
    player.reset(50,screenHeight-130)
    blob_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()

    #load world data
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        screen.blit(self.image,self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x,y)

    def update(self,gameOver):

        dx = 0
        dy = 0

        walk_cooldown = 5

        if gameOver == 0:
            #get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -11
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -=3.5
                self.counter+=1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx +=3.5
                self.counter+=1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.playerimage = self.images_right[self.index]
                if self.direction == -1:
                    self.playerimage = self.images_Left[self.index]

            #handle animation

            if self.counter>walk_cooldown:
                self.counter = 0
                self.index+=1
                if self.index >= len(self.images_right):
                    self.index=0
                if self.direction == 1:
                    self.playerimage = self.images_right[self.index]
                if self.direction == -1:
                    self.playerimage = self.images_Left[self.index]

            #add gravity
            self.vel_y += 1
            if self.vel_y > 8:
                self.vel_y = 8
            dy += self.vel_y

            #check for collision
            self.in_air = True
            for tile in world.tileList:
                #check for x collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if above
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            
            #check for collision with enemies
            if pygame.sprite.spritecollide(self,blob_group,False):
                gameOver = -1
            
            #check for collision with lava
            if pygame.sprite.spritecollide(self,lava_group,False):
                gameOver = -1
            
            #check for collision with door
            if pygame.sprite.spritecollide(self,exit_group,False):
                gameOver = 1

            #change player position
            self.rect.x += dx
            self.rect.y += dy

        elif gameOver == -1:
            self.playerimage = self.deadImage
            if self.rect.y > 100:
                self.rect.y -= 5


        #draw player onto screen
        screen.blit(self.playerimage,self.rect)
        # pygame.draw.rect(screen,(255,255,255),self.rect,2)
        return gameOver

    def reset(self,x,y):
        self.images_right = []
        self.images_Left = []
        self.index = 0
        self.counter = 0
        #load image
        for num in range(1,5):
            playerimage_Right = pygame.image.load(f'Images/guy{num}.png')
            playerimage_Right = pygame.transform.scale(playerimage_Right,(40,60))
            playerimage_Left = pygame.transform.flip(playerimage_Right,True,False)
            self.images_right.append(playerimage_Right)
            self.images_Left.append(playerimage_Left)
        self.deadImage = pygame.image.load('Images/ghost.png')
        self.deadImage = pygame.transform.scale(self.deadImage,(25,25))
        self.playerimage = self.images_right[self.index]
        self.rect = self.playerimage.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.playerimage.get_width()
        self.height = self.playerimage.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

class World():
    def __init__(self,data):
        self.tileList = []
        #load images
        borderTiles = pygame.image.load('Images/Base pack/Tiles/stoneCenter.png')
        leftGrassEnd = pygame.image.load('Images/Base pack/Tiles/grassLeft.png')
        midGrass = pygame.image.load('Images/Base pack/Tiles/grassMid.png')
        rightGrassEnd = pygame.image.load('Images/Base pack/Tiles/grassRight.png')
        singleGrassTile = pygame.image.load('Images/Base pack/Tiles/grass.png')
        dirtTile = pygame.image.load('Images/Base pack/Tiles/grassCenter.png')
        platformImage = pygame.image.load('Images/Base pack/Tiles/grassHalf.png')
        leftCliff = pygame.image.load('Images/Base pack/Tiles/grassCliffLeft.png')
        rightCliff = pygame.image.load('Images/Base pack/Tiles/grassCliffRight.png')
        row_count = 0
        for row in data:
            columnCount = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(borderTiles,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(leftGrassEnd,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(midGrass,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 4:
                    img = pygame.transform.scale(rightGrassEnd,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 5:
                    img = pygame.transform.scale(singleGrassTile,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 6:
                    img = pygame.transform.scale(dirtTile,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 9:
                    img = pygame.transform.scale(platformImage,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 10:
                    img = pygame.transform.scale(leftCliff,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 11:
                    img = pygame.transform.scale(rightCliff,(tilesizex,tilesizey))
                    imgRect = img.get_rect()
                    imgRect.x = columnCount*tilesizex
                    imgRect.y = row_count*tilesizey
                    tile = (img,imgRect)
                    self.tileList.append(tile)
                if tile == 12:
                    lava = Lava(columnCount*tilesizex,row_count*tilesizey)
                    lava_group.add(lava)
                if tile == 13:
                    coin = Coin(columnCount*tilesizex + int(tilesizey//2),row_count*tilesizey+ int(tilesizex//2))
                    coin_group.add(coin)
                if tile == 14:
                    blob = Enemy(columnCount*tilesizex,row_count*tilesizey+5)
                    blob_group.add(blob)
                if tile == 15:
                    exit = Exit(columnCount*tilesizex,row_count*tilesizey - int(tilesizex//2))
                    exit_group.add(exit)
                columnCount +=1
            row_count+=1
    def draw(self):
        for tile in self.tileList:
            screen.blit(tile[0],tile[1])
            pygame.draw.rect(screen,(255,255,255),tile[1],2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Images/blob.png')
        self.image = pygame.transform.scale(self.image,(25,20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 25:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Images/Base pack/Tiles/liquidLavaTop_mid.png')
        self.image = pygame.transform.scale(img,(tilesizex,tilesizey))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Images/coin1.png')
        self.image = pygame.transform.scale(img,(int(tilesizex ),int(tilesizey )))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Images/exit.png')
        self.image = pygame.transform.scale(img,(tilesizex,int(tilesizey * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(50,screenHeight-130)
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

#dummy coin
scoreCoin = Coin(tilesizex//2,tilesizey//2)
coin_group.add(scoreCoin)

#load world data
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

#create buttons
restart_button = Button(screenWidth//2 -60,screenHeight//2 + 50,restart_image)
start_button = Button(screenWidth//2 -175,screenHeight//2,start_image)
exit_button = Button(screenWidth//2 + 75,screenHeight//2,exit_image)



run = True

while run:

    clock.tick(fps)

    screen.blit(bgImg, (0,0))

    if mainMenu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            mainMenu = False
    else:
        world.draw()

        if gameOver == 0:
            blob_group.update()
            #update score
            #check if a coin has been collected
            if pygame.sprite.spritecollide(player,coin_group,True):
                score += 1
            drawText(' x ' + str(score), font_score, white, tilesizex - 5, 3)

        blob_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)

        gameOver = player.update(gameOver)

        #if player has died
        if gameOver == -1:
            drawText('Game Over', font, black, screenWidth//2 -130, screenHeight//2)
            if restart_button.draw():
                world_data = []
                world = resetLevel(level)
                gameOver = 0
                score = 0

        #if the player has completed the level
        if gameOver == 1:
            #reset game and go to next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = resetLevel(level)
                gameOver = 0
            else:
                drawText('You win!!!', font, black, screenWidth//2 -100, screenHeight//2)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = resetLevel(level)
                    gameOver = 0
                    score = 0

        # drawgrid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
