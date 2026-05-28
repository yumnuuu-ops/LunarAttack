import pygame
from SoundManager import SoundManager
from AssetManager import AssetManager

pygame.init()

pygame.mixer.set_num_channels(32)
sound = SoundManager()
assetMgr = AssetManager(2)