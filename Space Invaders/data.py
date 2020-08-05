import pygame
import csv
import numpy as np

# Initializations -----------------------
# DIMENSIONS
WIN_WIDTH, WIN_HEIGHT = 700,500
MENU_WIDTH = 150 

# COLORS
WHITE = (255,255,255)
GREEN = (154, 186, 182)
YELLOW = (255, 250, 149)

# PLAYERS
NB_ENEMIES= 10
ENEMY_HEALTH = 3
PLAYER_HEALTH = 5

# DISPLAY
FRAME_RATE=100
run = True
DT = 1/FRAME_RATE

# STATS
HIGHEST_SCORE = 0
EPISODE = 1
with open('SCORE.txt','r') as file:
	 reader = list(csv.reader(file))
	 if len(reader) >=2:
	 	ind = np.arange(1,len(reader),step=2)
	 	EPISODE = int(reader[-2][0][-1])+1	 	
	 	scores = [int(reader[i][0]) for i in ind]
	 	HIGHEST_SCORE = max(scores)

SCORE = 0


pygame.init()
win = pygame.display.set_mode((WIN_WIDTH+MENU_WIDTH,WIN_HEIGHT))
pygame.display.set_caption('Spaceship Invaders')
font = pygame.font.SysFont('cambria', 25,italic=True)
font2 = pygame.font.SysFont('cambria', 25,bold=True)
font3 = pygame.font.SysFont('cambria', 50,bold=True,italic=True)

# imgs
player_img = pygame.image.load('Imgs/spaceship.png')
laser_player_img = pygame.image.load('Imgs/laser_player.png')
enemy_img = pygame.image.load('Imgs/enemy.png')
laser_enemy_img = pygame.image.load('Imgs/laser_enemy.png')

# sizes
player_width,player_height = player_img.get_rect().size
enemy_width,enemy_height = enemy_img.get_rect().size
laser_width,laser_height = laser_player_img.get_rect().size

#  Background
BG = pygame.image.load('Imgs/space.jpg')
