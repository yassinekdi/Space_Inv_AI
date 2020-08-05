import pygame
from data import *
from Objects import *

def touch(obj1,obj2):
	Cx = obj1.posx+obj1.width >= obj2.posx and obj1.posx <= obj2.posx + obj2.width
	Cy = obj1.posy + obj1.height >= obj2.posy and obj1.posy <= obj2.posy + obj2.height

	if Cx and Cy:
		return True
	return False


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