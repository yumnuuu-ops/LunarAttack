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
from SoundManager import SoundManager
from Alien import Alien
from Formation import Formation
from BossFight import BossFight
import math

pygame.init()


pygame.font.init()
press_start = pygame.font.Font("PressStart2P-Regular.ttf", 20)
press_start_large = pygame.font.Font("PressStart2P-Regular.ttf", 32)
press_start_sub = pygame.font.Font("PressStart2P-Regular.ttf", 16)

pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
screen_w, screen_h = screen.get_size()
bg = Background(1280, 720)
clock = pygame.time.Clock()
assetMgr = AssetManager(2)
score_manager = ScoreManager()
sound = SoundManager()

alien_types = ["alien_drone", "tendril_alien", "tendril_alien"]

SPAWN_ALIEN_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ALIEN_EVENT, 1500)

MENU, PLAY_SCREEN, CUTSCENE, STAGE_1, STAGE_2, STAGE_3, BOSS = \
    "menu", "play_screen", "cutscene", "stage_1", "stage_2", "stage_3", "boss"
currState = MENU
selected_difficulty = None

transition_active = False
transition_timer = 0.0
TRANSITION_DURATION = 3.0
transition_target_state = None
transition_title = ""

enemies_spawned_so_far = 0
total_enemies_to_spawn = 0

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

attack = assetMgr.loadAnimScale("Mass", "imgs\\Mass Attack Anim.png", 4)
attack2 = assetMgr.loadAnimScale("MassX", "imgs\\Mass Attack Anim X.png", 4)
massExplosion = assetMgr.loadAnimScale("MassE", "imgs\\mass_implosion_strip-sheet.png", 4)
massSpawn = assetMgr.loadAnimScale("MassSpawn", "Assets\\Mass\\mass_spawn_strip_new.png", 4)
moon_phase1_idle = assetMgr.loadAnimScale("MoonP1", "Assets\\Moon\\moon_phase1_idle_strip.png", 6)
moon_phase_transition = assetMgr.loadAnimScale("MoonP1TP2", "Assets\\Moon\\moon_phase1_to_phase2_strip.png", 6)
moon_phase2_idle = assetMgr.loadAnimScale("MoonP2", "Assets\\Moon\\moon_phase2_idle_strip.png", 6)
moon_clone_spawn = assetMgr.loadAnimScale("MoonCSpawn", "Assets\\Moon\\moon_clone_spawn_strip.png", 6)
moon_clone_idle = assetMgr.loadAnimScale("MoonC", "Assets\\Moon\\moon_clone_idle_strip.png", 6)
moon_giant_transition = assetMgr.loadAnimScale("MoonP2TG", "Assets\\Moon\\moon_phase2_to_eclipse_strip.png", 10)
moon_giant_idle = assetMgr.loadAnimScale("MoonG", "Assets\\Moon\\moon_eclipse_idle_strip.png", 10)
moon_giant_phase2_transition = assetMgr.loadAnimScale("MoonGTP2Scarred", "Assets\\Moon\\moon_eclipse_to_phase2_scarred_strip.png", 6)
moon_phase2_scarred_idle = assetMgr.loadAnimScale("MoonP2Scarred", "Assets\\Moon\\moon_phase2_scarred_idle_strip.png", 6)
assetMgr.loadAnim("alien_drone", "Assets\\Aliens\\enemy_drone_strip.png")
assetMgr.loadAnim("tendril_alien", "Assets\\Aliens\\enemy_tendril_strip.png")

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


