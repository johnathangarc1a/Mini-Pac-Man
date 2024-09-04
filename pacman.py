#PacMan

# import libraries 
import pygame                  
import math
import sys
from board import boards
import copy


# load images 
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/player_images/{i}.png'), (45, 45)))

ghost_names = ['blinky', 'inky', 'pinky', 'clyde']

#initialize each ghost
blinky_img = pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/ghost_images/red.png'), (45, 45))
blinky_x = 56 
blinky_y = 58 
blinky_direction = 0

pinky_img = pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/ghost_images/pink.png'), (45, 45))
pinky_x = 440
pinky_y = 438 
pinky_direction = 2

inky_img = pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/ghost_images/blue.png'), (45, 45))
inky_x = 440
inky_y = 338 
inky_direction = 2

clyde_img = pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/ghost_images/orange.png'), (45, 45))
clyde_x = 440 
clyde_y = 438 
clyde_direction = 2

spooked_img = pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/ghost_images/powerup.png'), (45, 45))

dead_img = pygame.transform.scale(pygame.image.load(f'/Users/johnathangarcia/Documents/Work_w_Dan/PacMan/ghost_images/dead.png'), (45, 45))


# variables used later in program
direction = 0 # right
counter = 0
flicker = False
turns_allowed = [False, False, False, False] # R L U D
direction_command = 0

player_x = 450  # initialize player posiiton & speed
player_y = 663
player_speed = 2

moving = False
startup_counter = 0
lives = 3
game_over = False
game_won = False

# initializations for ghosts
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]  #initialize target for each ghost
blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
blinky_box, pinky_box, clyde_box, inky_box = False, False, False, False
ghost_speeds = [2, 2, 2, 2]


