import pygame
from data import *
from Objects import *

def redrawGameWindow(win,laser_on,player,enemies):
	global SCORE

	win.blit(BG,(0,0))
	if player.is_alive:
		player.move()

		probability_shooting = 1/200
		for enemy in enemies:
			if enemy.is_alive:
				enemy.move()
				enemy.shoot(probability_shooting)
				enemy.collision(player.lasers)
				player.collision(enemy)
			else:
				SCORE +=1
				enemies.remove(enemy)
			
		if laser_on:
			player.shoot()	

		player.draw(win)

		for enemy in enemies:
			enemy.draw(win)

		# STATS
		words = ['Health: ','Score: ', 'High score: ']
		words_x = WIN_WIDTH + 10
		words_y = []
		words2 = [str(player.health-player.hit),str(SCORE),str(HIGHEST_SCORE)]
		words2_x = words_x + 10
		words2_y = []

		i=1
		for _ in words:
			y = 65*i
			words_y.append(y)
			words2_y.append(y+25)
			i+=1

		texts = [font.render(txt, 1, WHITE) for txt in words]
		texts2 = [font2.render(txt, 1, GREEN) for txt in words2]
		[win.blit(txt, (words_x, y)) for txt,y in zip(texts,words_y)]
		[win.blit(txt, (words2_x, y)) for txt,y in zip(texts2,words2_y)]

	else:
		text = font3.render('GAME OVER ',1, YELLOW)
		txt_width,txt_height = text.get_rect().size
		win.blit(text, ((WIN_WIDTH+MENU_WIDTH-txt_width)/2, (WIN_HEIGHT-txt_height)/2))	
		del player
		

	pygame.display.update()

# Mainloop ----------------------------------
Me = player((WIN_WIDTH-player_width)/2,WIN_HEIGHT-player_height, player_img)
Me.health = PLAYER_HEALTH

Enemies = []

for _ in range(NB_ENEMIES):
	new_enemy = enemy(randint(WIN_WIDTH),-enemy_height,enemy_img)
	new_enemy.vely = 15
	Enemies.append(new_enemy)

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

	redrawGameWindow(win,laser_on,Me,Enemies)

with open('SCORE.txt','a') as file:
	file.write('EPISODE: '+ str(EPISODE) + '\n')
	file.write(str(SCORE) + '\n')

pygame.quit()