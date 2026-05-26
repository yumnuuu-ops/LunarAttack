import pygame
import sys
import os
import random
import pygame_menu as pyMenu
from AssetManager import AssetManager
from MainMenu import MainMenu
from Player import Player
from background import Background
from PlayScreen import PlayScreen

pygame.init()
pygame.font.init()
press_start = pygame.font.Font("PressStart2P-Regular.ttf", 20)
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
menu = MainMenu(screen_w, screen_h)
bg = Background(1280, 720)
clock = pygame.time.Clock()
assetMgr = AssetManager(2)


#states
MENU, PLAY_SCREEN, DIFFICULTY_1, DIFFICULTY_2, DIFFICULTY_3 = "menu", "play_screen", "difficulty_1", "difficulty_2", "difficulty_3"
currState = MENU

def setDifficulty(selected_diff):
    global currState
    currState = DIFFICULTY_1 if selected_diff == "Easy" else DIFFICULTY_2 if selected_diff == "Medium" else DIFFICULTY_3

def quitGame():
    global running
    running = False

##themes###
theme = pyMenu.themes.THEME_DEFAULT.copy()
theme.title = False
theme.background_color = (0,0,0,0)
# theme.widget_font = pyMenu.font.FONT_8BIT
theme.widget_font = "PressStart2P-Regular.ttf"
theme.widget_font_size = 18
theme.widget_font_color = (255,255,255)
theme.widget_font_shadow = True
theme.widget_font_shadow_color = (0,100,255)
theme.selection_color = (0,200,255)

###MENU###
mainMenu = pyMenu.Menu("SpaceCode", screen.get_size()[0], screen.get_size()[1], theme=theme)
selectDifficultyMenu = pyMenu.Menu("Select Difficulty", screen.get_size()[0], screen.get_size()[1], theme=theme)
historyMenu = pyMenu.Menu("History", screen.get_size()[0], screen.get_size()[1], theme=theme)
creditsMenu = pyMenu.Menu("Credits", screen.get_size()[0], screen.get_size()[1], theme=theme)

##add components###
mainMenu.add.button("Play", selectDifficultyMenu)
mainMenu.add.button("History", historyMenu)
mainMenu.add.button("Credits", creditsMenu)
mainMenu.add.button("Quit", quitGame)

selectDifficultyMenu.add.button("Easy", setDifficulty, "Easy")
selectDifficultyMenu.add.button("Medium", setDifficulty, "Medium")
selectDifficultyMenu.add.button("Hard", setDifficulty, "Hard")
selectDifficultyMenu.add.button("Back", pyMenu.events.BACK)

historyMenu.add.button("Back", pyMenu.events.BACK)

creditsMenu.add.label("Developed by")
creditsMenu.add.label("Kenzieng")
creditsMenu.add.label("Jinyoung")
creditsMenu.add.label("Yumnung")

creditsMenu.add.label("")
creditsMenu.add.label("Graphics:")
creditsMenu.add.label("Kenzie")
creditsMenu.add.label("")
creditsMenu.add.label("Music:")
creditsMenu.add.label("Kenzie")
creditsMenu.add.label("")
creditsMenu.add.label("SFX:")
creditsMenu.add.label("Kenzie")

creditsMenu.add.button("Back", pyMenu.events.BACK)





# ===================================== Asset Loading =====================================
imageScale = 2

assetMgr.loadTexture("cadet","imgs\\cadet.png")
assetMgr.loadTexture("alien","imgs\\alien.png")

# Ship
shipTex = assetMgr.loadTexture("MainShip Full","imgs\\Main Ship - Full health.png")
shipRect = assetMgr.getRect("MainShip Full")
assetMgr.loadTexture("MainShip SDam","imgs\\Main Ship - Slight damage.png")
assetMgr.loadTexture("MainShip Dam","imgs\\Main Ship -Damaged.png")
assetMgr.loadTexture("MainShip VDam","imgs\\Main Ship - Very damaged.png")

gun1Tex = assetMgr.loadAnim("AutoCannon","imgs\\Main Ship - Weapons - Auto Cannon.png")
gun2Tex = assetMgr.loadAnim("BigGun","imgs\\Main Ship - Weapons - Big Space Gun.png")
gun3Tex = assetMgr.loadAnim("Zapper","imgs\\Main Ship - Weapons - Zapper.png")
gun4Tex = assetMgr.loadAnim("Rockets","imgs\\Main Ship - Weapons - Rockets.png")


# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)

# ========================================== Get Size ======================================
#removed for background

# ====================================== Object Creation ======================================
player = Player(assetMgr,200, 300)
projectile_group = pygame.sprite.Group()

# ======================================== Main loop =======================================
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # only update player and projectiles when actually in game
    if currState in (DIFFICULTY_1, DIFFICULTY_2, DIFFICULTY_3):
        player.update()

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            bullets = player.weapon.shootProjectile()
            if bullets is not None:
                projectile_group.add(*bullets)

        projectile_group.update()

    if currState == MENU:
        dt = clock.get_time() / 1000.0
        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen, darkened=True)
        menu.update(events)
        menu.draw(screen)

        if menu.action == "PLAY":
            menu.slide_out()
        elif menu.action == "SLIDEOUT_DONE":
            currState = PLAY_SCREEN
            play_screen = PlayScreen(screen_w, screen_h)
        elif menu.action == "QUIT":
            running = False

    elif currState == PLAY_SCREEN:
        dt = clock.get_time() / 1000.0
        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen, darkened=True)
        play_screen.update(events)
        play_screen.draw(screen)

        if play_screen.action == "START":
            if play_screen.difficulty == "Easy":
                currState = DIFFICULTY_1
            elif play_screen.difficulty == "Medium":
                currState = DIFFICULTY_2
            elif play_screen.difficulty == "Hard":
                currState = DIFFICULTY_3
        elif play_screen.action == "BACK":
            currState = MENU

    elif currState == DIFFICULTY_1:
        dt = clock.get_time() / 1000.0
        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)
        projectile_group.draw(screen)

    elif currState == DIFFICULTY_2:
        dt = clock.get_time() / 1000.0
        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)
        projectile_group.draw(screen)

    elif currState == DIFFICULTY_3:
        dt = clock.get_time() / 1000.0
        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)
        projectile_group.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()