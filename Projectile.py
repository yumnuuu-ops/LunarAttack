import pygame
import utils
from AnimationManager import AnimationManager

class Projectile(pygame.sprite.Sprite):
    def __init__(self, assetMgr, selectedWeapon, speed, x, y, vx, vy, damage):
        super().__init__()
        self.assetMgr = assetMgr
        self.selectedProj = "Mass"        # AutoCannonProj    BigProj     ZapperProj    RocketProj
        animation = assetMgr.getAnim(self.selectedProj)
        self.animator = AnimationManager(animation, speed=0.24)

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

        self.ExplosiveProjectile = ["BigProjEx", "Mass", "MassX"]
        self.AfterEffect = ["MassE", "BigProjExE"]

    def moveProjectile(self):
        self.pos.x += self.vx * self.speed
        self.pos.y += self.vy * self.speed

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self):
        if self.selectedProj in self.ExplosiveProjectile:
            if self.animator.checkEndOfAnimation():
                newProj = self.selectedProj + "E"
                self.changeAnim(newProj)

            self.animator.update(False)
        elif self.selectedProj in self.AfterEffect:
            self.animator.update(False)
            if self.animator.checkEndOfAnimation():
                self.kill()
                return  # Exit early since the bullet is dead
        else:
            self.animator.update()
        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        self.moveProjectile()

        #  Check if it went off screen, kill it if it did
        if utils.is_off_screen(self.pos.x, self.pos.y):
            self.kill()

    def changeAnim(self, newProj):
        self.selectedProj = newProj
        new_frames = self.assetMgr.getAnim(self.selectedProj)
        self.animator.frames = new_frames
        self.animator.reset()



