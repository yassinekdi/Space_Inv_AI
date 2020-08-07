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
		# self.hitbox = (self.x + 17, self.y + 11, 29, 52)
		self.velx = 200
		self.vely =200
		self.is_alive=True
		self.health = ENEMY_HEALTH	
		self.hit = 0

	def __sub__(self, other):
		return (np.abs(other.posx-self.posx), np.abs(other.posy - self.posy))

	def is_hit(self,other):
		for laser in other.lasers:
			if touch(laser,self):
				return True
			else:
				return False

class player(Gameobject):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.lasers = []

	def shoot(self):
		X = self.posx + (self.width-laser_width)/2
		Y = self.posy-laser_height
		self.lasers.append(Gameobject(X,Y,laser_player_img))

	def draw(self,win):
		for laser in self.lasers:
			if laser.posy > 0:
				laser.posy -= laser.vely*DT
			else:
				self.lasers.remove(laser)
			win.blit(laser.img,(laser.posx,laser.posy))	
		win.blit(self.img,(self.posx,self.posy))

	def collision(self,enemy):
		for laser in enemy.lasers:
			if touch(laser,self):
				enemy.lasers.remove(laser)
				self.hit +=1
				if self.hit >= self.health:
					self.is_alive = False
					self.posx = 1000000
					self.posy = 1000000

class enemy(Gameobject):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.lasers = []

	def shoot(self,probability):
		if random.random() < probability:
			X = self.posx + (self.width-laser_width)/2
			Y = self.posy+enemy_height
			self.lasers.append(Gameobject(X,Y,laser_enemy_img))

	def draw(self,win):
		for laser in self.lasers:
			if laser.posy < WIN_HEIGHT:
				laser.posy += laser.vely*DT
			else:
				self.lasers.remove(laser)
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
		

	def collision(self,player):
		for laser in player.lasers:
			if touch(laser,self):
				player.lasers.remove(laser)
				self.hit +=1
				if self.hit >= self.health:
					self.is_alive = False