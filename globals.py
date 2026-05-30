import pygame
from SoundManager import SoundManager
from AssetManager import AssetManager

pygame.init()

soundMgr = SoundManager()
assetMgr = AssetManager(2)
dt = 0.0

projectile_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()