import pygame
import math

ENEMY_SPEED = 4


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y


    
