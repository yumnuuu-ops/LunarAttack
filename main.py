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
from CutScene import CutScene
from ScoreManager import ScoreManager
from HUD import HUD
from DummyEnemy import DummyEnemy # testing only
from Alien import Alien
from Formation import Formation
from BossFight import BossFight

pygame.init()
pygame.font.init()
press_start = pygame.font.Font("PressStart2P-Regular.ttf", 20)
pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
bg = Background(1280, 720)
clock = pygame.time.Clock()
assetMgr = AssetManager(2)
score_manager = ScoreManager()
dummy = DummyEnemy(screen_w, screen_h) # testing only

alien_types = ["alien_drone", "alien_drone", "alien_drone"]

SPAWN_ALIEN_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ALIEN_EVENT, 1500)

MENU, PLAY_SCREEN, CUTSCENE, STAGE_1, STAGE_2, BOSS = \
    "menu", "play_screen", "cutscene", "stage_1", "stage_2", "boss"
currState = MENU
selected_difficulty = None

EASY, MEDIUM, HARD = "easy", "medium", "hard"
currDifficulty = EASY

def setDifficulty(selected_diff):
    global currState, currDifficulty
    currDifficulty = EASY if selected_diff == "Easy" else MEDIUM if selected_diff == "Medium" else HARD
    currState = STAGE_1

def quitGame():
    global running
    running = False

theme = pyMenu.themes.THEME_DEFAULT.copy()
theme.title = False
theme.background_color = (0, 0, 0, 0)
theme.widget_font = "PressStart2P-Regular.ttf"
theme.widget_font_size = 18
theme.widget_font_color = (255, 255, 255)
theme.widget_font_shadow = True
theme.widget_font_shadow_color = (0, 100, 255)
theme.selection_color = (0, 200, 255)

mainMenu = pyMenu.Menu("SpaceCode", screen.get_size()[0], screen.get_size()[1], theme=theme)
selectDifficultyMenu = pyMenu.Menu("Select Difficulty", screen.get_size()[0], screen.get_size()[1], theme=theme)
historyMenu = pyMenu.Menu("History", screen.get_size()[0], screen.get_size()[1], theme=theme)
creditsMenu = pyMenu.Menu("Credits", screen.get_size()[0], screen.get_size()[1], theme=theme)

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

# asset loading
imageScale = 2

assetMgr.loadTexture("cadet", "imgs\\cadet.png")
assetMgr.loadTexture("alien", "imgs\\alien.png")

shipTex = assetMgr.loadTexture("MainShip Full", "imgs\\Main Ship - Full health.png")
shipRect = assetMgr.getRect("MainShip Full")
assetMgr.loadTexture("MainShip SDam", "imgs\\Main Ship - Slight damage.png")
assetMgr.loadTexture("MainShip Dam",  "imgs\\Main Ship -Damaged.png")
assetMgr.loadTexture("MainShip VDam", "imgs\\Main Ship - Very damaged.png")

gun1Anim = assetMgr.loadAnim("AutoCannon", "imgs\\Main Ship - Weapons - Auto Cannon.png")
gun2Anim = assetMgr.loadAnim("BigGun",     "imgs\\Main Ship - Weapons - Big Space Gun.png")
gun3Anim = assetMgr.loadAnim("Zapper",     "imgs\\Main Ship - Weapons - Zapper.png")
gun4Anim = assetMgr.loadAnim("Rockets",    "imgs\\Main Ship - Weapons - Rockets.png")

proj1Anim = assetMgr.loadAnim("AutoCannonProj", "imgs\\Main ship weapon - Projectile - Auto cannon bullet.png")
proj2Anim = assetMgr.loadAnim("BigProj",        "imgs\\Main ship weapon - Projectile - Big Space Gun.png")
proj5Anim = assetMgr.loadAnim("BigProjEx",      "imgs\\Main ship weapon - Projectile - Big Space Gun Ex.png")
proj3Anim = assetMgr.loadAnim("ZapperProj",     "imgs\\Main ship weapon - Projectile - Zapper.png")
proj4Anim = assetMgr.loadAnim("RocketProj",     "imgs\\Main ship weapon - Projectile - Rocket.png")

