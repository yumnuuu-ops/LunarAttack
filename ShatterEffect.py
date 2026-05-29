import pygame
from globals import particle_group
from ShatterParticle import ShatterParticle


class ShatterEffect:
    @staticmethod
    def trigger(entity, rows=4, cols=4):
        # Take texture and size from the entity image
        orig_img = entity.image
        w, h = orig_img.get_size()

        chunk_w = w // cols
        chunk_h = h // rows

        # Cut the image up into grid to fly off in random direction
        for r in range(rows):
            for c in range(cols):
                # Crop the specific grid square
                crop_rect = pygame.Rect(c * chunk_w, r * chunk_h, chunk_w, chunk_h)
                chunk_surface = orig_img.subsurface(crop_rect)

                # Calculate where this chunk lives in the world
                # Only spawn a particle if this chunk contains visible pixels
                tight_box = chunk_surface.get_bounding_rect()
                if tight_box.width > 0 and tight_box.height > 0:
                    world_x = entity.rect.x + (c * chunk_w)
                    world_y = entity.rect.y + (r * chunk_h)

                    # Create the flying fragment
                    shard = ShatterParticle(chunk_surface, world_x, world_y)

                    # Add to particle group for update and draw
                    particle_group.add(shard)