import pygame
import sys
import random
import pygame_menu as pyMenu
from AssetManager import AssetManager
from Player import Player
from background import Background
from Alien import Alien
from Formation import Formation

pygame.init()
pygame.font.init()
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
bg = Background(1280, 720)
clock = pygame.time.Clock()
assetMgr = AssetManager(2)

# 1. Define your alien types matching your AssetManager textures
alien_types = ["alien_drone", "alien_drone", "alien_drone"]

# Custom events for spawning aliens (Chicken Invaders style!)
SPAWN_ALIEN_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ALIEN_EVENT, 1500) # Spawns a mini-alien every 1.5 seconds




# Game States (Stages represent levels/stages that we progress through)
MENU, STAGE_1, STAGE_2 = "menu", "stage_1", "stage_2"
currState = MENU

# Difficulty variables (Currently empty - reserved for future implementation)
EASY, MEDIUM, HARD = "easy", "medium", "hard"
currDifficulty = EASY

def setDifficulty(selected_diff):
    global currState, currDifficulty
    currDifficulty = EASY if selected_diff == "Easy" else MEDIUM if selected_diff == "Medium" else HARD
    
    # Decoupled stage start: every difficulty starts at STAGE_1!
    currState = STAGE_1

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
# assetMgr.loadTexture("alien_drone", "Assets\\Aliens\\enemy_drone_f0.png")


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

enemy1Anim = assetMgr.loadAnim("alien_drone", "Assets\\Aliens\\enemy_drone_strip.png")
attack = assetMgr.loadAnim("Mass", "imgs\\Mass Attack Anim.png")

# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)

# ========================================== Get Size ======================================
#removed for background

# ====================================== Object Creation ======================================
player = Player(assetMgr,608, 848)
projectile_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
enemy_projectile_group = pygame.sprite.Group()

# GRID OF RECTANGLES FOR ENEMY FORMATION
num_cols = 6
spacing = 100
start_x = (screen_w - (num_cols - 1) * spacing) // 2
cols = [start_x + i * spacing for i in range(num_cols)]

grid_slots = [(col, row) for row in [100, 180, 260] for col in cols]
formation = Formation(screen_w, screen_h, grid_slots)

# ======================================== Main loop =======================================
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_ALIEN_EVENT and currState in [STAGE_1, STAGE_2]:
            chosen_type = random.choice(alien_types)
            if currState == STAGE_1:
                spawn_x = random.randint(50, 1230)
                new_alien = Alien(assetMgr, chosen_type, spawn_x, -100, stage=1)
                alien_group.add(new_alien)
            elif currState == STAGE_2:
                # 1. Collect up to two slots (one from the left, one from the right)
                slots_to_spawn = formation.get_spawn_slots()
                
                # 2. Spawn all selected slots in the same frame (parallel execution)
                for slot in slots_to_spawn:
                    if slot[0] < 640:
                        spawn_x = -50
                        spawn_y = 0
                    else:
                        spawn_x = screen_w + 50
                        spawn_y = 0
                        
                    new_alien = Alien(assetMgr, chosen_type, spawn_x, spawn_y, stage=2, target_x=slot[0], target_y=slot[1])
                    alien_group.add(new_alien)
                    formation.register_alien(new_alien, slot)


    # =========================================================================
    # PHASE 2: UPDATE GAME STATE (Physics & Math)
    # =========================================================================
    if currState == STAGE_2:
        formation.update()

    player.update()

    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]:  # 0 is Left Click held down
        # Spawn a bullet
        bullets = player.weapon.shootProjectile()
        if bullets is not None:
            projectile_group.add(*bullets)

    projectile_group.update()
    
    # Update alien_group and collect any fired enemy bullets
    enemy_bullets = []
    for alien in alien_group:
        result = alien.update()
        if result is not None:
            enemy_bullets.append(result)
    enemy_projectile_group.add(*enemy_bullets)
    enemy_projectile_group.update()

    # Clean up recycled slot tracker if any alien dies/gets killed off screen (Stage 2 only)
    if currState == STAGE_2:
        dead_aliens = [alien for alien in formation.active_aliens if not alien.alive()]
        for alien in dead_aliens:
            formation.release_alien(alien)

    # Bullet-alien collisions
    hits = pygame.sprite.groupcollide(projectile_group, alien_group, True, False)
    for bullet, hit_aliens in hits.items():
        for alien in hit_aliens:
            alien.takeDamage(bullet.damage)
            if alien.hp <= 0 and currState == STAGE_2: # If killed, return slot (Stage 2 only)
                formation.release_alien(alien)

    # =========================================================================
    # PHASE 3: DRAW (Back to Front)
    # =========================================================================

    if currState == MENU:
        # Clear groups when on menu to reset the level state clean
        alien_group.empty()
        projectile_group.empty()
        enemy_projectile_group.empty()
        formation.reset()
        
        mainMenu.update(events)
        mainMenu.draw(screen)
    elif currState in [STAGE_1, STAGE_2]:
        # 1. Update and render the scrolling space background
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        
        # 2. Render friendly lasers and the player ship on top
        player.draw(screen)  # 2. player ON TOP
        projectile_group.draw(screen)

        # 3. Render the alien fleet and their incoming laser fire
        enemy_projectile_group.draw(screen)
        alien_group.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()