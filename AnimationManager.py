import globals as g

class AnimationManager:
    def __init__(self, frame_list, target_fps=12): # 0.24 speed is 14 fps, change to 0.4 speed for 24 fps for faster pace
        self.frames = frame_list       # Receives the array from assetMgr.getAnim()
        self.index = 0.0               # Tracks floating time cursor
        self.animation_speed = float(target_fps)   # Adjust per object type

    def update(self, loop = True):
        # Tick the clock forward
        self.index += self.animation_speed * g.dt
        max_index = len(self.frames)

        if self.index >= max_index:
            if loop:
                self.index = 0.0  # loop
            else:
                max_index = len(self.frames) - 1
                self.index = float(max_index)  # Freeze on the last frame

    def get_current_frame(self):
        # Cleaned up syntax check to make sure the list isn't empty
        if len(self.frames) > 0:
            return self.frames[int(self.index)]
        return None

    def reset(self):
        self.index = 0.0

    def checkEndOfAnimation(self):
        current_frame = int(self.index)
        max_frame_index = len(self.frames) - 1
        if current_frame >= max_frame_index:
            return True
        else:
            return False