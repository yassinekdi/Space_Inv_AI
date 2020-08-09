import pygame
from Game.data import *
from Game.Objects import *

def define_DQN_params():
	params = {}
	params['total_episodes']=5
	params['save_weights_every']= 2
	params['load_weights']=False
	params['batch_size'] = 2
	params['epsilon'] = 1
	params['replay_memory_size']= 10_000
	params['min_replay_memory_size']= 1_000
	params['action_space'] = 4
	params['state_space'] = 28
	params['first_layer_size'] = 60
	params['second_layer_size'] = 60
	params['third_layer_size'] = 60
	params['gamma'] = .99
	params['discount_epsilon'] = .99
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
