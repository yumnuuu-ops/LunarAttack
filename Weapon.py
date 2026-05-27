import pygame
from AnimationManager import AnimationManager
from Projectile import Projectile


class Weapon:
    def __init__(self, assetMgr, x, y):
        self.selectedWeapon = "BigGun"
        animation = assetMgr.getAnim(self.selectedWeapon)
        self.animator = AnimationManager(animation, speed=0.24)
        self.image = self.animator.get_current_frame()
        self.rect = self.image.get_rect()
        self.scale = assetMgr.global_scale
        self.assetMgr = assetMgr

        self.pos = pygame.math.Vector2(x, y)

        self.fireRate = 10
        self.cooldown = 0
        self.projectileCount = 1
        self.projectileSize = 1
        self.projectileSpeed = 2

        self.damage = 10

        self.gun_map = {
            "AutoCannon": [(6, 7), (24, 7)],
            "Rockets":[(6,9), (20,9), (2,13), (24,13), (-3,17), (28,17)],
            "Zapper":[(7,3), (23,3)],
            "BigGun":[(16,0)]
        }
        self.current_barrel = 0

    def shootProjectile(self):
        # If the gun is ready to shoot
        if self.cooldown == 0:
            self.cooldown = self.fireRate

            if self.selectedWeapon == "Rockets":

                rocket_list = self.gun_map[self.selectedWeapon]

                local_x, local_y = rocket_list[self.current_barrel]

                bullet_x = self.rect.x + (local_x * self.scale)
                bullet_y = self.rect.y + (local_y * self.scale)

                new_bullet = Projectile(self.assetMgr, self.selectedWeapon, self.projectileSpeed, bullet_x, bullet_y, 0, -1, self.damage)

                self.current_barrel += 1
                if self.current_barrel >= len(rocket_list):
                    self.current_barrel = 0
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

                    new_bullet = Projectile(self.assetMgr, self.selectedWeapon, self.projectileSpeed, bullet_x, bullet_y, 0, -1, self.damage)
                    spawned_projectiles.append(new_bullet)

                return spawned_projectiles

        #  If the gun is on cooldown, return nothing
        return None

    def draw(self, surface):
        # Use its own stored self.image
        surface.blit(self.image, self.rect)

    def update(self, is_firing):
        if is_firing:
            # If pressing down, run the animation loop normally
            self.animator.update()
        else:
            # If NOT pressing down, instantly snap back to the resting frame
            self.animator.reset()
        # Grab whichever frame is active (either moving, or forced to 0)
        self.image = self.animator.get_current_frame()

        if self.cooldown > 0:
            self.cooldown -= 1