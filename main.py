import pygame
import sys
import random
import pygame_menu as pyMenu

from Player import Player

pygame.init()
pygame.font.init()
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


#states
MENU, DIFFICULTY_1_SCREEN, DIFFICULTY_2_SCREEN, DIFFICULTY_3_SCREEN = "menu", "difficulty_1_screen", "difficulty_2_screen", "difficulty_3_screen"
currState = MENU
selected_difficulty = 0

def startGame():
    global currState
    currState = DIFFICULTY_1_SCREEN

def startMenu():
    global currState
    currState = MENU

def setDifficulty(value):
    global selected_difficulty
    selected_difficulty = value

def openHistory():
    print("History")

def openCredits():
    print("Credits")

def quitGame():
    global running
    running = False


###MAIN MENU###
theme = pyMenu.themes.THEME_DEFAULT.copy()
theme.title = False
theme.background_color = pyMenu.BaseImage("imgs\\backdrop.jpg")
mainMenu = pyMenu.Menu("SpaceCode", screen.get_size()[0], screen.get_size()[1], theme=theme)
mainMenu.add.button("Play", startGame)
mainMenu.add.button("History", openHistory)
mainMenu.add.button("Credits", openCredits)
mainMenu.add.button("Quit", quitGame)

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
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False


    screen.blit(background, (0, 0))

    if currState == MENU:
        mainMenu.update(events)
        mainMenu.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()