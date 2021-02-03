#Goal: Create a ladder like game where you create bouncing platforms under
#a bouncing player ball by connecting points using the mouse.

'''
Close off sides from placing point, make it close in more and more as score increases but never more than 25% on either side
Gravity increases by .1 per 5-10 points of score
Flashing red boxes begin to appear that eventually will become solid red and kill the player, they can last a long time based on score
Maximum line length decreases
'''

import pygame, json, sys, math, random

pygame.mixer.pre_init()
pygame.init()

#Window settings
Title = "Ladder Lines"
WIDTH = 400
HEIGHT = 800
FPS = 60
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption(Title)
clock = pygame.time.Clock()
#Settings

START = 0
PLAYING = 1
DEAD = 2
STAGE = START
FONT = pygame.font.Font("minya_nouvelle_bd.ttf",36)
running = True
#Colors
DARK_BLUE = (16, 86, 103)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
RED = (255,40,40, 100)
BLACK = (0,0,0)
OFFGREEN = (40,230,100, 100)

#Setup
startLine = (100,760)
endLine = (300, 760)
previousEnd = (300,760)

player = pygame.Rect(200, 400, 10, 10)
playerVX = 0
playerVY = 0
velocity = [playerVX, playerVY]

lines = [[startLine, endLine]]
lineWidth = 4

particles = []

shakeoffset = [0,0]

filename = "hs.txt"    

bounceCD = 0
score = 0
screenshake = 0

class Vector():
    def __init__(self, startPos, endPos):
        self.startPos = startPos
        self.endPos = endPos
        self.width = lineWidth
        self.tempPos = (0,0)
        self.switched = False
        if startPos[0] > endPos[0]:  #Left-most point is always start point
            self.tempPos = self.endPos
            self.endPos = self.startPos
            self.startPos = self.tempPos
            self.switched = True

        #Saving coordinates as more accessible variables
        self.startX = self.startPos[0]
        self.startY = self.startPos[1]
        self.endX = self.endPos[0]
        self.endY = self.endPos[1]

        #Getting slope
        self.rise = self.endY - self.startY
        self.run = self.endX - self.startX
        if self.run != 0:
            self.slope = (self.rise/self.run)
        else:
            self.slope = 0

        self.points = []
        for x in range(self.run):
            y = (int) (self.slope * x + self.startY)
            x += self.startX
            self.points.append((x,y))  #Points now contains all collision points of the vector
        
        self.pointGiven = False
        
    def getPoints(self):
        return self.points

    def givePoint(self):
        if self.pointGiven == False:
            self.pointGiven = True
            return 1
        return 0

    def getBounce(self, velocity):
        vx = velocity[0]
        vy = velocity[1]

        slope = self.slope
        vStr = vx + vy
        x, y = 0, 0

        vy /= 2
        tempVX = vx
        if self.slope == 0:
            vy = -vy - 4
        else:   
            vx += (int)(self.slope * 5) + 1
            vy = -vy
            vy -= 2
        return [vx,vy]

class Particle():
    def __init__(self, x, y, vx, vy):
        self.x = x + random.randint(-5,5)
        self.y = y + random.randint(-5,5)

        self.vx = random.randint(-4,4) 
        self.vy = random.randint(-3,1)
        
        self.strength = random.randint(2,5)
        self.life = self.strength * 3
        
        self.rect = pygame.Rect(x,y,self.strength,self.strength)
        
    def getRect(self, offset):
        self.rect = pygame.Rect(self.rect.x+offset[0], self.rect.y+offset[1], self.strength, self.strength)
        return self.rect

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        
    def isDead(self):
        return self.life <= 0
        

def display_message(surface, text, x, y, color):
    text = FONT.render(text, 1, color)
    surface.blit(text, (x,y))
    
def getHighScore(filename):
    try:
        file = open(filename, 'r')
        hs = (int)(file.readline())
        file.close()
        return hs
    except:
        file = open(filename, 'w')
        file.write("0")
        file.close()
        return 0
    
def saveHighScore(filename, score):
    try:
        file = open(filename, 'w')
        file.write(str(score))
        file.close()
        return 1
    except:
        return 0

