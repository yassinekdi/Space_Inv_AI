import pygame
from Game.data import *
from Game.Objects import *
from Game.functions import *

# Mainloop ----------------------------------
Me = player((WIN_WIDTH-player_width)/2,WIN_HEIGHT-player_height, player_img)
Me.health = PLAYER_HEALTH

Enemies = []

for _ in range(NB_ENEMIES) :
	new_enemy = enemy(randint(WIN_WIDTH),-enemy_height,enemy_img)
	new_enemy.vely = 15
	Enemies.append(new_enemy)

# Environment RENDER ------------------------------------------------
while run:
	laser_on = False
	keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.KEYUP:	
			if keys[pygame.K_SPACE]:
				laser_on=True

	while len(Enemies)< NB_ENEMIES:
		new_enemy = enemy(randint(WIN_WIDTH),-enemy_height,enemy_img)
		new_enemy.vely = 15
		Enemies.append(new_enemy)


	redrawGameWindow(win,laser_on,Me, Enemies)

with open('SCORE.txt','a') as file:
	file.write('EPISODE: '+ str(EPISODE) + '\n')
	file.write(str(SCORE) + '\n')

pygame.quit()