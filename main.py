import pygame
import sys
import random
from AssetManager import AssetManager
from Player import Player

pygame.init()
pygame.font.init()
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
clock = pygame.time.Clock()
assetMgr = AssetManager(2)

# ===================================== Asset Loading =====================================
imageScale = 2

assetMgr.loadTexture("background", "imgs\\backdrop.jpg")
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
    # =========================================================================
    # PHASE 1: INPUT / EVENTS
    # =========================================================================
    for event in pygame.event.get():
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

    # =========================================================================
    # PHASE 3: DRAW (Back to Front)
    # =========================================================================
    screen.blit(background, (0, 0)) # Screen first

    player.draw(screen)
    projectile_group.draw(screen)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()