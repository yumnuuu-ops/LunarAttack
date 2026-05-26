SCREEN_W = 1280
SCREEN_H = 720
BUFFER_SIZE = 32

def is_off_screen(proj_x, proj_y):
    if proj_x > SCREEN_W or (proj_x + BUFFER_SIZE) < 0:
        return True
    if proj_y > SCREEN_H or (proj_y + BUFFER_SIZE) < 0:
        return True
    return False