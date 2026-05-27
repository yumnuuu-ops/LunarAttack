# Formation.py
import pygame
import random

class Formation:
    def __init__(self, screen_w, screen_h, slot_coordinates):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        # Base layout coordinates defined externally
        self.base_slots = slot_coordinates
        
        # The pool of unoccupied slots
        self.available_slots = []
        # Mapping of active Alien -> base slot coordinate (col, row)
        self.active_aliens = {}
        
        # Group swaying state (like Galaga/Space Invaders)
        self.x_offset = 0
        self.sway_speed = 0.5
        self.sway_direction = 1 # 1 = right, -1 = left
        self.max_sway = 40
        
        self.reset()

    def reset(self):
        """Clears all active assignments and rebuilds all slots."""
        self.available_slots.clear()
        self.active_aliens.clear()
        self.available_slots.extend(self.base_slots)

    def get_spawn_slots(self, boundary_x=640):
        """
        Finds and returns up to two symmetric slots (one left, one right).
        Falls back to a single slot if symmetric slots aren't available.
        """
        claimed = []
        
        # 1. Look for a left slot (x < boundary_x)
        left = next((s for s in self.available_slots if s[0] < boundary_x), None)
        if left:
            self.available_slots.remove(left)
            claimed.append(left)
            
        # 2. Look for a right slot (x >= boundary_x)
        right = next((s for s in self.available_slots if s[0] >= boundary_x), None)
        if right:
            self.available_slots.remove(right)
            claimed.append(right)
            
        # Fallback: if we couldn't find symmetric slots but some slots remain, take one
        if not claimed and self.available_slots:
            claimed.append(self.available_slots.pop(0))
            
        return claimed

    def register_alien(self, alien, slot):
        """Assigns an alien to a specific base slot."""
        self.active_aliens[alien] = slot

    def release_alien(self, alien):
        """Returns the slot occupied by the alien back to the available pool."""
        if alien in self.active_aliens:
            slot = self.active_aliens.pop(alien)
            self.available_slots.append(slot)

    def update(self):
        """
        Updates the formation's offset over time.
        Updates target coordinates of active aliens so they follow the sway.
        """
        # Sway the entire formation back and forth
        self.x_offset += self.sway_direction * self.sway_speed
        if abs(self.x_offset) > self.max_sway:
            self.sway_direction *= -1
            
        # Sync the target coordinates of all active aliens in formation
        for alien, base_slot in self.active_aliens.items():
            if alien.alive():
                # Base slot X + the group's swaying offset
                alien.target_x = base_slot[0] + self.x_offset
                
                # If they are already in the formation, let them slide to the new target
                if alien.phase == "in_formation":
                    alien.pos.x = alien.target_x
