import pygame
import sys
import os
import random
from MainMenu import MainMenu
from Player import Player
from background import Background
from PlayScreen import PlayScreen
from CutScene import CutScene
from ScoreManager import ScoreManager
from HUD import HUD
from BossFight import BossFight
from enemy.EnemyManager import EnemyManager
from ShatterEffect import ShatterEffect
import globals as g
from globals import soundMgr, assetMgr, particle_group, projectile_group
import math

pygame.init()


pygame.font.init()
press_start = pygame.font.Font("PressStart2P-Regular.ttf", 20)
press_start_large = pygame.font.Font("PressStart2P-Regular.ttf", 32)
press_start_sub = pygame.font.Font("PressStart2P-Regular.ttf", 16)

pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
game_surface = pygame.Surface((1280, 720))

screen_w, screen_h = screen.get_size()
bg = Background(1280, 720)
clock = pygame.time.Clock()
score_manager = ScoreManager()

alien_types = ["alien_drone", "tendril_alien", "tendril_alien"]

SPAWN_ALIEN_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ALIEN_EVENT, 1500)

MENU, PLAY_SCREEN, CUTSCENE, STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5, BOSS, DEATH_SCENE = \
    "menu", "play_screen", "cutscene", "stage_1", "stage_2", "stage_3", "stage_4", "stage_5", "boss", "death_scene"
currState = MENU
selected_difficulty = None
death_timer = 0.0

transition_active = False
transition_timer = 0.0
TRANSITION_DURATION = 3.0
transition_target_state = None
transition_title = ""


# Screen Shake System
shake_intensity = 0
shake_duration = 0

def trigger_shake(intensity, duration):
    global shake_intensity, shake_duration
    shake_intensity = max(shake_intensity, intensity)
    shake_duration = max(shake_duration, duration)

EASY, MEDIUM, HARD = "easy", "medium", "hard"
currDifficulty = EASY

def setDifficulty(selected_diff):
    global currState, currDifficulty
    currDifficulty = EASY if selected_diff == "Easy" else MEDIUM if selected_diff == "Medium" else HARD
    currState = STAGE_3
    enemy_manager.enemies_spawned_so_far = 0
    enemy_manager.total_enemies_to_spawn = 20

def game_over():
    global currState, player, death_timer

    ShatterEffect.trigger(player, rows=6, cols=6)

    currState = DEATH_SCENE
    death_timer = 2.0

def quitGame():
    global running
    running = False


def load_all_assets(assetMgr):
    # Loading Ship Textures
    assetMgr.loadTexture("MainShip Full", "imgs\\Main Ship - Full health.png")
    assetMgr.loadTexture("MainShip SDam", "imgs\\Main Ship - Slight damage.png")
    assetMgr.loadTexture("MainShip Dam",  "imgs\\Main Ship -Damaged.png")
    assetMgr.loadTexture("MainShip VDam", "imgs\\Main Ship - Very damaged.png")

    # Loading Ship Weapon Animations
    assetMgr.loadAnim("AutoCannon", "imgs\\Main Ship - Weapons - Auto Cannon.png")
    assetMgr.loadAnim("BigGun",     "imgs\\Main Ship - Weapons - Big Space Gun.png")
    assetMgr.loadAnim("Zapper",     "imgs\\Main Ship - Weapons - Zapper.png")
    assetMgr.loadAnim("Rockets",    "imgs\\Main Ship - Weapons - Rockets.png")

    # Loading Projectile Animations
    assetMgr.loadAnim("AutoCannonProj", "imgs\\Main ship weapon - Projectile - Auto cannon bullet.png")
    assetMgr.loadAnim("BigProj",        "imgs\\Main ship weapon - Projectile - Big Space Gun.png")
    assetMgr.loadAnim("BigProjEx",      "imgs\\Main ship weapon - Projectile - Big Space Gun Ex.png")
    assetMgr.loadAnim("ZapperProj",     "imgs\\Main ship weapon - Projectile - Zapper.png")
    assetMgr.loadAnim("RocketProj",     "imgs\\Main ship weapon - Projectile - Rocket.png")

    # Loading Boss / Eclipse Animations
    assetMgr.loadAnimScale("Mass", "imgs\\Mass Attack Anim.png", 4)
    assetMgr.loadAnimScale("MassX", "imgs\\Mass Attack Anim X.png", 4)
    assetMgr.loadAnimScale("MassE", "imgs\\mass_implosion_strip-sheet.png", 4)
    assetMgr.loadAnimScale("MassSpawn", "Assets\\Mass\\mass_spawn_strip_new.png", 4)
    assetMgr.loadAnimScale("MoonP1", "Assets\\Moon\\moon_phase1_idle_strip.png", 6)
    assetMgr.loadAnimScale("MoonP1TP2", "Assets\\Moon\\moon_phase1_to_phase2_strip.png", 6)
    assetMgr.loadAnimScale("MoonP2", "Assets\\Moon\\moon_phase2_idle_strip.png", 6)
    assetMgr.loadAnimScale("MoonCSpawn", "Assets\\Moon\\moon_clone_spawn_strip.png", 6)
    assetMgr.loadAnimScale("MoonC", "Assets\\Moon\\moon_clone_idle_strip.png", 6)
    assetMgr.loadAnimScale("MoonP2TG", "Assets\\Moon\\moon_phase2_to_eclipse_strip.png", 10)
    assetMgr.loadAnimScale("MoonG", "Assets\\Moon\\moon_eclipse_idle_strip.png", 10)
    assetMgr.loadAnimScale("MoonGTP2Scarred", "Assets\\Moon\\moon_eclipse_to_phase2_scarred_strip.png", 6)
    assetMgr.loadAnimScale("MoonP2Scarred", "Assets\\Moon\\moon_phase2_scarred_idle_strip.png", 6)

    # Loading Enemy Animations & Bullets
    assetMgr.loadAnim("alien_drone", "Assets\\Aliens\\enemy_drone_strip.png")
    assetMgr.loadAnim("tendril_alien", "Assets\\Aliens\\enemy_tendril_strip.png")
    assetMgr.loadTexture("enemy_bullet", "Assets\\Aliens\\enemy_bullets.png")

    # Loading Teleport Animations
    assetMgr.loadAnimScale("MoonTeleSlowOut", "imgs\\moon_phase1_teleport out slow.png", 6)
    assetMgr.loadAnimScale("MoonTeleFastOut", "imgs\\moon_phase1_teleport out fast.png", 6)
    assetMgr.loadAnimScale("MoonTeleSlowIn", "imgs\\moon_phase1_teleport in slow.png", 6)
    assetMgr.loadAnimScale("MoonTeleFastIn", "imgs\\moon_phase1_teleport in fast.png", 6)

