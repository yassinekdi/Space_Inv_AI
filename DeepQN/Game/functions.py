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
	params['state_space'] = 24  # 6 + 1 + 4 + 10 + 10=31 > 6 + 1 + 3 + 7 + 7 = 24
	params['first_layer_size'] = 100
	params['second_layer_size'] = 100
	params['third_layer_size'] = 100
	params['gamma'] = .99
	params['epsilon'] = 1
	params['learning_rate']= .000001 #.00001 #.0000001 #.0001
	params['discount_epsilon'] = .999
	params['minimum_epsilon_reached']= params['epsilon'] < .05
	params['update_target_every'] = 5
	params['weights_path'] = r'C:\Users\Cyala\PycharmProjects\RL\PyGame\DeepQN\weights.hdf5'
	# result_(total_episode)_replay.._gamma_discount_update..
	params['path_results']=r'C:\Users\Cyala\PycharmProjects\RL\PyGame\DeepQN\results_{}_{}_{}_{}_{}.xlsx'.format(
		params['learning_rate'], params['replay_memory_size'],params['gamma'],params['discount_epsilon'],params['update_target_every'])
	return params

def touch(obj1,obj2):
	# obj1: gameobject & obj2: laser
	margin=0
	Cx = obj1.posx+obj1.width >= obj2.posx+margin and obj1.posx <= obj2.posx + obj2.width+margin
	Cy = obj1.posy + obj1.height >= obj2.posy+margin and obj1.posy <= obj2.posy + obj2.height	+margin
	if Cx and Cy:
		return True
	else:
		return False


def flatten_list(list_,norm):
	# [(x1,y1),(x2,y2)] -> [x1,y1,x2,y2] / norm
	return np.array([elt/norm for elt2 in list_ for elt in elt2])


def get_lasers_positions(player,lasers,nb_lasers):
	rel_positions = [player-laser for laser in lasers][:nb_lasers]
	while len(rel_positions)<nb_lasers:
		rel_positions.append(0)
	return rel_positions

# def get_lasers_positions(lasers,nb_lasers):
# 	y_positions = [laser.posy/WIN_HEIGHT for laser in lasers][:nb_lasers]
# 	while len(y_positions)<nb_lasers:
# 		y_positions.append(0)
# 	return y_positions