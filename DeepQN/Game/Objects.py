import pygame
from numpy import random
from numpy.random import randint
from Game.data import *
from Game.functions import *

class Gameobject:
	def __init__(self,posx,posy,img):
		self.posx= posx
		self.posy = posy
		self.width,self.height = img.get_rect().size
		self.img = img
		self.left = False
		self.right = False
		self.velx = 200
		self.vely =200
		self.is_alive=True
		self.health = ENEMY_HEALTH	
		self.hit = 0
		self.hit_cond = False

	def __sub__(self, other):
		sign = np.sign(other.posx-self.posx)
		return sign*np.sqrt((other.posx-self.posx)**2+(other.posy - self.posy)**2)/WIN_HEIGHT
		# return (sign*(other.posx-self.posx), other.posy - self.posy)


	# def is_hit(self,lasers):
	# 	for laser in lasers:			
	# 		if touch(laser,self):
	# 			# print('TOUCHED')
	# 			return True
	# 		else:
	# 			return False

class player(Gameobject):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		# self.lasers = []
		# self.lasers_tracked = []

	# def shoot(self):
	# 	X = self.posx + (self.width-laser_width)/2
	# 	Y = self.posy-laser_height
	# 	self.lasers.append(Gameobject(X,Y,laser_player_img))

	def draw(self,win,player_shoots):
		for laser in player_shoots:
			if laser.posy > 0:
				laser.posy -= laser.vely*DT*2
			else:
				player_shoots.remove(laser)
			win.blit(laser.img,(laser.posx,laser.posy))	
		win.blit(self.img,(self.posx,self.posy))

	def collision(self,enemy_lasers):
		for laser in enemy_lasers:
			if touch(laser,self):
				enemy_lasers.remove(laser)
				self.hit +=1
				self.hit_cond=True
				if self.hit >= self.health:
					self.is_alive = False
					self.posx = 1000000
					self.posy = 1000000

	def closest_lasers(self,lasers_positions,treshold):
		if len(lasers_positions)>0:			
			result=sorted(lasers_positions, key=abs)[:treshold]
		    # result =sorted([np.abs(elt) for elt in lasers_positions])[:treshold]
		else:
		   	result=[]
		return result

	# def track_laser(self):
	# 	if len(self.lasers_tracked)< NB_LASERS_TRACKED:
	# 		self.lasers_tracked.append(self.lasers[-1])

	# def get_lasers_positions(self,nb_lasers):
	# 	y_positions = [laser.posy/WIN_HEIGHT for laser in self.lasers_tracked]
	# 	while len(y_positions)<nb_lasers:
	# 		y_positions.append(0)
	# 	return y_positions


class enemy(Gameobject):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		# self.lasers = []

	# def shoot(self,probability):
	# 	if random.random() < probability:
	# 		X = self.posx + (self.width-laser_width)/2
	# 		Y = self.posy+enemy_height
	# 		self.lasers.append(Gameobject(X,Y,laser_enemy_img))

	def draw(self,win,lasers):
		for laser in lasers:
			if laser.posy < WIN_HEIGHT:
				laser.posy += laser.vely*DT/4
			else:
				lasers.remove(laser)
			win.blit(laser.img,(laser.posx,laser.posy))	
		win.blit(self.img,(self.posx,self.posy))

	def move(self):
		if self.posx >= WIN_WIDTH-enemy_width:
			self.posx = WIN_WIDTH-enemy_width
			self.velx *=-1
		if self.posx <= 0:
			self.posx = 0
			self.velx *=-1
		self.posx += self.velx*DT
		self.posy += self.vely*DT
		

	def collision(self,laser_list):
		for laser in laser_list:
			if touch(laser,self):
				# if laser in player.lasers_tracked:
					# player.lasers_tracked.remove(laser)
				laser_list.remove(laser)
				self.hit +=1
				self.hit_cond=True
				if self.hit >= self.health:
					self.is_alive = False

	def in_screen(self):
		return self.posy < WIN_HEIGHT


def enemy_shoot(enemy,probability,lasers):
	if random.random() < probability:
		X = enemy.posx + (enemy.width-laser_width)/2
		Y = enemy.posy+enemy_height
		lasers.append(Gameobject(X,Y,laser_enemy_img))

	return lasers

def player_shoot(player,lasers):
	X = player.posx + (player.width-laser_width)/2
	Y = player.posy-laser_height
	lasers.append(Gameobject(X,Y,laser_player_img))

	return lasers


