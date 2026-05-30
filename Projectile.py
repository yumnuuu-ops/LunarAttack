import pygame
import utils
from AnimationManager import AnimationManager
from globals import soundMgr, assetMgr

class Projectile(pygame.sprite.Sprite):
    def __init__(self, selectedWeapon, speed, x, y, vx, vy, damage):
        super().__init__()
        self.assetMgr = assetMgr
        self.selectedProj = "MoonPha2TeleSlowOut"        # AutoCannonProj    BigProj     ZapperProj    RocketProj
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

        self.selectedWeapon = selectedWeapon
        self.damage = damage

        self.ExplosiveProjectile = ["Mass"]
        self.AfterEffect = ["MassE", "MoonTeleSlowIn", "MoonTeleSlowOut", "MoonTeleFastIn", "MoonTeleFastOut"]

    def moveProjectile(self):
        self.pos.x += self.vx * self.speed
        self.pos.y += self.vy * self.speed

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self):
        if self.selectedProj in self.ExplosiveProjectile:
            if self.animator.checkEndOfAnimation():
                newProj = self.selectedProj + "E"
                self.changeAnim(newProj)
                soundMgr.play_sfx("mass despawn")
            self.animator.update(False)
        elif self.selectedProj in self.AfterEffect:
            self.animator.update(False)
        else:
            self.animator.update()

        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        self.moveProjectile()

        if self.selectedProj in self.AfterEffect and self.animator.checkEndOfAnimation():
            #self.kill()
            return

        # Check if it went off screen
        if utils.is_off_screen(self.pos.x, self.pos.y):
            self.kill()

    def changeAnim(self, newProj):
        self.selectedProj = newProj
        new_frames = self.assetMgr.getAnim(self.selectedProj)
        self.animator.frames = new_frames
        self.animator.reset()



