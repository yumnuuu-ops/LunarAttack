import pygame
import sys
import random

from Player import Player

pygame.init()
pygame.font.init()
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# ===================================== Asset Loading =====================================
background = pygame.image.load("imgs\\backdrop.jpg")
cadet = pygame.image.load("imgs\\cadet.png")
alien = pygame.image.load("imgs\\alien.png")

# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)
background = pygame.transform.scale(background, (1280, 720))



# ========================================== Get Size ======================================
backgroundRect = background.get_rect()
alienRect = alien.get_rect()
cadetRect = cadet.get_rect()

# ====================================== Object Creation ======================================
player = Player()

# ======================================== Main loop =======================================
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()