last_y = 80
y_spacing = 20
cols_s2 = [((screen_w - 5 * 150) // 2) + i * 150 for i in range(6)]
grid_slots_stage2 = [(col, last_y + ((5 - i if i > 2 else i) * y_spacing)) for i, col in enumerate(cols_s2)]

cols_s3 = [((screen_w - 7 * 130) // 2) + i * 130 for i in range(7)]
grid_slots_stage3 = []
# Build second row formation (closest to player - spawns first)
for i, col in enumerate(cols_s3):
    grid_slots_stage3.append((col, 2 * last_y + ((6 - i if i > 2 else i) * y_spacing)))
# Build first row formation (further away - spawns second)
for i, col in enumerate(cols_s3):
    grid_slots_stage3.append((col, last_y + ((6 - i if i > 2 else i) * y_spacing)))

formation = Formation(screen_w, screen_h, grid_slots_stage2)

menu = MainMenu(screen_w, screen_h)
menu.on_hover       = lambda: sound.play_sfx("select")
menu.on_press_start = lambda: sound.play_sfx("save_load")

play_screen = PlayScreen(screen_w, screen_h, score_manager)
play_screen.on_hover   = lambda: sound.play_sfx("select")
play_screen.on_error   = lambda: sound.play_sfx("error")
play_screen.on_confirm = lambda: sound.play_sfx("confirm")

cutscene = CutScene(screen_w, screen_h)
cutscene.on_advance = lambda: sound.play_sfx("save_load")
bossFight = BossFight(screen_w, screen_h, assetMgr, player, sound)

# main loop
running = True

while running:
    dt = clock.get_time() / 1000.0
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_ALIEN_EVENT and currState in [STAGE_1, STAGE_2, STAGE_3]:
            if not transition_active:
                if currState == STAGE_1:
                    spawn_x = random.randint(50, 1230)
                    new_alien = Alien(assetMgr, alien_types[0], spawn_x, -100, stage=1)
                    alien_group.add(new_alien)
                elif currState in [STAGE_2, STAGE_3]:
                    slots_to_spawn = formation.get_spawn_slots()
                    for slot in slots_to_spawn:
                        if enemies_spawned_so_far < total_enemies_to_spawn:
                            if slot[0] < 640:
                                spawn_x = -50
                                spawn_y = 0
                            else:
                                spawn_x = screen_w + 50
                                spawn_y = 0
                            alien_type = alien_types[1] if currState == STAGE_2 else alien_types[2]
                            new_alien = Alien(assetMgr, alien_type, spawn_x, spawn_y, stage=2 if currState == STAGE_2 else 3,
                                              target_x=slot[0], target_y=slot[1])
                            alien_group.add(new_alien)
                            formation.register_alien(new_alien, slot)
                            enemies_spawned_so_far += 1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            currState = BOSS

    # update gameplay only if active and not transitioning
    if currState in [STAGE_1, STAGE_2, STAGE_3]:
        if not transition_active:
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

            if currState in [STAGE_2, STAGE_3]:
                dead_aliens = [alien for alien in formation.active_aliens if not alien.alive()]
                for alien in dead_aliens:
                    formation.release_alien(alien)

            ALIEN_POINTS = {"alien_drone":50,"tendril_alien":150,}

            hits = pygame.sprite.groupcollide(projectile_group, alien_group, True, False)
            for bullet, hit_aliens in hits.items():
                for alien in hit_aliens:
                    alien.takeDamage(bullet.damage)
                    if alien.hp <= 0:

                        hud.register_kill(ALIEN_POINTS.get(alien.alien_type,50))

                        if currState in [STAGE_2, STAGE_3]:
                            formation.release_alien(alien)

            # Check Stage 1 clear condition (20s)
            if currState == STAGE_1 and hud.wave_time >= 20.0:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = STAGE_2
                transition_title = "STAGE 1 CLEAR!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()

            # Check Stage 2 clear condition
            elif currState == STAGE_2 and enemies_spawned_so_far >= total_enemies_to_spawn and len(alien_group) == 0:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = STAGE_3
                transition_title = "STAGE 2 CLEAR!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()

            # Check Stage 3 clear condition
            elif currState == STAGE_3 and enemies_spawned_so_far >= total_enemies_to_spawn and len(alien_group) == 0:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = MENU
                transition_title = "VICTORY!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()
        else:
            # Transition active: tick timer
            transition_timer -= dt
            if transition_timer <= 0:
                transition_active = False
                hud.next_wave()
                currState = transition_target_state

                # Set up the new stage config
                if currState == STAGE_2:
                    formation = Formation(screen_w, screen_h, grid_slots_stage2)
                    enemies_spawned_so_far = 0
                    total_enemies_to_spawn = 18
                elif currState == STAGE_3:
                    formation = Formation(screen_w, screen_h, grid_slots_stage3)
                    enemies_spawned_so_far = 0
                    total_enemies_to_spawn = 36

    # draw
    if currState == MENU:
        if not sound.is_playing():
            sound.play_music("menu")
        alien_group.empty()
        projectile_group.empty()
        enemy_projectile_group.empty()
        formation.reset()
        enemies_spawned_so_far = 0
        total_enemies_to_spawn = 0

        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen, darkened=True)
        menu.update(events)
        menu.draw(screen)

        if menu.action == "PLAY":
            sound.play_sfx("save_load")
            menu.slide_out()
        elif menu.action == "HISTORY":
            sound.play_sfx("confirm")
        elif menu.action == "CREDITS":
            sound.play_sfx("confirm")
        elif menu.action == "SLIDEOUT_DONE":
            currState = PLAY_SCREEN
            play_screen = PlayScreen(screen_w, screen_h, score_manager)
            play_screen.on_hover = lambda: sound.play_sfx("select")
            play_screen.on_error = lambda: sound.play_sfx("error")
            play_screen.on_confirm = lambda: sound.play_sfx("confirm")
        elif menu.action == "QUIT":
            sound.play_sfx("back")
            running = False

    elif currState == PLAY_SCREEN:
        screen.fill((0, 0, 0))
        bg.update(dt)
        bg.draw(screen, darkened=True)
        play_screen.update(events)
        play_screen.draw(screen)

        if play_screen.action == "START":
            sound.play_sfx("save_load")
            selected_difficulty = play_screen.difficulty
            currState = CUTSCENE
            cutscene = CutScene(screen_w, screen_h, play_screen.player_name)
        elif play_screen.action == "BACK":
            sound.play_sfx("back")
            currState = MENU
            menu.reset()

    elif currState == CUTSCENE:
        bg.update(dt)
        bg.draw(screen)
        cutscene.update(events)
        cutscene.draw(screen)

        if cutscene.action == "DONE":
            currState = STAGE_1
            hud = HUD(screen_w, screen_h, play_screen.player_name, selected_difficulty)
            sound.stop_music()
            alien_group.empty()
            projectile_group.empty()
            enemy_projectile_group.empty()
            formation.reset()
            enemies_spawned_so_far = 0
            total_enemies_to_spawn = 0

    elif currState in [STAGE_1, STAGE_2, STAGE_3]:
        bg.update(dt)
        bg.draw(screen)
        player.draw(screen)
        projectile_group.draw(screen)

        # 3. Render the alien fleet and their incoming laser fire
        enemy_projectile_group.draw(screen)
        alien_group.draw(screen)
        for alien in alien_group:
            pygame.draw.rect(screen, (255, 0, 0), alien.rect, 1)
        for proj in projectile_group:
            pygame.draw.rect(screen, (0, 255, 0), proj.rect, 1)

        hud.update(dt)
        hud.draw(screen)
    elif currState == BOSS:
        dt = clock.get_time() / 1000.0
        bg.update(dt)
        bg.draw(screen)
        bossFight.update(events)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            bullets = player.weapon.shootProjectile()
            if bullets is not None:
                projectile_group.add(*bullets)
        projectile_group.update()
        player.draw(screen)
        projectile_group.draw(screen)
        bossFight.draw(screen)

    # Transition to the next stage
    if transition_active:
        print("preparing for: " + transition_target_state)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()