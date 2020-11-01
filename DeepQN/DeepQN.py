import pygame
import sys
from random import choice, sample
from Game.data import *
from Game.Objects import *
from Game.functions import *
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from collections import deque
import pandas as pd

class DQNAgent:
	def __init__(self,params):
		self.replay_memory = deque(maxlen=params['replay_memory_size'])		
		self.batch_size = params['batch_size']
		self.gamma = params['gamma']


		self.input_layer = params['state_space']
		self.first_layer = params['first_layer_size']
		self.second_layer = params['second_layer_size']
		self.third_layer = params['third_layer_size']
		self.output_layer = params['action_space']
		self.learning_rate = params['learning_rate']


		self.model = self.new_model()

		self.target_model = self.new_model()
		self.target_model.set_weights(self.model.get_weights())
		self.target_update_counter = 0
		self.update_target_every = params['update_target_every']
		self.loss_list = []
		self.meanq = []

	def new_model(self):
		model = Sequential()
		model.add(Dense(units=self.first_layer, activation = 'relu', input_dim=self.input_layer))
		model.add(Dense(units=self.second_layer, activation = 'relu'))
		# model.add(Dense(units=self.third_layer, activation = 'relu'))
		model.add(Dense(units=self.output_layer, activation = 'softmax'))
		model.compile(loss='mse', optimizer=Adam(self.learning_rate), metrics=["accuracy"])
		return model

	def update_replay_memory(self,transition):
		self.replay_memory.append(transition)

	def get_q_values(self,state):
		return self.model.predict(state)[0]

	def train(self,termination):
		if len(self.replay_memory) < params['min_replay_memory_size']:
			return

		batch = sample(self.replay_memory,self.batch_size)
		
		for transition in batch:		
			current_states = np.array([transition[0] for transition in batch])
			# some times transition[0] is already flat (no idea why), so :
			# if isinstance(transition[0][0],tuple):				
			# 	current_states = np.array([flatten_list(transition[0],WIN_WIDTH) for transition in batch])
			# else:
			# 	current_states = np.array([transition[0] for transition in batch])

		current_qs_values = self.model.predict(current_states)
		next_states = np.array([transition[3] for transition in batch])
		# if isinstance(transition[3][0],tuple):
		# 	next_states = np.array([flatten_list(transition[3],WIN_WIDTH) for transition in batch])
		# else:
		# 	next_states = np.array([transition[3] for transition in batch])

		next_qs_values = self.target_model.predict(next_states)
		y = []

		for ind,(_,action,reward,next_state,done) in enumerate(batch):
			if not done:
				max_future_q = np.max(next_qs_values[ind])
				new_q = reward + self.gamma*max_future_q
			else:
				new_q = reward
			current_qs = current_qs_values[ind]
			current_qs[action] = new_q

			y.append(current_qs)
			
		

		fitting= self.model.fit(current_states,np.array(y),batch_size=self.batch_size, verbose=0, shuffle=False)
		self.loss_list.append(fitting.history['loss'][0])

		self.meanq = [list(elt) for elt in y[10:15]]

		if termination:
			self.target_update_counter+=1
		if self.target_update_counter > self.update_target_every:
			self.target_model.set_weights(self.model.get_weights())
			self.target_update_counter=0

