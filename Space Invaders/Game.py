import pygame
from data import *
from Objects import *
from functions import *


def redrawGameWindow(win,laser_on,agent,enemies,player_shoots,enemy_shoots):
	global SCORE

	win.blit(BG,(0,0))
	if agent.is_alive:
		agent.move()
		probability_shooting = 1/200
		for enemy in enemies:
			if enemy.is_alive:
				enemy.move()
				# enemy.shoot(probability_shooting)
				enemy_shoot(enemy,probability_shooting,enemy_shoots)
				enemy.collision(player_shoots)
				agent.collision(enemy_shoots)
			else:
				SCORE +=1
				enemies.remove(enemy)
		if laser_on:
			# agent.shoot()	
			player_shoot(agent,player_shoots)
		agent.draw(win,player_shoots)

		for enemy in enemies:
			enemy.draw(win,enemy_shoots)

		# STATS
		words = ['Health: ','Score: ', 'High score: ']
		words_x = WIN_WIDTH + 10
		words_y = []
		words2 = [str(agent.health-agent.hit),str(SCORE),str(HIGHEST_SCORE)]
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
		text2 = font2.render('Press space to restart ',1, GREEN)
		txt_width,txt_height = text.get_rect().size
		txt2_width,txt2_height = text2.get_rect().size

		win.blit(text, ((WIN_WIDTH+MENU_WIDTH-txt_width)/2, (WIN_HEIGHT-txt_height)/2))	
		win.blit(text2, ((WIN_WIDTH+MENU_WIDTH-txt2_width)/2, (WIN_HEIGHT-txt_height)/2+100))	
		del agent

		keys = pygame.key.get_pressed()
		if keys[pygame.K_SPACE]:
			return False
			
	pygame.display.update()
	return True



def start_game():
	global SCORE
	global HIGHEST_SCORE
	global EPISODE 
	with open('SCORE.txt','r') as file:
	 reader = list(csv.reader(file))
	 if len(reader) >=2:
	 	ind = np.arange(1,len(reader),step=2)
	 	EPISODE = int(reader[-2][0].split(' ')[1])+1	 	
	 	scores = [int(reader[i][0]) for i in ind]
	 	HIGHEST_SCORE = max(scores)

	SCORE = 0

	agent = player((WIN_WIDTH-player_width)/2,WIN_HEIGHT-player_height, player_img)
	agent.health = PLAYER_HEALTH

	enemies = []

	for _ in range(NB_ENEMIES):
		new_enemy = enemy(randint(WIN_WIDTH),-enemy_height,enemy_img)
		new_enemy.vely = 15
		enemies.append(new_enemy)
	return (agent,enemies)

# Mainloop ----------------------------------

Me,Enemies = start_game()
enemy_shoots = []
player_shoots = []
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

	if not redrawGameWindow(win,laser_on,Me,Enemies, player_shoots, enemy_shoots):
		with open('SCORE.txt','a') as file:
			file.write('EPISODE: '+ str(EPISODE) + '\n')
			file.write(str(SCORE) + '\n')

		Me,Enemies=start_game()

with open('SCORE.txt','a') as file:
	file.write('EPISODE: '+ str(EPISODE) + '\n')
	file.write(str(SCORE) + '\n')


pygame.quit()