import pygame
import sys
import random

#is git working?
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('freesansbold.ttf', 20)

background = pygame.image.load("C:\\Users\\USER\\Desktop\\backdrop.jpg")
cadet = pygame.image.load("C:\\Users\\USER\\Desktop\\cadet.png")
alien = pygame.image.load("C:\\Users\\USER\\Desktop\\alien.png")

background = pygame.transform.scale(background, (1920, 1080))
cadet = pygame.transform.scale(cadet, (110, 102))
alien = pygame.transform.scale(alien, (150, 150))
screen = pygame.display.set_mode((1920, 1080))
background_color = (0, 128, 255)

alienrect = alien.get_rect()
cadetrect = cadet.get_rect()
backgroundrect = background.get_rect()

alienrect.center = (900, 400)

lasers = []
abilities = []

recoil = 0
recoil_strength = 8
recoil_recovery = 2

shake_timer = 0
shake_duration = 24
shake_intensity = 6
shake_offset_x = 0
shake_offset_y = 0

intro_active = True
intro_step = 0
intro_timer = 0
intro_step_duration = 40

intro_waypoints = [
    (1300, 1000),
    (1300, 900),
    (1500, 800),
    (1400, 700),
    (1300, 600),
    (1100, 700),
    (1000, 800),
    (940,  840),
    (960,  800),
]
cadetrect.center = intro_waypoints[0]
original_y = cadetrect.y

def shootLaser():
    global recoil
    laser = {
        'rect': pygame.Rect(cadetrect.centerx - 37, cadetrect.top + 20, 5, 20),
        'speed': 1
    }
    lasers.append(laser)
    laser2 = {
        'rect': pygame.Rect(cadetrect.centerx + 32, cadetrect.top + 20, 5, 20),
        'speed': 1
    }
    lasers.append(laser2)
    recoil = recoil_strength

def shootAbility():
    ability = {
        'rect': pygame.Rect(cadetrect.centerx, cadetrect.top - 30, 10, 40),
        'speed': 1
    }
    abilities.append(ability)

def moveLaser():
    for laser in lasers[:]:
        laser['speed'] += 0.7
        if laser['speed'] >= 15:
            laser['speed'] = 15
        laser['rect'].y -= int(laser['speed'])
        if laser['rect'].y < 0:
            lasers.remove(laser)

def moveAbility():
    for ability in abilities[:]:
        ability['speed'] += 0.2
        if ability['speed'] >= 10:
            ability['speed'] = 20
        ability['rect'].y -= int(ability['speed'])
        if ability['rect'].y < 0:
            abilities.remove(ability)

def applyRecoil():
    global recoil
    if recoil > 0:
        cadetrect.y += recoil
        recoil -= recoil_recovery
        if recoil < 0:
            recoil = 0
    elif cadetrect.y > original_y:
        cadetrect.y -= recoil_recovery
        if cadetrect.y < original_y:
            cadetrect.y = original_y

def applyShake():
    global shake_timer, shake_offset_x, shake_offset_y
    if shake_timer > 0:
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)
        shake_timer -= 1
    else:
        shake_offset_x = 0
        shake_offset_y = 0

def lerp(a, b, t):
    return a + (b - a) * t

def updateIntro():
    global intro_active, intro_step, intro_timer
    if not intro_active:
        return
    if intro_step >= len(intro_waypoints) - 1:
        intro_active = False
        cadetrect.center = intro_waypoints[-1]
        return
    t = intro_timer / intro_step_duration
    start = intro_waypoints[intro_step]
    end   = intro_waypoints[intro_step + 1]
    cadetrect.centerx = int(lerp(start[0], end[0], t))
    cadetrect.centery = int(lerp(start[1], end[1], t))
    intro_timer += 1
    if intro_timer >= intro_step_duration:
        intro_timer = 0
        intro_step += 1

dialogue = [
    'Today is someday', 'There are less comets than usual',
    'It is good for a galactic cruise . . .', 'LETS PUSH FORWARD!!!']
currLine = 0
diaTime = 0
diaInterval = 3000

clock = pygame.time.Clock()

def renderDialogue():
    global currLine, diaTime
    if currLine < len(dialogue):
        contentSurface = font.render(dialogue[currLine], True, (255, 0, 0))
        textRect = contentSurface.get_rect(left=0)
        screen.blit(contentSurface, textRect)
    diaTime += clock.get_time()
    if diaTime >= diaInterval:
        currLine += 1
        diaTime = 0

GameTime = 60
countDownEvent = pygame.USEREVENT + 1
pygame.time.set_timer(countDownEvent, 1000)

def displayTimer():
    TimerSurface = font.render(f"Time: {GameTime}", True, (255, 255, 255))
    TimerRect = TimerSurface.get_rect(topright=(950, 50))
    screen.blit(TimerSurface, TimerRect)
    TimerBackground = pygame.Rect(TimerRect.left - 2, TimerRect.top - 2, TimerRect.width + 2, TimerRect.height + 2)
    pygame.draw.rect(screen, (255, 255, 255), TimerBackground, 2)

pygame.display.set_caption('SpaceCode')

running = True

while running:                                          # ← everything below is INSIDE here
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not intro_active:
                shootLaser()
            elif event.key == pygame.K_r and not intro_active:
                shootAbility()
                shake_timer = shake_duration
        elif event.type == countDownEvent:
            GameTime -= 1
            if GameTime <= 0:
                GameTime = 0

    if not intro_active:                                # ← still inside while
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            cadetrect.x -= 5
        if keys[pygame.K_d]:
            cadetrect.x += 5
        if keys[pygame.K_w]:
            cadetrect.y -= 5
            if recoil == 0: original_y = cadetrect.y
        if keys[pygame.K_s]:
            cadetrect.y += 5
            if recoil == 0: original_y = cadetrect.y

    updateIntro()
    applyRecoil()
    applyShake()

    screen.fill(background_color)
    screen.blit(background, (0, 0))
    screen.blit(alien, alienrect)
    screen.blit(cadet, (cadetrect.x + shake_offset_x, cadetrect.y + shake_offset_y))

    moveLaser()
    for laser in lasers:
        pygame.draw.rect(screen, (255, 0, 0), laser['rect'])

    moveAbility()
    for ability in abilities:
        pygame.draw.rect(screen, (0, 255, 255), ability['rect'])

    renderDialogue()
    displayTimer()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()