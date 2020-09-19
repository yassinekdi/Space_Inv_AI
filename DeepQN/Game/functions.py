import pygame
import random
from Game.data import *
from Game.Objects import *

def define_DQN_params():
	params = {}
	params['save_weights_every']= 200
	params['batch_size'] = 64
	params['min_replay_memory_size']= 1_000
	params['replay_memory_size']= 10_000
	params['total_episodes']=3_000
	params['load_weights']=False
	params['action_space'] = 4
	params['state_space'] = 13  # 6 + 1 + 4 + 10 + 10=31 > 3 + 1 + 3 + 3 + 3 = 13
	params['first_layer_size'] = 100
	params['second_layer_size'] = 100
	params['third_layer_size'] = 100
	params['gamma'] = .99
	params['epsilon'] = 1
	params['learning_rate']=.0005
	params['discount_epsilon'] = .999
	params['minimum_epsilon_reached']= params['epsilon'] < .05
	params['update_target_every'] = 5
	params['weights_path'] = r'C:\Users\Cyala\PycharmProjects\RL\PyGame\DeepQN\weights.hdf5'
	# result_(total_episode)_replay.._gamma_discount_update..
	params['path_results']=r'C:\Users\Cyala\PycharmProjects\RL\PyGame\DeepQN\results_{}_{}_{}_{}_{}.xlsx'.format(
		params['total_episodes'], params['replay_memory_size'],params['gamma'],params['discount_epsilon'],params['update_target_every'])
	return params

def touch(obj1,obj2):
	Cx = obj1.posx+obj1.width >= obj2.posx and obj1.posx <= obj2.posx + obj2.width
	Cy = obj1.posy + obj1.height >= obj2.posy and obj1.posy <= obj2.posy + obj2.height

	if Cx and Cy:
		return True
	return False

def flatten_list(list_,norm):
	# [(x1,y1),(x2,y2)] -> [x1,y1,x2,y2] / norm
	return np.array([elt/norm for elt2 in list_ for elt in elt2])


def get_lasers_positions(lasers,nb_lasers):
	y_positions = [laser.posy/WIN_HEIGHT for laser in lasers][:nb_lasers]
	while len(y_positions)<nb_lasers:
		y_positions.append(0)
	return y_positions