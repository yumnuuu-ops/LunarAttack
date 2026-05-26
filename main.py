import pygame
import sys
import random
import pygame_menu as pyMenu
from AssetManager import AssetManager
from Player import Player

pygame.init()
pygame.font.init()
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
clock = pygame.time.Clock()
assetMgr = AssetManager()


#states
MENU, SELECT_DIFFICULTY, DIFFICULTY_1, DIFFICULTY_2, DIFFICULTY_3 = "menu", "select_difficulty", "difficulty_1", "difficulty_2", "difficulty_3"
currState = MENU

def setDifficulty(selected_diff):
    global currState
    currState = DIFFICULTY_1 if selected_diff == "Easy" else DIFFICULTY_2 if selected_diff == "Medium" else DIFFICULTY_3

def openHistory():
    print("History")

def openCredits():
    print("Credits")

def quitGame():
    global running
    running = False

##themes###
theme = pyMenu.themes.THEME_DEFAULT.copy()
theme.title = False
theme.background_color = pyMenu.BaseImage("imgs\\backdrop.jpg")


###MENU###
mainMenu = pyMenu.Menu("SpaceCode", screen.get_size()[0], screen.get_size()[1], theme=theme)
selectDifficultyMenu = pyMenu.Menu("Select Difficulty", screen.get_size()[0], screen.get_size()[1], theme=theme)


##add components###
mainMenu.add.button("Play", selectDifficultyMenu)
mainMenu.add.button("History", openHistory)
mainMenu.add.button("Credits", openCredits)
mainMenu.add.button("Quit", quitGame)

selectDifficultyMenu.add.button("Easy", setDifficulty, "Easy")
selectDifficultyMenu.add.button("Medium", setDifficulty, "Medium")
selectDifficultyMenu.add.button("Hard", setDifficulty, "Hard")
selectDifficultyMenu.add.button("Back", pyMenu.events.BACK)

# ===================================== Asset Loading =====================================
imageScale = 2

assetMgr.loadTexture("background", "imgs\\backdrop.jpg")
assetMgr.loadTexture("cadet","imgs\\cadet.png")
assetMgr.loadTexture("alien","imgs\\alien.png")

# Ship
shipTex = assetMgr.loadTexture("MainShip Full","imgs\\Main Ship - Full health.png", 2)
shipRect = assetMgr.getRect("MainShip Full")
assetMgr.loadTexture("MainShip SDam","imgs\\Main Ship - Slight damage.png", 2)
assetMgr.loadTexture("MainShip Dam","imgs\\Main Ship -Damaged.png", 2)
assetMgr.loadTexture("MainShip VDam","imgs\\Main Ship - Very damaged.png", 2)

gun1Tex = assetMgr.loadTexture("AutoCannon","imgs\\Main Ship - Weapons - Auto Cannon.png", 2)
gun2Tex = assetMgr.loadTexture("BigGun","imgs\\Main Ship - Weapons - Big Space Gun.png", 2)
gun3Tex = assetMgr.loadTexture("Zapper","imgs\\Main Ship - Weapons - Zapper.png", 2)
gun4Tex = assetMgr.loadTexture("Rockets","imgs\\Main Ship - Weapons - Rockets.png", 2)


# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)
raw_background = assetMgr.getTexture("background")
background = pygame.transform.scale(raw_background, (1280, 720))



# ========================================== Get Size ======================================
backgroundRect = assetMgr.getRect("background")

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


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 1 is Left Click

                # 1. Tell the weapon to shoot and catch the projectile it creates
                bullet = player.weapon.shootLaser()

                # 2. Drop it directly into your main projectile group!
                projectile_group.add(bullet)

    # =========================================================================
    # PHASE 2: UPDATE GAME STATE (Physics & Math)
    # =========================================================================
    player.update()
    projectile_group.update()

    if currState == MENU:
        mainMenu.update(events)
        mainMenu.draw(screen)
    elif currState == DIFFICULTY_1:
        screen.blit(background, (0, 0)) # Screen first
        player.draw(screen)
        projectile_group.draw(screen)
    elif currState == DIFFICULTY_2:
        screen.blit(background, (0, 0)) # Screen first
        player.draw(screen)
        projectile_group.draw(screen)
    elif currState == DIFFICULTY_3:
        screen.blit(background, (0, 0)) # Screen first
        player.draw(screen)
        projectile_group.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()