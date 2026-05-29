import pygame
from SoundManager import SoundManager
from AssetManager import AssetManager

pygame.init()

pygame.mixer.set_num_channels(32)
soundMgr = SoundManager()
assetMgr = AssetManager(2)
dt = 0.0

projectile_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()