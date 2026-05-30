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
from PauseMenu import PauseMenu
from GameOver import GameOver
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

MENU, PLAY_SCREEN, CUTSCENE, STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5, BOSS, DEATH_SCENE, END_SCENE = \
    "menu", "play_screen", "cutscene", "stage_1", "stage_2", "stage_3", "stage_4", "stage_5", "boss", "death_scene","end_cutscene"
currState = MENU
selected_difficulty = None
death_timer = 0.0

transition_active = False
transition_timer = 0.0
TRANSITION_DURATION = 3.0
transition_target_state = None
transition_title = ""

end_cutscene = None


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
    global currState, player, game_over_screen

    ShatterEffect.trigger(player, rows=6, cols=6)
    score_manager.save_run(hud.player_name, hud.score, hud.difficulty, hud.current_stage)

    game_over_screen = GameOver(screen_w, screen_h, hud.player_name, hud.score)
    game_over_screen.on_hover = lambda: soundMgr.play_sfx("select")
    game_over_screen.on_click = lambda: soundMgr.play_sfx("confirm")
    game_over_screen.open()

    currState = DEATH_SCENE

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
    assetMgr.loadAnim("BigGunProj",        "imgs\\Main ship weapon - Projectile - Big Space Gun.png")
    assetMgr.loadAnimScale("BigGunProjE",      "imgs\\Main ship weapon - Projectile - Big Space Gun Ex.png", 8)
    assetMgr.loadAnim("ZapperProj",     "imgs\\Main ship weapon - Projectile - Zapper.png")
    assetMgr.loadAnim("RocketsProj",     "imgs\\Main ship weapon - Projectile - Rocket.png")

    # Loading Boss / Eclipse Animations
    assetMgr.loadAnimScale("Mass", "imgs\\Mass Attack Anim.png", 4)
    assetMgr.loadAnimScale("MassX", "imgs\\Mass Attack Anim X.png", 4)
    assetMgr.loadAnimScale("MassSpawn", "Assets\\Mass\\mass_spawn_strip.png", 4)
    assetMgr.loadAnimScale("MassDespawn", "Assets\\Mass\\mass_implosion_strip.png", 4)
    assetMgr.loadAnimScale("CloneMassSpawn", "Assets\\Mass\\clone_mass_spawn_strip.png", 4)
    assetMgr.loadAnimScale("CloneMassDespawn", "Assets\\Mass\\clone_mass_implosion_strip.png", 4)
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
    assetMgr.loadAnim("alien_drone", "Assets\\Aliens\\enemy_spaceship.png")
    assetMgr.loadAnim("tendril_alien", "Assets\\Aliens\\enemy_tendril_strip.png")
    assetMgr.loadAnim("eye_spawn", "Assets\\Aliens\\eye_spawn.png")
    assetMgr.loadTexture("enemy_bullet", "Assets\\Aliens\\enemy_bullets.png")

    # Loading Teleport Animations
    assetMgr.loadAnimScale("MoonTeleSlowOut", "imgs\\moon_phase1_teleport out slow.png", 6)
    assetMgr.loadAnimScale("MoonTeleFastOut", "imgs\\moon_phase1_teleport out fast.png", 6)
    assetMgr.loadAnimScale("MoonTeleSlowIn", "imgs\\moon_phase1_teleport in slow.png", 6)
    assetMgr.loadAnimScale("MoonTeleFastIn", "imgs\\moon_phase1_teleport in fast.png", 6)
    assetMgr.loadAnimScale("MoonPha2TeleSlowOut", "imgs\\moon_phase2_teleport out slow.png", 6)
    assetMgr.loadAnimScale("MoonPha2TeleFastOut", "imgs\\moon_phase2_teleport out fast.png", 6)
    assetMgr.loadAnimScale("MoonPha2TeleSlowIn", "imgs\\moon_phase2_teleport in slow.png", 6)
    assetMgr.loadAnimScale("MoonPha2TeleFastIn", "imgs\\moon_phase2_teleport in fast.png", 6)
    assetMgr.loadAnimScale("MoonScarTeleSlowIn", "imgs\\moon_scarred_teleport in slow.png", 6)
    assetMgr.loadAnimScale("MoonScarTeleSlowOut", "imgs\\moon_scarred_teleport out slow.png", 6)

    # Clone Teleport Animations
    assetMgr.loadAnimScale("CMoonTeleIn", "imgs\\moon_clone_teleport in.png", 6)
    assetMgr.loadAnimScale("CMoonTeleOut", "imgs\\moon_clone_teleport out.png", 6)

    # Cutscene Boss
    assetMgr.loadAnimScale("BlackholeSpawn", "Assets\\Mass\\mass_spawn_strip.png", 12)
    assetMgr.loadAnimScale("Blackhole", "imgs\\Mass Attack Anim.png", 12)
    assetMgr.loadAnimScale("BlackholeDespawn", "Assets\\Mass\\mass_implosion_strip.png", 12)
    assetMgr.loadAnimScale("ScarToNormal", "imgs\\moon_scarred_to_normal.png", 6)

