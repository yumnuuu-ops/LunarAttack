import pygame


class Player:
    def __init__(self):
        self.health = 100
        self.fireRate = 1
        self.projectileCount = 1
        self.projectileType = "cannon"

    def shootLaser(self):

    def shootBomb(self):

    def takeDamage(self, damage):
        self.health -= damage

    def changeFireMode(self):

