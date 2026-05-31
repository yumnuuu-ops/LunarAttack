import pygame
from AnimationManager import AnimationManager
from Projectile import Projectile
from globals import soundMgr, assetMgr, projectile_group
import globals as g

class Weapon:
    def __init__(self, x, y):
        self.selectedWeapon = "AutoCannon"
        self.scale = assetMgr.global_scale
        self.assetMgr = assetMgr

        self.pos = pygame.math.Vector2(x, y)

        self.fireRate = 7
        self.projectileSpeed = 11
        self.damage = 8
        self.anim_fps = 24
        self.cooldown = 0

        animation = assetMgr.getAnim(self.selectedWeapon)
        self.animator = AnimationManager(animation, self.anim_fps)
        self.image = self.animator.get_current_frame()
        self.rect = self.image.get_rect()

        self.cooldowns = {
            "AutoCannon": 0.0,
            "Rockets": 0.0,
            "Zapper": 0.0,
            "BigGun": 0.0
        }

        self.gun_map = {
            "AutoCannon": [(6, 7), (24, 7)],
            "Rockets":[(6,9), (20,9), (2,13), (24,13), (-3,17), (28,17)],
            "Zapper":[(7,3), (23,3)],
            "BigGun":[(16,0)]
        }
        self.current_barrel = 0

    def shootProjectile(self):
        if self.selectedWeapon == "Rockets":

            rocket_list = self.gun_map[self.selectedWeapon]

            local_x, local_y = rocket_list[self.current_barrel]

            bullet_x = self.rect.x + (local_x * self.scale)
            bullet_y = self.rect.y + (local_y * self.scale)

            new_bullet = Projectile(self.selectedWeapon, self.projectileSpeed, bullet_x, bullet_y, 0, -1, self.damage)

            self.current_barrel += 1
            if self.current_barrel >= len(rocket_list):
                self.current_barrel = 0
            weapon_sfx = self.selectedWeapon + " fire"
            soundMgr.play_sfx(weapon_sfx)

            return [new_bullet]

        else:
            # This list will hold all the bullets created in this single frame
            spawned_projectiles = []
            # Look up the info from the map
            gunStartingPos = self.gun_map[self.selectedWeapon]

            for local_x, local_y in gunStartingPos:
                scaled_offset_x = local_x * self.scale
                scaled_offset_y = local_y * self.scale

                bullet_x = self.rect.x + scaled_offset_x
                bullet_y = self.rect.y + scaled_offset_y

                new_bullet = Projectile(self.selectedWeapon, self.projectileSpeed, bullet_x, bullet_y, 0, -1, self.damage)
                spawned_projectiles.append(new_bullet)
            weapon_sfx = self.selectedWeapon + " fire"
            soundMgr.play_sfx(weapon_sfx)
            return spawned_projectiles

    def draw(self, surface):
        # Use its own stored self.image
        surface.blit(self.image, self.rect)

    def update(self, is_firing, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                old_weapon = self.selectedWeapon
                if event.key == pygame.K_1:
                    self.selectedWeapon = "AutoCannon"
                    self.fireRate = 7
                    self.projectileSpeed = 11
                    self.damage = 8
                elif event.key == pygame.K_2:
                    self.selectedWeapon = "Rockets"
                    self.fireRate = 7
                    self.projectileSpeed = 14
                    self.damage = 30
                elif event.key == pygame.K_3:
                    self.selectedWeapon = "Zapper"
                    self.fireRate = 14
                    self.projectileSpeed = 15
                    self.damage = 5
                elif event.key == pygame.K_4:
                    self.selectedWeapon = "BigGun"
                    self.fireRate = 0.5
                    self.projectileSpeed = 15
                    self.damage = 60

                    animation = assetMgr.getAnim(self.selectedWeapon)
                    self.anim_fps = len(animation) * self.fireRate

                if self.selectedWeapon != old_weapon:
                    animation = assetMgr.getAnim(self.selectedWeapon)
                    self.animator = AnimationManager(animation, self.anim_fps)

        if is_firing:
            # If pressing down, run the animation loop normally
            self.animator.update()
        else:
            # If NOT pressing down, instantly snap back to the resting frame
            self.animator.reset()

        # Grab whichever frame is active (either moving, or forced to 0)
        self.image = self.animator.get_current_frame()

        for gun in self.cooldowns:
            if self.cooldowns[gun] > 0:
                self.cooldowns[gun] -= g.dt

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            if is_firing and self.cooldowns[self.selectedWeapon] <= 0:
                bullets = self.shootProjectile()
                projectile_group.add(*bullets)
                self.cooldowns[self.selectedWeapon] = 1.0 / self.fireRate