# asset loading
imageScale = 2
load_all_assets(assetMgr)

# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)

# ========================================== Get Size ======================================
#removed for background

# ====================================== Object Creation ======================================
player = Player(608, 948)
font = pygame.font.SysFont('freesansbold.ttf', 20)

enemy_manager = EnemyManager(player, None, screen_w, screen_h, trigger_shake)

menu = MainMenu(screen_w, screen_h)
menu.on_hover       = lambda: soundMgr.play_sfx("select")
menu.on_press_start = lambda: soundMgr.play_sfx("save_load")

play_screen = PlayScreen(screen_w, screen_h, score_manager)
play_screen.on_hover   = lambda: soundMgr.play_sfx("select")
play_screen.on_error   = lambda: soundMgr.play_sfx("error")
play_screen.on_confirm = lambda: soundMgr.play_sfx("confirm")

cutscene = CutScene(screen_w, screen_h)
cutscene.on_advance = lambda: soundMgr.play_sfx("save_load")
bossFight = BossFight(screen_w, screen_h, player)

# main loop
running = True

while running:
    g.dt = clock.tick(60) / 1000.0
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_ALIEN_EVENT and currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
            if not transition_active:
                enemy_manager.spawn_aliens(currState)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            currState = BOSS

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            soundMgr.play_sfx("phase 1 to 2") # phase 2 to eclipse     phase 1 to 2      eclipse to scarred

    # update gameplay only if active and not transitioning
    if currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
        if not transition_active:
            player.update()

            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                bullets = player.weapon.shootProjectile()
                if bullets is not None:
                    projectile_group.add(*bullets)

            projectile_group.update()
            particle_group.update()

            player_touching_edge = (player.pos.x <= 0 or player.pos.x >= 1280 - player.rect.width)

            enemy_manager.handle_updates_and_collisions(currState, player_touching_edge)

            # Game Over Check
            if player.hp <= 0:
                game_over()

            # Check Stage Clear Conditions
            stage_configs = {
                STAGE_1: (STAGE_2, "STAGE 1 CLEAR!", True),
                STAGE_2: (STAGE_3, "STAGE 2 CLEAR!", False),
                STAGE_3: (STAGE_4, "STAGE 3 CLEAR!", False),
                STAGE_4: (STAGE_5, "STAGE 4 CLEAR!", True),
                STAGE_5: (MENU, "VICTORY!", True)
            }

            if currState in stage_configs:
                target_state, title, require_empty = stage_configs[currState]
                condition = enemy_manager.enemies_spawned_so_far >= enemy_manager.total_enemies_to_spawn
                if require_empty:
                    condition = condition and len(enemy_manager.alien_group) == 0
                
                if condition:
                    transition_active = True
                    transition_timer = TRANSITION_DURATION
                    transition_target_state = target_state
                    transition_title = title
                    enemy_manager.alien_group.empty()
                    projectile_group.empty()
                    enemy_manager.enemy_projectile_group.empty()
                    enemy_manager.formation.reset()
        else:
            # Transition active: tick timer
            transition_timer -= g.dt
            if transition_timer <= 0:
                transition_active = False
                hud.next_wave()
                currState = transition_target_state

                # Set up the new stage config
                enemy_manager.setup_stage_config(currState)

    elif currState == DEATH_SCENE:
        # Countdown the timer
        death_timer -= g.dt

        particle_group.update()
        enemy_manager.enemy_projectile_group.update()

        # Once time runs out, clean up and head to the menu
        if death_timer <= 0:
            currState = MENU
            menu.reset()
            player.hp = 100
            soundMgr.play_music("menu")

    # Clear the intermediate drawing surface
    game_surface.fill((0, 0, 0))

    # draw
    if currState == MENU:
        if not soundMgr.is_playing():
            soundMgr.play_music("menu")
        enemy_manager.alien_group.empty()
        projectile_group.empty()
        particle_group.empty()
        enemy_manager.enemy_projectile_group.empty()
        enemy_manager.formation.reset()
        enemy_manager.enemies_spawned_so_far = 0
        enemy_manager.total_enemies_to_spawn = 0

        bg.update(g.dt)
        bg.draw(game_surface, darkened=True)
        menu.update(events)
        menu.draw(game_surface)

        if menu.action == "PLAY":
            soundMgr.play_sfx("save_load")
            menu.slide_out()
        elif menu.action == "HISTORY":
            soundMgr.play_sfx("confirm")
        elif menu.action == "CREDITS":
            soundMgr.play_sfx("confirm")
        elif menu.action == "SLIDEOUT_DONE":
            currState = PLAY_SCREEN
            play_screen = PlayScreen(screen_w, screen_h, score_manager)
            play_screen.on_hover = lambda: soundMgr.play_sfx("select")
            play_screen.on_error = lambda: soundMgr.play_sfx("error")
            play_screen.on_confirm = lambda: soundMgr.play_sfx("confirm")
        elif menu.action == "QUIT":
            soundMgr.play_sfx("back")
            running = False

    elif currState == PLAY_SCREEN:
        bg.update(g.dt)
        bg.draw(game_surface, darkened=True)
        play_screen.update(events)
        play_screen.draw(game_surface)

        if play_screen.action == "START":
            soundMgr.play_sfx("save_load")
            selected_difficulty = play_screen.difficulty
            currState = CUTSCENE
            cutscene = CutScene(screen_w, screen_h, play_screen.player_name)
        elif play_screen.action == "BACK":
            soundMgr.play_sfx("back")
            currState = MENU
            menu.reset()

    elif currState == CUTSCENE:
        bg.update(g.dt)
        bg.draw(game_surface)
        cutscene.update(events)
        cutscene.draw(game_surface)

        if cutscene.action == "DONE":
            currState = STAGE_1
            hud = HUD(screen_w, screen_h, play_screen.player_name, selected_difficulty)
            hud.on_game_over = lambda: game_over()
            enemy_manager.hud = hud
            soundMgr.stop_music()
            enemy_manager.alien_group.empty()
            projectile_group.empty()
            enemy_manager.enemy_projectile_group.empty()
            enemy_manager.formation.reset()
            enemy_manager.enemies_spawned_so_far = 0
            enemy_manager.total_enemies_to_spawn = 20

    elif currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
        bg.update(g.dt)
        bg.draw(game_surface)
        player.draw(game_surface)
        projectile_group.draw(game_surface)
        particle_group.draw(game_surface)

        # 3. Render the alien fleet, lasers, and target indicators
        enemy_manager.draw(game_surface, currState)


        hud.update(g.dt)

    elif currState == BOSS:
        bg.update(g.dt)
        bg.draw(game_surface)
        bossFight.update(events)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            bullets = player.weapon.shootProjectile()
            if bullets is not None:
                projectile_group.add(*bullets)
        projectile_group.update()
        player.draw(game_surface)
        projectile_group.draw(game_surface)
        particle_group.draw(game_surface)
        bossFight.draw(game_surface)

    elif currState == DEATH_SCENE:
        bg.update(g.dt)
        bg.draw(game_surface)

        enemy_manager.draw(game_surface, currState)
        enemy_manager.enemy_projectile_group.draw(game_surface)

        particle_group.draw(game_surface)

        # Draw GAME OVER at center of the screen
        text_surf = press_start_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = text_surf.get_rect(center=(screen_w // 2, screen_h // 2))
        game_surface.blit(text_surf, text_rect)

    # Process and Blit Screen Shake
    shake_offset_x = 0
    shake_offset_y = 0
    if shake_duration > 0:
        shake_duration -= 1
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)
        if shake_duration == 0:
            shake_intensity = 0

    screen.fill((0, 0, 0))
    screen.blit(game_surface, (shake_offset_x, shake_offset_y))

    # Render HUD statically on top of the shook screen
    if currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
        hud.draw(screen)

    # Transition to the next stage
    if transition_active:
        print("preparing for: " + transition_target_state)


    pygame.display.flip()

pygame.quit()
sys.exit()