class Space_env:
	# Rewards
	DEATH_REWARD = -1  #-10
	PLAYER_HIT_REWARD = -.5  #-5
	ENEMY_HIT_REWARD = .5   #5
	ENEMY_KILLED_REWARD = 1  # 10 - value given also in the main bloc
	PLAYER_ALIVE_REWARD = .0001  #1 

	# ACTIONS/STATES
	# STATE_SPACE = 14  # (enemy position - player position) 10 times (10 enemies) 
					  # + 4 min(laser enemy position - player position) (the 4 closest lasers)
	# ACTION_SPACE = 4 # Left right still shoot
	ACTIONS = [0,1,2,3]
	TOTAL_EPISODES = define_DQN_params()['total_episodes']

	def reset(self,episode):

		self.player,self.enemies = start_game() 
		self.player_shoots = []
		self.enemy_shoots = []


		self.episode_step = episode


		# Observation
		observation= []
		  # enemy relative distance (10) > (7)
		enemy_rel_dist=[]
		for enemy_ in self.enemies:
			enemy_rel_dist.append(enemy_-self.player)

		  # 6 closest lasers: values initialized by 1 (6) > (6) 
		closest_enemy_lasers = [1]*NB_MINIMUM_CLOSEST_LASERS

		  # Player's position (1)
		player_pos = [self.player.posx/WIN_WIDTH]

		  # tracking 4 player's lasers (4) > (2) 
		player_lasers_pos = [0]*NB_LASERS_TRACKED

		  # direction of enemy: +1 if moving right, -1 left (10) > (7)
		direction_enemy = [.5]*NB_ENEMIES

		  # Vel of player (1)
		# direction_player = [1]

		observation = enemy_rel_dist + closest_enemy_lasers + player_pos + player_lasers_pos + direction_enemy

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

			if action == self.ACTIONS[0]:
				self.player.posx-= self.player.velx*DT
			elif action == self.ACTIONS[1]:
				self.player.posx+= self.player.velx*DT
			elif action == self.ACTIONS[2]:
				pass
			elif action == self.ACTIONS[3]:
				if frame%20==0:
					# self.player.shoot()
					player_shoot(self.player,self.player_shoots)
					# self.player.track_laser()

			# Enemy actions
			for enemy_ in self.enemies:
				if enemy_.is_alive and enemy_.in_screen():
					enemy_.move()
					# enemy_.shoot(PROBABILITY_SHOOTING)
					enemy_shoot(enemy_,PROBABILITY_SHOOTING,self.enemy_shoots)
					enemy_.collision(self.player_shoots)
					self.player.collision(self.enemy_shoots)
				else:
					SCORE +=1
					self.enemies.remove(enemy_)

		# Update enemies number
		while len(self.enemies)< NB_ENEMIES:
			new_enemy = enemy(randint(WIN_WIDTH),-randint(enemy_height),enemy_img)
			new_enemy.vely = 15
			self.enemies.append(new_enemy)


		# Update observations
		new_observation= []

		   # Enemy relative distance (10)
		enemy_lasers_positions = []
		las=[]
		enemy_rel_dist=[]
		for enemy_ in self.enemies:
			enemy_rel_dist.append(enemy_-self.player)			
		for laser in self.enemy_shoots:
			enemy_lasers_positions.append(self.player - laser)
			las.append(laser.posy)
				
		   # Closest enemy lasers (6) 
		# print('ENEMY LASERS POSITION : ', enemy_lasers_positions)
		closest_enemy_lasers = self.player.closest_lasers(enemy_lasers_positions,NB_MINIMUM_CLOSEST_LASERS)
		# closest_enemy_lasers = get_lasers_positions(enemy_shoots, NB_MINIMUM_CLOSEST_LASERS)
		while len(closest_enemy_lasers)<NB_MINIMUM_CLOSEST_LASERS:
			closest_enemy_lasers.append(1)


		   # Player's position (1)
		player_pos = [self.player.posx/WIN_WIDTH]

		   # Tracking 4 player's lasers (4)
		player_lasers_pos = get_lasers_positions(self.player,self.player_shoots, NB_LASERS_TRACKED)
		# player_lasers_pos = get_lasers_positions(self.player_shoots, NB_LASERS_TRACKED)
		   #direction of enemy +1 if moving right, -1 left (10)
		direction_enemy = [np.sign(enemy_.velx)/2 for enemy_ in self.enemies]

		new_observation = enemy_rel_dist + closest_enemy_lasers + player_pos + player_lasers_pos + direction_enemy

		# if frame%500==0:			
		# 	with open('enemy_rel_dist.txt','a') as f:
		# 			f.write(str(enemy_rel_dist)+'\n')

		# 	with open('closest_enemy_lasers.txt','a') as f:
		# 			f.write(str(closest_enemy_lasers)+'\n')

		# 	with open('player_lasers_pos.txt','a') as f:
		# 			f.write(str(player_lasers_pos)+'\n')


		# Rewards
		reward = 0
		reward_ = ''
		if self.player.is_alive:
			reward = self.PLAYER_ALIVE_REWARD   # Player safe
			reward_ = 'PLAYER ALIVE'	
		else: # Player is killed
			reward = self.DEATH_REWARD	
			reward_ = 'PLAYER IS KILLED'

		for enemy_ in self.enemies:
			# if self.player.is_hit(self.enemy_shoots):	# Player is hit		
			# 	reward = self.PLAYER_HIT_REWARD
			# 	reward_ = 'PLAYER IS HIT'
			# elif not self.player.is_alive:          # Player is killed
			# 	reward = self.DEATH_REWARD	
			# 	reward_ = 'PLAYER IS KILLED'		
			# elif enemy_.is_hit(self.player_shoots):                   # Enemy is hit
			# 	reward = self.ENEMY_HIT_REWARD
			# 	reward_ = 'ENEMY IS HIT'		
			# elif not enemy_.is_alive:               # Enemy is killed
			# 	reward = self.ENEMY_KILLED_REWARD				
			# 	reward_ = 'ENEMY IS KILLED'		
			# else:
			# 	reward = self.PLAYER_ALIVE_REWARD   # Player safe
			# 	reward_ = 'PLAYER ALIVE'		
				
		

			# if self.player.is_hit(self.enemy_shoots):	# Player is hit		
			if self.player.hit_cond:
				for _ in range(self.player.hit):
					reward += self.PLAYER_HIT_REWARD
				reward_ = 'PLAYER IS HIT', reward
				self.player.hit_cond = False
		
			# if enemy_.is_hit(self.player_shoots):                   # Enemy is hit
			if enemy_.hit_cond:
				for _ in range(enemy_.hit):
					reward += self.ENEMY_HIT_REWARD
				reward_ = 'ENEMY IS HIT ', reward	
				enemy_.hit_cond = False

			if not enemy_.is_alive:               # Enemy is killed
				reward = self.ENEMY_KILLED_REWARD				
				reward_ = 'ENEMY IS KILLED', reward
				
		# Done
		done = False
		if reward == self.DEATH_REWARD or self.episode_step > self.TOTAL_EPISODES:
			done = True
			# run = False
			with open('Game/SCORE.txt','a') as file:
				file.write('EPISODE: '+ str(EPISODE) + '\n')
				file.write(str(SCORE) + '\n')

		options=[[reward_]]
		# options= ['']
		return new_observation, reward, done,options

	def render(self,options=[]):
		redrawGameWindow(win,self.player,self.enemies,episode,self.player_shoots,self.enemy_shoots,options)


