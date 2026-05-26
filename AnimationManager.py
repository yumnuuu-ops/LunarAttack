class AnimationManager:
    def __init__(self, frame_list, speed=0.15):
        self.frames = frame_list       # Receives the array from assetMgr.getAnim()
        self.index = 0.0               # Tracks floating time cursor
        self.animation_speed = speed   # Adjust per object type

    def update(self, loop = True):
        # Tick the clock forward
        self.index += self.animation_speed
        if loop:
            if self.index >= len(self.frames):
                self.index = 0.0           # Loop back
        else:
            max_index = len(self.frames) - 1
            if self.index > max_index:
                self.index = float(max_index)

    def get_current_frame(self):
        # Cleaned up syntax check to make sure the list isn't empty
        if len(self.frames) > 0:
            return self.frames[int(self.index)]
        return None

    def reset(self):
        self.index = 0.0