enemy1Anim = assetMgr.loadAnim("alien_drone", "Assets\\Aliens\\enemy_drone_strip.png")
attack = assetMgr.loadAnimScale("Mass", "imgs\\Mass Attack Anim.png", 4)
massExplosion = assetMgr.loadAnimScale("MassE", "imgs\\mass_implosion_strip-sheet.png", 4)
moon_phase1_idle = assetMgr.loadAnimScale("MoonP1", "Assets\\Moon\\moon_phase1_idle_strip.png", 6)
moon_phase_transition = assetMgr.loadAnimScale("MoonP1TP2", "Assets\\Moon\\moon_phase1_to_phase2_strip.png", 6)
moon_phase2_idle = assetMgr.loadAnimScale("MoonP2", "Assets\\Moon\\moon_phase2_idle_strip.png", 6)
moon_clone_spawn = assetMgr.loadAnimScale("MoonCSpawn", "Assets\\Moon\\moon_clone_spawn_strip.png", 6)
moon_clone_idle = assetMgr.loadAnimScale("MoonC", "Assets\\Moon\\moon_clone_idle_strip.png", 6)

# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)

# ========================================== Get Size ======================================
#removed for background

# ====================================== Object Creation ======================================
player = Player(assetMgr,608, 848)
font = pygame.font.SysFont('freesansbold.ttf', 20)


projectile_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
enemy_projectile_group = pygame.sprite.Group()

num_cols = 6
spacing = 100
start_x = (screen_w - (num_cols - 1) * spacing) // 2
cols = [start_x + i * spacing for i in range(num_cols)]
grid_slots = [(col, row) for row in [100, 180, 260] for col in cols]
formation = Formation(screen_w, screen_h, grid_slots)

menu = MainMenu(screen_w, screen_h)
play_screen = PlayScreen(screen_w, screen_h, score_manager)
cutscene = CutScene(screen_w, screen_h)
bossFight = BossFight(screen_w, screen_h, assetMgr, player)

# main loop
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
                slots_to_spawn = formation.get_spawn_slots()
                for slot in slots_to_spawn:
                    if slot[0] < 640:
                        spawn_x = -50
                        spawn_y = 0
                    else:
                        spawn_x = screen_w + 50
                        spawn_y = 0
                    new_alien = Alien(assetMgr, chosen_type, spawn_x, spawn_y, stage=2,
                                      target_x=slot[0], target_y=slot[1])
                    alien_group.add(new_alien)
                    formation.register_alien(new_alien, slot)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            currState = BOSS

    # their update — untouched
    if currState == STAGE_2:
        formation.update()

    player.update()

    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]:
        bullets = player.weapon.shootProjectile()
        if bullets is not None:
            projectile_group.add(*bullets)

    projectile_group.update()

    enemy_bullets = []
    for alien in alien_group:
        result = alien.update()
        if result is not None:
            enemy_bullets.append(result)
    enemy_projectile_group.add(*enemy_bullets)
    enemy_projectile_group.update()

    if currState == STAGE_2:
        dead_aliens = [alien for alien in formation.active_aliens if not alien.alive()]
        for alien in dead_aliens:
            formation.release_alien(alien)

    hits = pygame.sprite.groupcollide(projectile_group, alien_group, True, False)
    for bullet, hit_aliens in hits.items():
        for alien in hit_aliens:
            alien.takeDamage(bullet.damage)
            if alien.hp <= 0 and currState == STAGE_2:
                formation.release_alien(alien)

    # draw
    if currState == MENU:
        alien_group.empty()
        projectile_group.empty()
        enemy_projectile_group.empty()
        formation.reset()

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
            play_screen = PlayScreen(screen_w, screen_h, score_manager)
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
            selected_difficulty = play_screen.difficulty
            currState = CUTSCENE
            cutscene = CutScene(screen_w, screen_h, play_screen.player_name)
        elif play_screen.action == "BACK":
            currState = MENU
            menu.reset()

    elif currState == CUTSCENE:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        cutscene.update(events)
        cutscene.draw(screen)

        if cutscene.action == "DONE":
            currState = STAGE_1
            hud = HUD(screen_w, screen_h, play_screen.player_name, selected_difficulty)
            alien_group.empty()
            projectile_group.empty()
            enemy_projectile_group.empty()
            formation.reset()

    elif currState in [STAGE_1, STAGE_2]:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)
        projectile_group.draw(screen)

        # 3. Render the alien fleet and their incoming laser fire
        enemy_projectile_group.draw(screen)
        alien_group.draw(screen)

        if dummy.alive:
            dummy.check_hit(projectile_group)
            dummy.draw(screen)
        else:
            points = hud.register_kill(dummy.points)
            dummy.spawn()

        hud.update(dt)
        hud.draw(screen)
    elif currState == BOSS:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)
        projectile_group.draw(screen)
        bossFight.update(events)
        bossFight.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()