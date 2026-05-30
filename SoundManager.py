import pygame
from pygame.mixer_music import set_volume


class SoundManager:
    TRACKS = {
        "menu" : "audio/music/mmm.mp3",
    }

    SFX = {
        "back": "audio/sfx/Menu/UI_Back.wav",
        "confirm": "audio/sfx/Menu/UI_Confirm.wav",
        "error": "audio/sfx/Menu/UI_Error.wav",
        "save_load": "audio/sfx/Menu/UI_Save-Load.wav",
        "select": "audio/sfx/Menu/UI_Select.wav",
        "AutoCannon fire": "audio\\sfx\\autocannon fire.wav",
        "Zapper fire": "audio\\sfx\\Zapper fire.wav",
        "Rockets fire": "audio\\sfx\\Rocket fire.wav",
        "BigGun fire": "audio\\sfx\\BigGun fire.wav",
        "asteroid": "audio/sfx/BossFight/Asteroid Sound.wav",
        "mass active": "audio/sfx/BossFight/Mass Active.wav",
        "mass despawn": "audio\\sfx\\Mass despawn.wav",
        "mass spawn": "audio\\sfx\\Mass spawn.wav",
        "phase 1 to 2": "audio\\sfx\\phase 1 to 2.wav",
        "phase 2 to eclipse": "audio\\sfx\\phase 2 to eclipse.wav",
        "eclipse to scarred": "audio\\sfx\\eclipse to scarred.wav",
        "teleport in": "audio\\sfx\\teleport in.wav",
        "teleport out": "audio\\sfx\\teleport out.wav",
        "BigGunProj explosion": "audio\\sfx\\BigGun fire.wav",


        "player hit": "audio\\sfx\\player hit.wav",
        "player dies": "audio\\sfx\\player dies.wav",
    }

    def __init__(self):
        self.current_track = None
        self.music_volume  = 0.5
        self.sfx_volume = 0.3

        self.sounds = {}
        for name, path in self.SFX.items():
            try:
                loaded_sound = pygame.mixer.Sound(path)
                loaded_sound.set_volume(self.sfx_volume)
                self.sounds[name] = loaded_sound
            except Exception as e:
                print(f"SoundManager: Could not load sfx 'name': {e}")

    def play_music(self, track_name, loop=-1):
        path = self.TRACKS.get(track_name)
        if not path:
            print(f"SoundManager: track '{track_name}' not found")
            return
        if self.current_track == track_name:
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(loop)
        self.current_track = track_name

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_track = None

    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def play_sfx(self, sfx_name):
        if sfx_name in self.sounds:
            self.sounds[sfx_name].set_volume(self.sfx_volume)
            self.sounds[sfx_name].play()
        else:
            print(f"SoundManager: sfx '{sfx_name}' not found")

    def loop_sfx(self, sfx_name, volume):
        if sfx_name in self.sounds:
            self.sounds[sfx_name].set_volume(volume)
            self.sounds[sfx_name].play(loops=-1)
        else:
            print(f"SoundManager: sfx '{sfx_name}' not found")

    def stop_sfx(self, sfx_name):
        if sfx_name in self.sounds:
            self.sounds[sfx_name].stop()