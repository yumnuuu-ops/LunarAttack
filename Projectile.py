import pygame
import utils
from AnimationManager import AnimationManager
from globals import soundMgr, assetMgr, projectile_group

class Projectile(pygame.sprite.Sprite):
    def __init__(self, selectedWeapon, speed, x, y, vx, vy, damage):
        super().__init__()
        self.assetMgr = assetMgr
        self.selectedProj = selectedWeapon + "Proj"        # AutoCannonProj    BigProj     ZapperProj    RocketsProj
        animation = assetMgr.getAnim(self.selectedProj)
        self.animator = AnimationManager(animation, 24)

        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        self.rect = self.image.get_rect()
        self.scale = assetMgr.global_scale

        # calculate to align projectile with the gun pos passed in
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.damage = damage

        self.ExplosiveProjectile = ["BigGunProj"]

    def moveProjectile(self):
        self.pos.x += self.vx * self.speed
        self.pos.y += self.vy * self.speed

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self):
        self.animator.update()

        if self.selectedProj in self.ExplosiveProjectile and self.animator.checkEndOfAnimation():
            self.detonate()
            return

        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        self.moveProjectile()

        # Check if it went off screen
        if utils.is_off_screen(self.pos.x, self.pos.y):
            self.kill()

    def changeAnim(self, newProj):
        self.selectedProj = newProj
        new_frames = self.assetMgr.getAnim(self.selectedProj)
        self.animator.frames = new_frames
        self.animator.reset()

    def detonate(self):
        splash_damage = 20

        explosion = Explosion(self.pos.x, self.pos.y, self.selectedProj + "E", splash_damage)
        projectile_group.add(explosion)

        soundMgr.play_sfx("BigGunProj explosion")
        self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_name, damage):
        super().__init__()
        self.is_explosion = True
        self.damage = damage
        self.damaged_enemies = set()  # Prevents damaging the same alien every single frame

        self.animator = AnimationManager(assetMgr.getAnim(anim_name), 24)

        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))

    def update(self):
        self.animator.update()

        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        if self.animator.checkEndOfAnimation():
            self.kill()