'''ghost class'''
class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22 # got 22 by trial and error
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.in_box = box
        self.dead = dead
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    # function to draw the ghosts on the screen
    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead): # no powerup & alive or eaten and poweruo and alive
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]: # powerup and alive and not eaten
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos)) # else dead
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))     # using 18 as a fair hitbox, can make it smaller to force ghosts to be closer to you for contact to register
        
        return ghost_rect
    
    # function to check collision between ghosts and borders
    def check_collisions(self):
        num1 = (HEIGHT - 50) // 32 # height of each row 
        num2 = WIDTH//30 # width of each column
        num3 = 15 # buffer
        self.turns = [False, False, False, False] # make all turns false
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y-num3)//num1][self.center_x//num2] == 9: # if wall is above ghost and it is ghost door, let ghost move up
                self.turns[2] = True
            if level[self.center_y//num1][(self.center_x - num3)//num2] < 3 or (level[self.center_y//num1][(self.center_x - num3)//num2] == 9 and (self.in_box or self.dead)): # use some math to find index in level aka board grid
                self.turns[1] = True
            if level[self.center_y//num1][(self.center_x + num3)//num2] < 3 or (level[self.center_y//num1][(self.center_x + num3)//num2] == 9 and (self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3)//num1][self.center_x//num2] < 3 or (level[(self.center_y + num3)//num1][self.center_x//num2] == 9 and (self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3)//num1][self.center_x//num2] < 3 or (level[(self.center_y - num3)//num1][self.center_x//num2] == 9 and (self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3: # if already going right/left
                if 12 <= self.center_x % num2 <= 18: # if in middle of box 
                    if level[(self.center_y + num3)//num1][self.center_x//num2] < 3 or (level[(self.center_y + num3)//num1][self.center_x//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True # if no wall or ghost gate below, go up
                    if level[(self.center_y - num3)//num1][self.center_x//num2] < 3 or (level[(self.center_y - num3)//num1][self.center_x//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True # same but for down
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y//num1][(self.center_x + num2)//num2] < 3 or (level[(self.center_y)//num1][(self.center_x + num2)//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True # same for right
                    if level[self.center_y//num1][(self.center_x - num2)//num2] < 3 or (level[self.center_y//num1][(self.center_x - num2)//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True # same for left

            if self.direction == 0 or self.direction == 1: 
                if 12 <= self.center_x % num2 <= 18: 
                    if level[(self.center_y + num3)//num1][self.center_x//num2] < 3 or (level[(self.center_y + num3)//num1][self.center_x//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3)//num1][self.center_x//num2] < 3 or (level[(self.center_y - num3)//num1][self.center_x//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y//num1][(self.center_x + num3)//num2] < 3 or (level[(self.center_y)//num1][(self.center_x + num3)//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True
                    if level[self.center_y//num1][(self.center_x - num3)//num2] < 3 or (level[self.center_y//num1][(self.center_x - num3)//num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
        else: 
            self.turns[0] = True
            self.turns[1] = True

        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else: 
            self.in_box = False


        return self.turns, self.in_box
    
    # function to move clyde
    def move_clyde(self):
        # R L U D
        # clyde is turning when makes sense for pursuit 
        if self.direction == 0:                                 # if going right and target is farther right and clyde can keep going right, then go right
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:   # target below me and can go down
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: # target above and can go up
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: # target to left and can turn left
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         # if can't go right and can down, go down
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         # if cant go right/down, go up
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:         # if cant go right/down/up, go left
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]: # if we can go right but target is not over there, go up or down to get closer to target
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:                           # if we can't go up/down, go right (no reason to go left bc j came from there)
                    self.x_pos += self.speed
        elif self.direction == 1:                                 
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
                self.y_pos += self.speed
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]: 
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: 
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:                           
                    self.x_pos -= self.speed
        elif self.direction == 2:                                 
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]: 
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed                
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: 
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                else:                           
                    self.y_pos -= self.speed
        elif self.direction == 3:  
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed   
            elif not self.turns[3]:                            
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: 
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                else:                           
                    self.y_pos += self.speed
        
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    # function to move blinky
    def move_blinky(self):
        # R L U D
        # blinky is turning when hits walls, else go straight
        if self.direction == 0:                                 
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]: 
                self.x_pos += self.speed
        elif self.direction == 1:                                 
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]: 
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: 
                self.x_pos -= self.speed
        elif self.direction == 2:                                 
            if self.target[1] < self.y_pos and self.turns[2]:
                # self.direction = 2 // doesn't have to be here bc direction is already 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]: 
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed                
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]: # if i can go up, keep going up
                self.y_pos -= self.speed
        elif self.direction == 3:  
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed   
            elif not self.turns[3]:                            
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]: 
                self.y_pos += self.speed
        
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # R L U D
        # inky turns up or down when can to pursue, but left/right only on collisions (with walls up/down)
        if self.direction == 0:                                 
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]: 
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:                           # if we can't go up/down, go right (no reason to go left bc j came from there)
                    self.x_pos += self.speed
        elif self.direction == 1:                                 
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
                self.y_pos += self.speed
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]: 
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: 
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:                           
                    self.x_pos -= self.speed
        elif self.direction == 2:                                 
            if self.target[1] < self.y_pos and self.turns[2]:
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]: 
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed                
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: 
                self.y_pos -= self.speed
        elif self.direction == 3:  
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed   
            elif not self.turns[3]:                            
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: 
                self.y_pos += self.speed
        
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # R L U D
        # pinky turns left/right when can to pursuit, but up/down on collision (with wall on left/right) 
        if self.direction == 0:                                 
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]: 
                self.x_pos += self.speed
        elif self.direction == 1:                                 
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
                self.y_pos += self.speed
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:   
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]: 
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]: 
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed 
                elif self.turns[2]:         
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: 
                self.x_pos -= self.speed
        elif self.direction == 2:                                 
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]: 
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:         
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:         
                    self.direction = 3
                    self.y_pos += self.speed                
                elif self.turns[0]:         
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: 
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                else:                           
                    self.y_pos -= self.speed
        elif self.direction == 3:  
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed   
            elif not self.turns[3]:                            
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: 
                if self.target[0] > self.x_pos and self.turns[0]:   
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]: 
                    self.direction = 1
                    self.x_pos -= self.speed
                else:                           
                    self.y_pos += self.speed
        
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

