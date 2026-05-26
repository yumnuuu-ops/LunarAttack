import pygame
import sys
import random
import pygame_menu as pyMenu
from AssetManager import AssetManager
from Player import Player
from background import Background

pygame.init()
pygame.font.init()
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
bg = Background(1280, 720)
clock = pygame.time.Clock()
assetMgr = AssetManager(2)


#states
MENU, DIFFICULTY_1, DIFFICULTY_2, DIFFICULTY_3 = "menu", "difficulty_1", "difficulty_2", "difficulty_3"
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
theme.background_color = pyMenu.BaseImage("imgs\\backdrop.jpg")


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

gun1Anim = assetMgr.loadAnim("AutoCannon","imgs\\Main Ship - Weapons - Auto Cannon.png")
gun2Anim = assetMgr.loadAnim("BigGun","imgs\\Main Ship - Weapons - Big Space Gun.png")
gun3Anim = assetMgr.loadAnim("Zapper","imgs\\Main Ship - Weapons - Zapper.png")
gun4Anim = assetMgr.loadAnim("Rockets","imgs\\Main Ship - Weapons - Rockets.png")

proj1Anim =  assetMgr.loadAnim("AutoCannonProj", "imgs\\Main ship weapon - Projectile - Auto cannon bullet.png")
proj2Anim =  assetMgr.loadAnim("BigProj", "imgs\\Main ship weapon - Projectile - Big Space Gun.png")
proj5Anim =  assetMgr.loadAnim("BigProjEx", "imgs\\Main ship weapon - Projectile - Big Space Gun Ex.png")
proj3Anim =  assetMgr.loadAnim("ZapperProj", "imgs\\Main ship weapon - Projectile - Zapper.png")
proj4Anim =  assetMgr.loadAnim("RocketProj", "imgs\\Main ship weapon - Projectile - Rocket.png")


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

    # =========================================================================
    # PHASE 2: UPDATE GAME STATE (Physics & Math)
    # =========================================================================
    player.update()

    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]:  # 0 is Left Click held down
        # Spawn a bullet
        bullets = player.weapon.shootProjectile()
        if bullets is not None:
            projectile_group.add(*bullets)

    projectile_group.update()

    if currState == MENU:
        mainMenu.update(events)
        mainMenu.draw(screen)
    elif currState == DIFFICULTY_1:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)  # 2. player ON TOP
        projectile_group.draw(screen)
    elif currState == DIFFICULTY_2:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)  # 2. player ON TOP
        projectile_group.draw(screen)
    elif currState == DIFFICULTY_3:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)  # 2. player ON TOP
        projectile_group.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()