highscore = getHighScore(filename)
vectors = [Vector(startLine, endLine)]
while running:
    #Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and STAGE == PLAYING:
            if event.button == 1:
                lines.append([previousEnd, nextPoint])
                vectors.append(Vector(previousEnd, nextPoint))
                previousEnd = nextPoint
        elif event.type == pygame.KEYDOWN and STAGE == START:
            STAGE = PLAYING
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and STAGE == DEAD:
                startLine = (100,760)
                endLine = (300, 760)
                previousEnd = (300,760)

                player = pygame.Rect(200, 400, 10, 10)
                playerVX = 0
                playerVY = 0
                velocity = [playerVX, playerVY]

                lines = [[startLine, endLine]]

                vectors = [Vector(startLine, endLine)]

                STAGE = START
                

                if score > highscore:
                    saveHighScore(filename, score)
                    highscore = score

                score = 0

    #Keep max lines/vectors on screen to 3
    if (len(vectors) > 3):
        del vectors[0]
        del lines[0]

    #Mouse
    mx,my = pygame.mouse.get_pos()
    nextPoint = (mx,my)

    #Particle handling
    p = 0
    particlesLength = len(particles)
    while p < particlesLength:
        particles[p].update()
        if particles[p].isDead():
            del particles[p]
            p -= 1
            particlesLength -= 1
        p += 1
    
    #Player Movement
    gravity = 0.1
    if STAGE == PLAYING:
        playerVY += gravity 
        velocity = [playerVX, playerVY]
        player.x += velocity[0]
        player.y += velocity[1]

    #Vector Collisions
    if bounceCD > 0:
        bounceCD -= 1
    for v in vectors:
        points = v.getPoints()
        for p in points:
            if playerVY > 0 and bounceCD == 0 and player.collidepoint(p):
                bounceCD = 6
                tempVelocity = v.getBounce(velocity)
                playerVX = tempVelocity[0]
                playerVY = tempVelocity[1]
                score += v.givePoint()
                for i in range(random.randint(8,12)):
                    particles.append(Particle(player.x, player.y, playerVX, playerVY))
                screenshake += 25
    #Screen collisions and player max velocities
    if player.right >= WIDTH or player.left <= 0:
        playerVX = -playerVX
    if playerVX > 10:
        playerVX = 10
    if playerVX < -10:
        playerVX = -10
    if playerVY > 10:
        playerVY = 10
    if playerVY < -10:
        playerVY = -10

    if player.y > HEIGHT:
        STAGE =DEAD
        
    #Screenshake
    shakeOffset = [0,0]
    if screenshake > 0:
        screenshake -= 1
        shakeOffset = [random.randint(-4,4), random.randint(-4,4)]
        
    #Draw game stuff
    screen.fill(DARK_BLUE)
        
    for p in particles:
        pygame.draw.rect(screen, OFFGREEN, p.getRect(shakeOffset))
    
    for L in lines:
        lineX1 = L[0][0] + shakeOffset[0]
        lineY1 = L[0][1] + shakeOffset[1]
        lineX2 = L[1][0] + shakeOffset[0]
        lineY2 = L[1][1] + shakeOffset[1]
        pygame.draw.line(screen, BLACK, (lineX1, lineY1), (lineX2, lineY2), 4)
    
    pygame.draw.rect(screen, GREEN, (player.x+shakeOffset[0], player.y+shakeOffset[1], player.width, player.height))

    #Message displays
    if STAGE == DEAD:
        display_message(screen, "GAME OVER!", 95, 299, WHITE)
        display_message(screen, "Press R to restart.", 70, 399, WHITE)
    if STAGE == START:
        display_message(screen, "Press any key to start.", 30, 399, WHITE)
        display_message(screen, "High Score: " + str(highscore), 100, 100, WHITE)
    if STAGE == PLAYING:
        display_message(screen, "Score = " + str(score), 15+shakeOffset[0],15+shakeOffset[1], WHITE)
        pygame.draw.line(screen, WHITE, (mx,my), previousEnd)
    
    pygame.display.flip()
    
    clock.tick(FPS)

pygame.quit()
