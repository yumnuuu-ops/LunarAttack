class AnimationManager:
    def __init__(self, frame_list, speed=0.15):
        self.frames = frame_list       # Receives the array from assetMgr.getAnim()
        self.index = 0.0               # Tracks floating time cursor
        self.animation_speed = speed   # Adjust per object type

    def update(self):
        # Tick the clock forward
        self.index += self.animation_speed
        if self.index >= len(self.frames):
            self.index = 0.0           # Loop back

    def get_current_frame(self):
        return self.frames[int(self.index)]

    def reset(self):
        self.index = 0.0