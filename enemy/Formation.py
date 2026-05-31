# Formation.py
import pygame

class Formation:
    def __init__(self, screen_w, screen_h, slot_coordinates):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.base_slots = slot_coordinates
        
        self.available_slots = [] #(col, row)
        self.active_aliens = {} # alien: (col, row)
        self.cooldown_slots = [] # (slot, end_time)
        self.reset()

    def reset(self):
        self.available_slots.clear()
        self.active_aliens.clear()
        self.cooldown_slots.clear()
        self.available_slots.extend(self.base_slots)

    def get_spawn_slots(self, boundary_x=640):
        #put expired slots back into available
        now = pygame.time.get_ticks()
        expired = [item for item in self.cooldown_slots if now >= item[1]]
        for item in expired:
            self.available_slots.append(item[0])
            self.cooldown_slots.remove(item)

        claimed = []
        
        # find left slot
        left = None
        for s in self.available_slots:
            if s[0] < boundary_x:
                left = s
                break
        if left:
            self.available_slots.remove(left)
            claimed.append(left)
            
        # find right slot
        right = None
        for s in self.available_slots:
            if s[0] >= boundary_x:
                right = s
                break
        if right:
            self.available_slots.remove(right)
            claimed.append(right)
            
        # no symmetric slots
        if not claimed and self.available_slots:
            claimed.append(self.available_slots.pop(0))
            
        return claimed

    def register_alien(self, alien, slot):
        self.active_aliens[alien] = slot

    def release_alien(self, alien):
        if alien in self.active_aliens:
            slot = self.active_aliens.pop(alien)
            # 3 second delay
            cooldown_until = pygame.time.get_ticks() + 3000
            self.cooldown_slots.append((slot, cooldown_until))
