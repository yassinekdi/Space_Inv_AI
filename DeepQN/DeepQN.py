
import pygame
import sys
from random import choice
from Game.data import *
from Game.Objects import *
from Game.functions import *
# from PIL import Image
# import matplotlib.pyplot as plt


class DQNAgent:
	def __init__(self):
		pass

	def create_model(self):
		pass

	def update_replay_memory(self):
		pass

	def get_q_value(self,state):
		pass

	def train(self,terminalstate,step):
		pass


class Space_env:

	# Rewards
	DEATH_REWARD = -20
	PLAYER_HIT_REWARD = -15
	ENEMY_HIT_REWARD = 15
	ENEMY_KILLED_REWARD = 20

	# Dimensions
	STATE_SPACE = 14  # (enemy position - player position) 10 times (10 enemies) 
					  # + 4 min(laser enemy position - player position) (the 4 closest lasers)
	ACTION_SPACE = 4 # Left right still shoot
	ACTIONS = {"still":[1,0,0,0],
			   "right": [0,1,0,0],
			   "left": [0,0,1,0], 
			   "shoot": [0,0,0,1]}
	TOTAL_EPISODES = define_DQN_params()['total_episodes']

	def reset(self,episode):

		self.player,self.enemies = start_game() 

		self.episode_step = episode

		# Observation
		  # enemy relative position
		observation= []
		for enemy_ in self.enemies:
			observation.append(enemy_-self.player)

		  # 4 closest lasers: values initialized by (100,100)
		observation = observation + [(100,100)]*NB_MINIMUM_CLOSEST_LASERS

		return observation

	def step(self,action,frame):
		global SCORE

		# Player actions
		if self.player.is_alive:
			# Player actions
			if self.player.posx >= WIN_WIDTH-enemy_width:
				self.player.posx = WIN_WIDTH-enemy_width
			if self.player.posx <= 0:
				self.player.posx = 0

			if action == self.ACTIONS['left']:
				self.player.posx-= self.player.velx*DT
			elif action == self.ACTIONS['right']:
				self.player.posx+= self.player.velx*DT
			elif action == self.ACTIONS['still']:
				pass
			elif action == self.ACTIONS['shoot']:
				if frame%30==0:
					self.player.shoot()

			# Enemy actions
			for enemy_ in self.enemies:
				if enemy_.is_alive:
					enemy_.move()
					enemy_.shoot(PROBABILITY_SHOOTING)
					enemy_.collision(self.player.lasers)
					self.player.collision(enemy_)
				else:
					SCORE +=1
					self.enemies.remove(enemy_)

		# Update observations
		new_observation= []
		enemy_lasers = []
		for enemy_ in self.enemies:
			new_observation.append(enemy_-self.player)
			for laser in enemy_.lasers:
				enemy_lasers.extend(laser - self.player)
		closest_enemy_lasers = sorted(enemy_lasers[:NB_MINIMUM_CLOSEST_LASERS])
		new_observation = new_observation + closest_enemy_lasers

		# Rewards
		reward = 0
		for enemy_ in self.enemies:
			if 0 < self.player.hit < self.player.health:			
				reward = self.PLAYER_HIT_REWARD
			elif not self.player.is_alive:
				reward = self.DEATH_REWARD			
			elif 0 < enemy_.hit < enemy_.health:
				reward = self.ENEMY_HIT_REWARD
			elif not enemy_.is_alive:
				reward = self.ENEMY_KILLED_REWARD
	
		# Done
		done = False
		if reward == self.DEATH_REWARD or self.episode_step > self.TOTAL_EPISODES:
			done = True
			# run = False
			with open('Game/SCORE.txt','a') as file:
				file.write('EPISODE: '+ str(EPISODE) + '\n')
				file.write(str(SCORE) + '\n')

		return new_observation, reward, done

	def render(self):
		while len(self.enemies)< NB_ENEMIES:
			new_enemy = enemy(randint(WIN_WIDTH),-enemy_height,enemy_img)
			new_enemy.vely = 15
			self.enemies.append(new_enemy)

		redrawGameWindow(win,self.player,self.enemies,episode)


def redrawGameWindow(win,agent,enemies,episode):
	global SCORE
	win.blit(BG,(0,0))
	if agent.is_alive:		
		agent.draw(win)

		for enemy in enemies:
			enemy.draw(win)

		# STATS
		words = ['Health: ','Score: ', 'High score: ', 'Episode']
		words_x = WIN_WIDTH + 10
		words_y = []
		words2 = [str(agent.health-agent.hit),str(SCORE),str(HIGHEST_SCORE),str(episode)]
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
			
	pygame.display.update()

		
def start_game():
	global SCORE
	global HIGHEST_SCORE
	global EPISODE 
	with open('Game/SCORE.txt','r') as file:
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



params = define_DQN_params()
env = Space_env()
# Agent = DQNAgent()

quit = False
for episode in range(1,params['total_episodes']+1):
	current_state = env.reset(episode)
	done = False

	frame=1
	if quit:
		pygame.quit()
		sys.exit()

	while not done:	
		
		pygame.init()
		action = choice(list(ACTIONS.keys()))
		frame +=1
		new_state,reward,done = env.step(ACTIONS[action],frame)
		env.render()
		event = pygame.event.poll()
		if event.type == pygame.QUIT:
			quit=True
			done = True

	# with open('Game/SCORE.txt','a') as file:
	# 	file.write('EPISODE: '+ str(EPISODE) + '\n')
	# 	file.write(str(SCORE) + '\n')
	
	