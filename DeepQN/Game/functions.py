import pygame
from Game.data import *
from Game.Objects import *

def define_DQN_params():
	params = {}
	params['total_episodes']=5
	params['epsilon'] = 1/2
	return params

def touch(obj1,obj2):
	Cx = obj1.posx+obj1.width >= obj2.posx and obj1.posx <= obj2.posx + obj2.width
	Cy = obj1.posy + obj1.height >= obj2.posy and obj1.posy <= obj2.posy + obj2.height

	if Cx and Cy:
		return True
	return False
