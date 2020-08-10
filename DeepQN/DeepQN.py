
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

	def new_model(self):
		model = Sequential()
		model.add(Dense(units=self.first_layer, activation = 'relu', input_dim=self.input_layer))
		model.add(Dense(units=self.second_layer, activation = 'relu'))
		model.add(Dense(units=self.third_layer, activation = 'relu'))
		model.add(Dense(units=self.output_layer, activation = 'softmax'))
		model.compile(loss='mse', optimizer=Adam(self.learning_rate), metrics=["accuracy"])
		return model

	def update_replay_memory(self,transition):
		self.replay_memory.append(transition)

	def get_q_values(self,state):
		return self.model.predict(state)

	def train(self,termination):
		if len(self.replay_memory) < params['min_replay_memory_size']:
			return

		batch = sample(self.replay_memory,self.batch_size)

		# flatten_list transform [(x1,y1), (x2,y2),...] to [x1,y1,x2,y2...]
		for transition in batch:
			# some times transition[0] is already flat (no idea why), so :
			if isinstance(transition[0][0],tuple):
				current_states = np.array([flatten_list(transition[0],WIN_WIDTH) for transition in batch])
			else:
				current_states = np.array([transition[0] for transition in batch])
		current_qs_values = self.model.predict(current_states)
		
		if isinstance(transition[3][0],tuple):
			next_states = np.array([flatten_list(transition[3],WIN_WIDTH) for transition in batch])
		else:
			next_states = np.array([transition[3] for transition in batch])
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

		if termination:
			self.target_update_counter+=1
		if self.target_update_counter > self.update_target_every:
			self.target_model.set_weights(self.model.get_weights())
			self.target_update_counter=0


class Space_env:
	# Rewards
	DEATH_REWARD = -1.5
	PLAYER_HIT_REWARD = -.5
	ENEMY_HIT_REWARD = .5
	ENEMY_KILLED_REWARD = 1
	PLAYER_ALIVE_REWARD = .001

	# ACTIONS/STATES
	STATE_SPACE = 14  # (enemy position - player position) 10 times (10 enemies) 
					  # + 4 min(laser enemy position - player position) (the 4 closest lasers)
	ACTION_SPACE = 4 # Left right still shoot
	ACTIONS = [0,1,2,3]
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
		return flatten_list(observation,WIN_WIDTH)

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
					self.player.shoot()

			# Enemy actions
			for enemy_ in self.enemies:
				if enemy_.is_alive:
					enemy_.move()
					enemy_.shoot(PROBABILITY_SHOOTING)
					enemy_.collision(self.player)
					self.player.collision(enemy_)
				else:
					SCORE +=1
					self.enemies.remove(enemy_)

		# Update enemies number
		while len(self.enemies)< NB_ENEMIES:
			new_enemy = enemy(randint(WIN_WIDTH),-enemy_height,enemy_img)
			new_enemy.vely = 15
			self.enemies.append(new_enemy)

		# Update observations
		new_observation= []
		enemy_lasers = []
		for enemy_ in self.enemies:
			new_observation.append(enemy_-self.player)
			for laser in enemy_.lasers:
				enemy_lasers.append(laser - self.player)
		
		closest_enemy_lasers = sorted(enemy_lasers[:NB_MINIMUM_CLOSEST_LASERS])
		while len(closest_enemy_lasers)<NB_MINIMUM_CLOSEST_LASERS:
			closest_enemy_lasers.append((0,WIN_HEIGHT))

		new_observation = new_observation + closest_enemy_lasers

		# Rewards
		reward = 0
		for enemy_ in self.enemies:
			if self.player.is_hit(enemy_):	# Player is hit		
				reward = self.PLAYER_HIT_REWARD
			elif not self.player.is_alive:          # Player is killed
				reward = self.DEATH_REWARD			
			elif enemy_.is_hit(self.player):                   # Enemy is hit
				reward = self.ENEMY_HIT_REWARD
			elif not enemy_.is_alive:               # Enemy is killed
				reward = self.ENEMY_KILLED_REWARD
			else:
				reward = self.PLAYER_ALIVE_REWARD   # Player safe
	
		# Done
		done = False
		if reward == self.DEATH_REWARD or self.episode_step > self.TOTAL_EPISODES:
			done = True
			# run = False
			with open('Game/SCORE.txt','a') as file:
				file.write('EPISODE: '+ str(EPISODE) + '\n')
				file.write(str(SCORE) + '\n')

		return flatten_list(new_observation,WIN_WIDTH), reward, done

	def render(self):
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
agent = DQNAgent(params)
if params['load_weights']:
	agent.model.load_weights(params['weights_path'])

Export_results = pd.DataFrame(columns=['episode','reward','score','epsilon','loss'])

quit = False
for episode in range(1,params['total_episodes']+1):
	current_state = env.reset(episode)
	done = False
	episode_reward=0

	if quit:
		pygame.quit()
		sys.exit()

	frame=1 # frame enable discontinued shooting 
	while not done:			
		pygame.init()
		if np.random.random() > params['epsilon']:
			action = np.argmax(agent.get_q_values(np.array([current_state,])))
		else:
			action = choice(env.ACTIONS)

		frame +=1

		next_state,reward,done = env.step(action,frame)
		episode_reward += reward
		env.render()

		transition = (current_state,action, reward, next_state,done)
		agent.update_replay_memory(transition)
		agent.train(done)

		current_state = next_state

		event = pygame.event.poll()
		if event.type == pygame.QUIT:
			quit=True
			done = True

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