def redrawGameWindow(win,agent,enemies,episode, player_shoots, enemy_shoots,options=[]):
	global SCORE
	win.blit(BG,(0,0))
	# keys = pygame.key.get_pressed()
	# if keys[pygame.K_t]:
	# 	done = True

	if agent.is_alive:		
		agent.draw(win,player_shoots)

		for enemy in enemies:
			enemy.draw(win, enemy_shoots)

		# STATS
		words = ['Health: ','Score: ', 'High score: ', 'Episode','reward']
		words_x = WIN_WIDTH + 10
		words_y = []
		# options = [round(elt,2) for elt in options]
		words2 = [str(agent.health-agent.hit),str(SCORE),str(HIGHEST_SCORE),str(episode),str(options[0])]
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
		texts2[-1] = font4.render(words2[-1],1,GREEN)
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
		new_enemy = enemy(randint(WIN_WIDTH),-randint(enemy_height),enemy_img)
		new_enemy.vely = 15
		enemies.append(new_enemy)
	return (agent,enemies)



params = define_DQN_params()
env = Space_env()
agent = DQNAgent(params)

if params['load_weights']:
	agent.model.load_weights(params['weights_path'])

Export_results = pd.DataFrame(columns=['episode','reward','score','epsilon','loss'])

quit = False
for episode in range(1,params['total_episodes']+1):
	current_state = env.reset(episode)
	done = False
	episode_reward=0

	# enemy_shoots = []
	# player_shoots = []
	if quit:
		pygame.quit()
		sys.exit()

	frame=1 # frame enable discontinued shooting 
	# with open('debug.txt', 'a') as f:
		# f.write('EPISODE : ' + str(episode)+'\n')
	debug_iter=0
	reward_bugs = []
	while not done:	
		debug_iter+=1
		pygame.init()
		if np.random.random() > params['epsilon']:
			action = np.argmax(agent.get_q_values(np.array([current_state,])))
		else:
			action = choice(env.ACTIONS)

		frame +=1

		next_state,reward,done,options = env.step(action,frame)
		episode_reward += reward
		reward_bugs.append(reward)

		# To handle bug of Game Over & only enemy killed rewards given
		if len(reward_bugs)==20:
			check_list=[elt==1 for elt in reward_bugs]
			if False in check_list:
				reward_bugs = []
			else:
				print('BUG FIXED')
				done = True

		# DEBUG ITER
		
		# if frame%1000==0:
			# var='w'
		# else:
			# var = 'a'
		# with open('debug.txt', var) as f:
			# f.write('\n')
			# f.write('A : debug_iter : REWARD : '+ str(reward)  + 'REWARD_ ' + str(options) + ' DEBUG ITER '+ str(debug_iter) + '\n')

		if done:
			with open('debug.txt','a') as f:
				f.write('DONE:  '+str(done) + '\n')
				f.write(' \n')

		env.render(options)

		transition = (current_state,action, reward, next_state,done)

		# DEBUG ITER
		# with open('debug.txt', var) as f:
			# f.write('BBBBB' +'\n')		
		if frame%10==0:
			agent.update_replay_memory(transition)

		if frame%500==0:
			with open('STATES.txt','a') as f:
					f.write(str(transition[0])+'   '+str(transition[1])+'   '+str(transition[2])+'\n')
		

		agent.train(done)
		# DEBUG ITER
		# with open('debug.txt', var) as f:
			# f.write('CCCCCC' +'\n')
		meanQ = np.mean(agent.get_q_values(np.array([current_state,])))

		current_state = next_state

		event = pygame.event.poll()
		if event.type == pygame.QUIT:
			quit=True
			done = True

		# DEBUG ITER
		# with open('debug.txt', var) as f:
			# f.write('DDDDDD' +'\n')
	# if len(agent.replay_memory)>params['min_replay_memory_size']:
	# 	with open('meanQ.txt','a') as file:
	# 			file.write(str(agent.meanq)+'\n')

	if episode%params['save_weights_every']==0:
		agent.model.save_weights(params['weights_path'])
	if len(agent.loss_list)>0:
		losses = np.mean(agent.loss_list)
		agent.loss_list = []
	else:
		losses = 0
	Export_results.loc[episode-1] = [episode,episode_reward,SCORE,params['epsilon'],losses]

	if params['minimum_epsilon_reached']:
		pass
	else:
		params['epsilon']*=params['discount_epsilon']

	Export_results.to_excel(params['path_results'])