import pygame
import sys
import os
import random
import pygame_menu as pyMenu
from MainMenu import MainMenu
from Player import Player
from background import Background
from PlayScreen import PlayScreen
from CutScene import CutScene
from ScoreManager import ScoreManager
from HUD import HUD
from Alien import Alien
from Formation import Formation
from BossFight import BossFight
import globals as g
from globals import sound, assetMgr
import math

pygame.init()


pygame.font.init()
press_start = pygame.font.Font("PressStart2P-Regular.ttf", 20)
press_start_large = pygame.font.Font("PressStart2P-Regular.ttf", 32)
press_start_sub = pygame.font.Font("PressStart2P-Regular.ttf", 16)

pygame.display.set_caption('SpaceCode')
screen = pygame.display.set_mode((1280, 720))
game_surface = pygame.Surface((1280, 720))

# Screen Shake System
shake_intensity = 0
shake_duration = 0

def trigger_shake(intensity, duration):
    global shake_intensity, shake_duration
    shake_intensity = max(shake_intensity, intensity)
    shake_duration = max(shake_duration, duration)

screen_w, screen_h = screen.get_size()
bg = Background(1280, 720)
clock = pygame.time.Clock()
score_manager = ScoreManager()

alien_types = ["alien_drone", "tendril_alien", "tendril_alien"]

SPAWN_ALIEN_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ALIEN_EVENT, 1500)

MENU, PLAY_SCREEN, CUTSCENE, STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5, BOSS = \
    "menu", "play_screen", "cutscene", "stage_1", "stage_2", "stage_3", "stage_4", "stage_5", "boss"
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
    global currState, currDifficulty, enemies_spawned_so_far, total_enemies_to_spawn
    currDifficulty = EASY if selected_diff == "Easy" else MEDIUM if selected_diff == "Medium" else HARD
    currState = STAGE_3
    enemies_spawned_so_far = 0
    total_enemies_to_spawn = 20

def game_over():
    global currState, player
    currState = MENU
    menu.reset()
    player.health = 100
    sound.play_music("menu")

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