# asset loading
load_all_assets(assetMgr)

# ===================================== Initial Setting =====================================
font = pygame.font.SysFont('freesansbold.ttf', 20)


# ====================================== Object Creation ======================================
player = Player(608, 500)
player.trigger_shake = trigger_shake
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

pause_menu = PauseMenu(screen_w, screen_h)
pause_menu.on_hover = lambda: soundMgr.play_sfx("select")
pause_menu.on_click = lambda: soundMgr.play_sfx("confirm")
is_paused = False
#game over screen
game_over_screen = None

# main loop
running = True

while running:
    g.dt = clock.tick(60) / 1000.0
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_ALIEN_EVENT and currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5, BOSS]:
            if not transition_active and not is_paused:
                enemy_manager.spawn_aliens(currState)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            currState = BOSS

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            soundMgr.play_sfx("phase 1 to 2") # phase 2 to eclipse     phase 1 to 2      eclipse to scarred


        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
                is_paused = not is_paused
                if is_paused:
                    pause_menu.open()
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()



        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            name = getattr(play_screen, "player_name", "") or "Cadet"
            end_cutscene = CutScene(screen_w, screen_h, player_name=name, scenes="ending")
            end_cutscene.on_advance = lambda: soundMgr.play_sfx("save_load")
            currState = END_SCENE

    # update gameplay only if active and not transitioning
    if currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
        if not transition_active and not is_paused:
            player.update(events)

            projectile_group.update()
            particle_group.update()

            player_touching_edge = (player.pos.x <= 0 or player.pos.x >= 1280 - player.rect.width)

            enemy_manager.handle_updates_and_collisions(currState, player_touching_edge)

            # Check Stage Clear Conditions
            stage_configs = {
                STAGE_1: (STAGE_2, "STAGE 1 CLEAR!", True),
                STAGE_2: (STAGE_3, "STAGE 2 CLEAR!", True),
                STAGE_3: (STAGE_4, "STAGE 3 CLEAR!", True),
                STAGE_4: (STAGE_5, "STAGE 4 CLEAR!", True),
                STAGE_5: (BOSS, "Why have thy summoned thee me, za moon?", True),
            }

            if currState in stage_configs and currState != BOSS:
                target_state, title, require_empty = stage_configs[currState]

                if currState in [STAGE_2, STAGE_3]:
                    left_alive = enemy_manager.sentry_left and enemy_manager.sentry_left.alive()
                    right_alive = enemy_manager.sentry_right and enemy_manager.sentry_right.alive()
                    condition = not left_alive and not right_alive
                else:
                    condition = enemy_manager.enemies_spawned_so_far >= enemy_manager.total_enemies_to_spawn
                    if require_empty:
                        condition = condition and len(enemy_manager.alien_group) == 0

                if condition:
                    enemy_manager.alien_group.empty()
                    projectile_group.empty()
                    enemy_manager.enemy_projectile_group.empty()
                    enemy_manager.formation.reset()

                    hud.next_wave()
                    currState = target_state
                    enemy_manager.setup_stage_config(currState)

    elif currState == DEATH_SCENE:
        # Countdown the timer
        particle_group.update()
        enemy_manager.enemy_projectile_group.update()
        game_over_screen.update(g.dt, events)

        if game_over_screen.action == "PLAY_AGAIN":
            currState = PLAY_SCREEN
            player.hp = 100

            play_screen = PlayScreen(screen_w, screen_h, score_manager)
            play_screen.on_hover = lambda: soundMgr.play_sfx("select")
            play_screen.on_error = lambda: soundMgr.play_sfx("error")
            play_screen.on_confirm = lambda: soundMgr.play_sfx("confirm")
            soundMgr.play_music("menu")

        elif game_over_screen.action == "MENU":
            currState = MENU
            menu.reset()
            menu.reset()
            player.hp = 100 #think of this as resetting player health to full health
            soundMgr.play_music("menu")

    elif currState == BOSS:
        bg.update(g.dt)

        if not is_paused:
            player.update(events)
            bg.update(g.dt)
            bossFight.update(events)
            projectile_group.update()
            hud.update(g.dt)

        if bossFight.finished:
            currState = END_SCENE
            name = getattr(play_screen, "player_name", "") or "Cadet"
            end_cutscene = CutScene(screen_w, screen_h, player_name=name, scenes="ending")
            end_cutscene.on_advance = lambda: soundMgr.play_sfx("save_load")

    elif currState == END_SCENE:
        end_cutscene.update(events)
        if end_cutscene.action == "DONE":
            currState = MENU
            menu.reset()
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
            bossFight.hud = hud
            soundMgr.stop_music()
            enemy_manager.alien_group.empty()
            projectile_group.empty()
            enemy_manager.enemy_projectile_group.empty()
            enemy_manager.formation.reset()
            enemy_manager.enemies_spawned_so_far = 0
            enemy_manager.total_enemies_to_spawn = 20



    elif currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
        bg.update(g.dt)
        # Always draw (so pause menu has a frozen game behind it)
        bg.draw(game_surface)
        player.draw(game_surface)
        projectile_group.draw(game_surface)
        particle_group.draw(game_surface)
        for proj in projectile_group:
            pygame.draw.rect(game_surface, (0, 255, 0), proj.rect, 1)
        for alien in enemy_manager.alien_group:
            pygame.draw.rect(game_surface, (255, 0, 0), alien.rect, 1)
        for e_proj in enemy_manager.enemy_projectile_group:
            pygame.draw.rect(game_surface, (255, 128, 0), e_proj.rect, 1)
        enemy_manager.draw(game_surface, currState)
        # Only update/advance logic when not paused

        if not is_paused:

            hud.update(g.dt)

    elif currState == BOSS:
        bg.draw(game_surface)
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
#PLEASE TIE THIS TO DEATH OF BOSS LATER
    elif currState == END_SCENE:
        bg.update(g.dt)
        bg.draw(game_surface)
        end_cutscene.draw(game_surface)

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
    #print(f"game_surface color at center: {game_surface.get_at((640, 360))}")
    screen.blit(game_surface, (shake_offset_x, shake_offset_y))

    # Render HUD statically on top of the shook screen
    if currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5, BOSS]:
        hud.draw(screen)

    if currState == DEATH_SCENE and game_over_screen is not None:
        game_over_screen.draw(screen)

    # Transition to the next stage
    if transition_active:
        print("preparing for: " + transition_target_state)

    if is_paused:
        pause_menu.update(events)
        pause_menu.draw(screen)


        if pause_menu.action == "RESUME":
            is_paused = False
            pygame.mixer.music.unpause()
        elif pause_menu.action == "RESTART":
            is_paused = False
            transition_active = False
            transition_timer = 0.0
            currState = STAGE_1
            hud = HUD(screen_w, screen_h, play_screen.player_name, selected_difficulty)
            hud.on_game_over = lambda: game_over()
            enemy_manager.hud = hud
            bossFight.hud = hud
            enemy_manager.alien_group.empty()
            projectile_group.empty()
            enemy_manager.enemy_projectile_group.empty()
            enemy_manager.formation.reset()
            enemy_manager.enemies_spawned_so_far = 0
            enemy_manager.total_enemies_to_spawn = 20
            player.hp = 100
            pygame.mixer.music.unpause()

        elif pause_menu.action == "MENU":
            is_paused = False
            soundMgr.stop_music()
            currState = MENU
            menu.reset()
            player.hp = 100
            soundMgr.play_music("menu")

        elif  pause_menu.action == "QUIT":
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()