''' functions '''
# context: in pacman theres 32 vertical items and 30 horizontal
# function to draw board using board.py
def draw_board():
    num1 = ((HEIGHT - 50) // 32)   # want a 50 pixel buffer and /32 bc 32 vertical items 
    num2 = (WIDTH // 30)           # use floor division to keep integers

    for i in range(len(level)):                     #iterate through every row & every item in each row
        for j in range(len(level[i])):
            match level[i][j]:
                case 1:
                    pygame.draw.circle(screen, 'white', (j * num2 + (.5*num2), i*num1 + (.5*num1)), 4)      # j*num2 = position equidistance away....+.5*num2 centers it
                case 2:
                    if not flicker:
                        pygame.draw.circle(screen, 'white', (j * num2 + (.5*num2), i*num1 + (.5*num1)), 10)
                    else:
                        continue
                case 3:
                    pygame.draw.line(screen, wall_color, (j*num2 + (.5*num2), i*num1),      # keeps x the same & draws vertical line
                                     (j*num2 + (.5*num2), i*num1 + num1), 3)
                case 4:
                    pygame.draw.line(screen, wall_color, (j*num2, i*num1 + (.5*num1)),      # keeps y the same & draws horizontal line
                                     (j*num2 + num2, i*num1 + (.5*num1)), 3)
                case 5: 
                    pygame.draw.arc(screen, wall_color, [(j*num2 - (.4*num2) - 2), (i*num1 + (.5*num1)), num2, num1], 0, PI/2, 3)   # .4 & -2 just make it look better on screen
                case 6: 
                    pygame.draw.arc(screen, wall_color, [(j*num2 + (.5*num2)), (i*num1 + (.5*num1)), num2, num1],PI/2, PI, 3)
                case 7:
                    pygame.draw.arc(screen, wall_color, [(j*num2 + (.5*num2)), (i*num1 - (.4*num1)), num2, num1], PI, 3*PI/2, 3)
                case 8:
                    pygame.draw.arc(screen, wall_color, [(j*num2 - (.4*num2) - 2), (i*num1 - (.4*num1)), num2, num1], 3*PI/2, 2*PI, 3)
                case 9: 
                    pygame.draw.line(screen, 'white', (j*num2, i*num1 + (.5*num1)),
                                     (j*num2 + num2, i*num1 + (.5*num1)), 3)
                case _:
                    continue

# draw misc objects: score, lives, game lost/won pop up
def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    for i in range(lives):      # draws lives at bottom of screen
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        game_over_text = font.render('Game Over! Space Bar to Restart!', True, 'red')
        screen.blit(game_over_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        game_over_text = font.render('Victory! Space Bar to Restart!', True, 'green')
        screen.blit(game_over_text, (100, 300))
    

def draw_player():      # 0-right 1-left 2-up 3-down
    match direction:
        case 0:
            screen.blit(player_images[counter//5], (player_x, player_y))
        case 1:
            screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
        case 2:
            screen.blit(pygame.transform.rotate(player_images[counter//5], 90), (player_x, player_y))
        case 3:
            screen.blit(pygame.transform.rotate(player_images[counter//5], 270), (player_x, player_y))
        
# function to update players position
def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT-50)//32 # height of each row
    num2 = (WIDTH//30) # width of each column
    num3 = 15 # buffer
    # check collisions based on centerx and centery of player +- an offset
    if centerx//30 < 29: # checking ur in a square
        if direction == 0:
            if level[centery//num1][(centerx - num3) // num2] < 3:      # use centery and centerx to locate row and column from board.py ... checks if you can turn back how you came from
                turns[1] = True
        if direction == 1:
            if level[centery//num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3)//num1][(centerx) // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3)//num1][(centerx) // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3: 
            if 12 <= centerx % num2 <= 18:                  #each tile abt 30p wide, 12<=x<=18 is roughly center of tile, turn when in middle of tile so turning looks smoother
                if level[(centery + num3) // num1][centerx//num2] < 3: # if below u is a dot or ghost door, can go down
                    turns[3] = True
                if level[(centery - num3) // num1][centerx//num2] < 3: # if above is dot or ghost door, can go up
                    turns[2] = True
            if 12 <= centery % num1 <= 18:                  # at midpoint of square , checking if can turn left/right at this height
                if level[(centery) // num1][(centerx - num2) //num2] < 3:   # checking behind us by a full square, if clear we can go left
                    turns[1] = True
                if level[(centery) // num1][(centerx + num2) //num2] < 3:   # checking in front of us, if clear we can go right
                    turns[0] = True

        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:                  #each tile abt 30p wide, 12<=x<=18 is roughly center of tile so turning looks smoother
                if level[(centery + num1) // num1][centerx//num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx//num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:                  
                if level[(centery) // num1][(centerx - num3) //num2] < 3:   # using num3 here (smaller #) bc want to be able to go left/right longer to make game look cleaner
                    turns[1] = True
                if level[(centery) // num1][(centerx + num3) //num2] < 3:   
                    turns[0] = True



    else:
        turns[0], turns[1] = True, True
    return turns

# function to move player 
def move_player(play_x, play_y):
    # R, L, U, D
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    elif direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    
    return play_x, play_y

# function to update ghost target... ie player, box, run away
def get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y):
    if player_x < 450:      # how to get away from player if powerup is active
        runaway_x = 900
    else:
        runaway_x = 0
    
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)  # box

    if powerup:                         # if powerup active, and a ghost is not dead or eaten, run away, else if not dead but eaten, if in box then go to door, once out of box target player
        if not blinky.dead and not eaten_ghost[0]:
            blinky_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 340 < blinky_x < 560 and 340 < blinky_y < 500:
                blinky_target = (400, 100)
            else: 
                blinky_target = (player_x, player_y)
        else:
            blinky_target = return_target

        if not inky.dead:
            inky_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 340 < inky_x < 560 and 340 < inky_y < 500:
                inky_target = (400, 100)
            else: 
                inky_target = (player_x, player_y)
        else:
            inky_target = return_target

        if not pinky.dead:
            pinky_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 340 < pinky_x < 560 and 340 < pinky_y < 500:
                pinky_target = (400, 100)
            else: 
                pinky_target = (player_x, player_y)    
        else:
            pinky_target = return_target

        if not clyde.dead:
            clyde_target = (450, 450)
        elif not clyde.dead and eaten_ghost[3]:
            if 340 < clyde_x < 560 and 340 < clyde_y < 500:
                clyde_target = (400, 100)
            else: 
                clyde_target = (player_x, player_y)
        else:
            clyde_target = return_target
    
    else:                           # can optimize this by working into class
        if not blinky.dead:
            if 340 < blinky_x < 560 and 340 < blinky_y < 500:
                blinky_target = (400, 100)
            else: 
                blinky_target = (player_x, player_y)
        else:
            blinky_target = return_target

        if not inky.dead:
            if 340 < inky_x < 560 and 340 < inky_y < 500:
                inky_target = (400, 100)
            else: 
                inky_target = (player_x, player_y)
        else:
            inky_target = return_target

        if not pinky.dead:
            if 340 < pinky_x < 560 and 340 < pinky_y < 500:
                pinky_target = (400, 100)
            else: 
                pinky_target = (player_x, player_y)
        else:
            pinky_target = return_target

        if not clyde.dead:
            if 340 < clyde_x < 560 and 340 < clyde_y < 500:
                clyde_target = (400, 100)
            else: 
                clyde_target = (player_x, player_y)
        else:
            clyde_target = return_target
            
    return [blinky_target, inky_target, pinky_target, clyde_target]

score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]

# function to eat white dots
def check_collisions(score, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH//30)
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:       # by using center_x and center_y, looks more realistic when eating compared to when just entering square
            level[center_y//num1][center_x//num2] = 0
            score += 10
        if level[center_y // num1][center_x // num2] == 2:       
            level[center_y//num1][center_x//num2] = 0
            score += 50
            power = True
            power_count = 0 #resets counter for every new powerup
            eaten_ghosts = [False, False, False, False] # keeps track of ghosts we've eaten with powerup
    return score, power, power_count, eaten_ghosts

# initialize game
pygame.init()     

# game board set up 
WIDTH = 900 
HEIGHT = 950
PI = math.pi
screen = pygame.display.set_mode((WIDTH, HEIGHT))
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)  # by using list can add levels later if you wanted to , use deepcopy so original board stays unedited
wall_color = 'blue'

run = True
while run:
    timer.tick(fps)

    if counter<19:      # controls animation of pacman
        counter +=1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True

    if powerup and power_counter < 600:     # < 600 = 10 seconds on 60 fps , keep powerup active for 10 seconds
        power_counter += 1
    elif powerup and power_counter >= 600:  # once reach 10 sec, take away powerup & reset eaten ghosts
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]

    if startup_counter < 180 and not game_over and not game_won:   # countdown of 3 seconds before game starts
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board()    # draws board
    center_x = player_x + 23    # gets the center of pacman to pass into check_position and hit box ( got by testing it out on screen )
    center_y = player_y + 24

    if powerup:
        ghost_speeds = [1, 1, 1, 1] # makes ghost slower when powerup activated
    else:
        ghost_speeds = [2, 2, 2, 2] # regular speed

    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2

    # if ghost dead, go back to box faster 
    if blinky_dead:            
        ghost_speeds[0] = 4
    if inky_dead:
        ghost_speeds[1] = 4
    if pinky_dead:
        ghost_speeds[2] = 4
    if clyde_dead:
        ghost_speeds[3] = 4
    
    # turns game_won false if theres any dots left on screen
    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False
    

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)   # hitbox for player
    draw_player()   # draws pacman after we make hitbox so you can't see outline
    draw_misc()

    # initialize each ghost & set targets
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead, inky_box, 1)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)

    turns_allowed = check_position(center_x, center_y) # returns what turns pacman is able to make 

    if moving:  # after 3 second countdown, moving set to True and player can start moving
        player_x, player_y = move_player(player_x, player_y) # moves player based on key pressed
        # initialize ghost movement
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        
        if not inky_dead and not inky.in_box:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            inky_x, inky_y, inky_direction = inky.move_clyde()
        
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()

        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()

    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost) # handles eating dots and adding score 

 # can optimize this by using a for loop
 # if no powerup and ghost hits player, reset game and take off a life
    if not powerup:
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
        (player_circle.colliderect(inky.rect) and not inky.dead) or \
        (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
        (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                blinky_x = 56 
                blinky_y = 58 
                blinky_direction = 0
                inky_x = 440
                inky_y = 338 
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438 
                pinky_direction = 2
                clyde_x = 440 
                clyde_y = 438 
                clyde_direction = 2
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
                eaten_ghost = [False, False, False, False]
            else:
                game_over = True
                moving = False
                startup_counter = 0
    
    # checking collisons between hitbox and ghosts when powerup active
    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
        if lives > 0:
            lives -= 1
            startup_counter = 0
            powerup = False
            powerup_counter = 0
            blinky_x = 56 
            blinky_y = 58 
            blinky_direction = 0
            inky_x = 440
            inky_y = 338 
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438 
            pinky_direction = 2
            clyde_x = 440 
            clyde_y = 438 
            clyde_direction = 2
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
            eaten_ghost = [False, False, False, False]
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead:
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_counter = 0
                blinky_x = 56 
                blinky_y = 58 
                blinky_direction = 0
                inky_x = 440
                inky_y = 338 
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438 
                pinky_direction = 2
                clyde_x = 440 
                clyde_y = 438 
                clyde_direction = 2
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
                eaten_ghost = [False, False, False, False]
            else:
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead:
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_counter = 0
                blinky_x = 56 
                blinky_y = 58 
                blinky_direction = 0
                inky_x = 440
                inky_y = 338 
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438 
                pinky_direction = 2
                clyde_x = 440 
                clyde_y = 438 
                clyde_direction = 2
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
                eaten_ghost = [False, False, False, False]
            else:
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead:
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_counter = 0
                blinky_x = 56 
                blinky_y = 58 
                blinky_direction = 0
                inky_x = 440
                inky_y = 338 
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438 
                pinky_direction = 2
                clyde_x = 440 
                clyde_y = 438 
                clyde_direction = 2
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
                eaten_ghost = [False, False, False, False]
            else:
                game_over = True
                moving = False
                startup_counter = 0

    # handles score and attributes after eating ghost during powerup
    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2**eaten_ghost.count(True)) * 100         # 200 points per ghost eaten
    if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        score += (2**eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        score += (2**eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        score += (2**eaten_ghost.count(True)) * 100
        


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            elif event.key == pygame.K_LEFT:
                direction_command = 1
            elif event.key == pygame.K_UP:
                direction_command = 2
            elif event.key == pygame.K_DOWN:
                direction_command = 3
            elif event.key == pygame.K_SPACE and (game_over or game_won):   # allows pressing of spacebar to reset gamea after won/lost
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_counter = 0
                blinky_x = 56 
                blinky_y = 58 
                blinky_direction = 0
                inky_x = 440
                inky_y = 338 
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438 
                pinky_direction = 2
                clyde_x = 440 
                clyde_y = 438 
                clyde_direction = 2
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_dead, pinky_dead, clyde_dead, inky_dead = False, False, False, False
                eaten_ghost = [False, False, False, False]
                score = 0
                lives = 3
                level = boards
                game_over = False
                game_won = False
                level = copy.deepcopy(boards)

        '''if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:  # and blah blah allows for user error when accidentally pressing key they didnt mean to
                direction_command = direction
            elif event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            elif event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            elif event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction'''
        # same code above and below
        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_RIGHT and direction_command == 0) or (event.key == pygame.K_LEFT and direction_command == 1) or (event.key == pygame.K_UP and direction_command == 2) or (event.key == pygame.K_DOWN and direction_command == 3):
                direction_command = direction

    for i in range(4):      # updates direction if allowed
        if direction_command == i and turns_allowed[i]:
            direction = i

        if player_x > 900:  # handles pacman going from right to left off screen & vice versa 
            player_x = -47
        elif player_x < -50:
            player_x = 897

    # if eyeballs (ghost after you eat them during powerup) get back to box, we want them to be alive again
    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False

    pygame.display.flip()

pygame.quit()