teleport_out_slow = assetMgr.loadAnimScale("MoonTeleSlowOut", "imgs\\moon_phase1_teleport out slow.png", 6)
teleport_out_fast = assetMgr.loadAnimScale("MoonTeleFastOut", "imgs\\moon_phase1_teleport out fast.png", 6)
teleport_in_slow = assetMgr.loadAnimScale("MoonTeleSlowIn", "imgs\\moon_phase1_teleport in slow.png", 6)
teleport_in_fast = assetMgr.loadAnimScale("MoonTeleFastIn", "imgs\\moon_phase1_teleport in fast.png", 6)

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
cols_s4 = [((screen_w - 5 * 150) // 2) + i * 150 for i in range(6)]
grid_slots_stage4 = [(col, last_y + ((5 - i if i > 2 else i) * y_spacing)) for i, col in enumerate(cols_s4)]

cols_s5 = [((screen_w - 7 * 130) // 2) + i * 130 for i in range(7)]
grid_slots_stage5 = []
# Build second row formation (closest to player - spawns first)
for i, col in enumerate(cols_s5):
    grid_slots_stage5.append((col, 2 * last_y + ((6 - i if i > 2 else i) * y_spacing)))
# Build first row formation (further away - spawns second)
for i, col in enumerate(cols_s5):
    grid_slots_stage5.append((col, last_y + ((6 - i if i > 2 else i) * y_spacing)))

formation = Formation(screen_w, screen_h, grid_slots_stage4)

menu = MainMenu(screen_w, screen_h)
menu.on_hover       = lambda: sound.play_sfx("select")
menu.on_press_start = lambda: sound.play_sfx("save_load")

play_screen = PlayScreen(screen_w, screen_h, score_manager)
play_screen.on_hover   = lambda: sound.play_sfx("select")
play_screen.on_error   = lambda: sound.play_sfx("error")
play_screen.on_confirm = lambda: sound.play_sfx("confirm")

cutscene = CutScene(screen_w, screen_h)
cutscene.on_advance = lambda: sound.play_sfx("save_load")
bossFight = BossFight(screen_w, screen_h, assetMgr, player, sound, projectile_group)

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
                if currState == STAGE_1:
                    num_to_spawn = random.randint(2, 3)
                    chosen_xs = []
                    existing_xs = [a.pos.x for a in alien_group if a.pos.y < 150]
                    for _ in range(num_to_spawn):
                        if enemies_spawned_so_far < total_enemies_to_spawn:
                            valid_x = None
                            for _ in range(20):
                                candidate_x = random.randint(100, 1180)
                                too_close = False
                                for cx in chosen_xs:
                                    if abs(candidate_x - cx) < 160:
                                        too_close = True
                                        break
                                for ex in existing_xs:
                                    if abs(candidate_x - ex) < 160:
                                        too_close = True
                                        break
                                if not too_close:
                                    valid_x = candidate_x
                                    break
                            if valid_x is None:
                                valid_x = random.randint(100, 1180)
                            chosen_xs.append(valid_x)
                            new_alien = Alien(assetMgr, "alien_drone", valid_x, -100, stage=1)
                            alien_group.add(new_alien)
                            enemies_spawned_so_far += 1
                elif currState in [STAGE_2, STAGE_3]:
                    num_to_spawn = random.choice([3, 4])
                    for idx in range(num_to_spawn):
                        if enemies_spawned_so_far < total_enemies_to_spawn:
                            # Alternate spawning between off-screen left and right boundaries!
                            if idx % 2 == 0:
                                spawn_x = -100 # Off-screen left
                            else:
                                spawn_x = 1380 # Off-screen right
                            
                            # Stagger Y coordinates off-screen down the sides
                            spawn_y = 60 + (idx * 110)
                            
                            new_alien = Alien(assetMgr, "alien_drone", spawn_x, spawn_y, stage=2 if currState == STAGE_2 else 3)
                            alien_group.add(new_alien)
                            enemies_spawned_so_far += 1
                elif currState in [STAGE_4, STAGE_5]:
                    # Spawn in a swarm! Request up to 6 slots (3 pairs) per tick
                    slots_to_spawn = []
                    for _ in range(3):
                        slots_to_spawn.extend(formation.get_spawn_slots())
                    
                    for idx, slot in enumerate(slots_to_spawn):
                        if enemies_spawned_so_far < total_enemies_to_spawn:
                            if slot[0] < 640:
                                # Stagger spawn position so they stream in beautifully without overlapping
                                spawn_x = -50 - (idx * 80)
                                spawn_y = 0
                            else:
                                # Stagger spawn position so they stream in beautifully without overlapping
                                spawn_x = screen_w + 50 + (idx * 80)
                                spawn_y = 0
                            alien_type = alien_types[1] if currState == STAGE_4 else alien_types[2]
                            new_alien = Alien(assetMgr, alien_type, spawn_x, spawn_y, stage=4 if currState == STAGE_4 else 5,
                                              target_x=slot[0], target_y=slot[1])
                            alien_group.add(new_alien)
                            formation.register_alien(new_alien, slot)
                            enemies_spawned_so_far += 1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            currState = BOSS

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            sound.play_sfx("phase 1 to 2") # phase 2 to eclipse     phase 1 to 2      eclipse to scarred

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

            player_touching_edge = (player.pos.x <= 0 or player.pos.x >= 1280 - player.rect.width)

            enemy_bullets = []
            for alien in alien_group:
                result = alien.update(player_pos=player.rect.center, player_touching_edge=player_touching_edge)
                if result is not None:
                    enemy_bullets.append(result)
                    # Satisfying micro-shake when enemy shoots
                    trigger_shake(2, 4)
            enemy_projectile_group.add(*enemy_bullets)
            enemy_projectile_group.update()

            if currState in [STAGE_4, STAGE_5]:
                dead_aliens = [alien for alien in formation.active_aliens if not alien.alive()]
                for alien in dead_aliens:
                    formation.release_alien(alien)

            ALIEN_POINTS = {"alien_drone":50,"tendril_alien":150,}

            hits = pygame.sprite.groupcollide(projectile_group, alien_group, True, False)
            for bullet, hit_aliens in hits.items():
                for alien in hit_aliens:
                    alien.takeDamage(bullet.damage)
                    trigger_shake(3, 6)
                    if alien.hp <= 0:
                        trigger_shake(8, 15)

                        hud.register_kill(ALIEN_POINTS.get(alien.alien_type,50))

                        if currState in [STAGE_4, STAGE_5]:
                            formation.release_alien(alien)

            # Player-Alien Collision Check (Kamikaze / Crashing into player!)
            collided_aliens = [alien for alien in alien_group if player.rect.colliderect(alien.rect)]
            for alien in collided_aliens:
                alien.kill()
                player.takeDamage(1) # Deduct 1 HP on crash

                hud.take_damage()

                trigger_shake(12, 25) # Trigger a dramatic screen shake!
                if currState in [STAGE_4, STAGE_5]:
                    formation.release_alien(alien)

            # Player-EnemyBullet Collision Check
            collided_bullets = [bullet for bullet in enemy_projectile_group if player.rect.colliderect(bullet.rect)]
            for bullet in collided_bullets:
                bullet.kill()
                player.takeDamage(1) # Deduct 1 HP on bullet hit

                hud.take_damage()

                trigger_shake(5, 10) # Subtle screen shake on player hit

            # Game Over Check
            if player.health <= 0:
                currState = MENU
                menu.reset()
                player.health = 100

            # Check Stage 1 clear condition
            if currState == STAGE_1 and enemies_spawned_so_far >= total_enemies_to_spawn and len(alien_group) == 0:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = STAGE_2
                transition_title = "STAGE 1 CLEAR!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()

            # Check Stage 2 clear condition
            elif currState == STAGE_2 and enemies_spawned_so_far >= total_enemies_to_spawn:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = STAGE_3
                transition_title = "STAGE 2 CLEAR!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()

            # Check Stage 3 clear condition
            elif currState == STAGE_3 and enemies_spawned_so_far >= total_enemies_to_spawn:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = STAGE_4
                transition_title = "STAGE 3 CLEAR!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()

            # Check Stage 4 clear condition
            elif currState == STAGE_4 and enemies_spawned_so_far >= total_enemies_to_spawn and len(alien_group) == 0:
                transition_active = True
                transition_timer = TRANSITION_DURATION
                transition_target_state = STAGE_5
                transition_title = "STAGE 4 CLEAR!"
                alien_group.empty()
                projectile_group.empty()
                enemy_projectile_group.empty()
                formation.reset()

            # Check Stage 5 clear condition
            elif currState == STAGE_5 and enemies_spawned_so_far >= total_enemies_to_spawn and len(alien_group) == 0:
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
            transition_timer -= g.dt
            if transition_timer <= 0:
                transition_active = False
                hud.next_wave()
                currState = transition_target_state

                # Set up the new stage config
                if currState == STAGE_2:
                    enemies_spawned_so_far = 2
                    total_enemies_to_spawn = 20
                    p1 = Alien(assetMgr, "tendril_alien", 480, 150, stage=2)
                    p1.phase = "stationary"
                    alien_group.add(p1)
                    p2 = Alien(assetMgr, "tendril_alien", 800, 150, stage=2)
                    p2.phase = "stationary"
                    alien_group.add(p2)
                elif currState == STAGE_3:
                    enemies_spawned_so_far = 2
                    total_enemies_to_spawn = 30
                    p1 = Alien(assetMgr, "tendril_alien", 480, 150, stage=3)
                    p1.phase = "stationary"
                    alien_group.add(p1)
                    p2 = Alien(assetMgr, "tendril_alien", 800, 150, stage=3)
                    p2.phase = "stationary"
                    alien_group.add(p2)
                elif currState == STAGE_4:
                    formation = Formation(screen_w, screen_h, grid_slots_stage4)
                    enemies_spawned_so_far = 0
                    total_enemies_to_spawn = 18
                elif currState == STAGE_5:
                    formation = Formation(screen_w, screen_h, grid_slots_stage5)
                    enemies_spawned_so_far = 0
                    total_enemies_to_spawn = 36

    # Clear the intermediate drawing surface
    game_surface.fill((0, 0, 0))

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

        bg.update(g.dt)
        bg.draw(game_surface, darkened=True)
        menu.update(events)
        menu.draw(game_surface)

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
        bg.update(g.dt)
        bg.draw(game_surface, darkened=True)
        play_screen.update(events)
        play_screen.draw(game_surface)

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
        bg.update(g.dt)
        bg.draw(game_surface)
        cutscene.update(events)
        cutscene.draw(game_surface)

        if cutscene.action == "DONE":
            currState = STAGE_1
            hud = HUD(screen_w, screen_h, play_screen.player_name, selected_difficulty)
            hud.on_game_over = lambda: game_over()
            sound.stop_music()
            alien_group.empty()
            projectile_group.empty()
            enemy_projectile_group.empty()
            formation.reset()
            enemies_spawned_so_far = 0
            total_enemies_to_spawn = 20

    elif currState in [STAGE_1, STAGE_2, STAGE_3, STAGE_4, STAGE_5]:
        bg.update(g.dt)
        bg.draw(game_surface)
        player.draw(game_surface)
        projectile_group.draw(game_surface)

        # 3. Render the alien fleet and their incoming laser fire
        enemy_projectile_group.draw(game_surface)
        alien_group.draw(game_surface)
        for alien in alien_group:
            if hasattr(alien, "phase") and alien.phase != "stage2_align":
                pygame.draw.rect(game_surface, (255, 0, 0), alien.rect, 1)
            # Draw blinking red Lock-On laser sights only for the stationary front enemies!
            if hasattr(alien, "phase") and alien.phase == "stationary":
                timer = alien.shoot_cooldown
                crit_threshold = 15
                warn_threshold = 40
                
                if timer <= crit_threshold:
                    # Thick solid warning beam pointing directly at the player!
                    pygame.draw.line(game_surface, (255, 0, 0), alien.rect.center, player.rect.center, 3)
                else:
                    # Blinks faster as cooldown counts down
                    blink_interval = 8 if timer > warn_threshold else 4
                    if pygame.time.get_ticks() // (blink_interval * 15) % 2 == 0:
                        pygame.draw.line(game_surface, (255, 30, 30), alien.rect.center, player.rect.center, 2)

        for proj in projectile_group:
            pygame.draw.rect(game_surface, (0, 255, 0), proj.rect, 1)

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
        bossFight.draw(game_surface)

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