# Lunar Attack

A 2D space shooter built with Python and Pygame, developed for the Imaging and Special Effects course at Asia Pacific University. Players pilot a ship through waves of alien enemies, collect upgrades, and face off against a multi-phase boss battle, all backed by custom sprite animations, particle effects, and a full game-state flow (menu, gameplay, pause, game over, history, credits).

## Tech Stack

- **Engine:** Python + [Pygame](https://www.pygame.org/)
- **Image Processing:** OpenCV (`cv2`) and NumPy, used for visual/image-based effects
- **Assets:** Custom sprite sheets, animations, and a pixel font (`PressStart2P`)

## Features

- **Main Menu & Navigation** — Start game, view history, credits, and pause/resume flow
- **Player Ship** — Movement, multiple weapon types (AutoCannon, Rockets, Zapper, BigGun), health states with visual damage feedback, and temporary invincibility
- **Enemy System** — Alien formations (`Formation`, `EnemyManager`) with multiple enemy types and projectile attacks
- **Boss Fight** — A multi-phase boss encounter (`Boss.py` / `BossFight.py`) featuring:
  - HP-based phase transitions (normal → phase 2 → "giant" phase)
  - Scripted intro sequence (fly-in, black hole spawn/despawn, fade transitions)
  - Special attacks including beam and gamma beam effects
  - Asteroid hazard system with multiple asteroid variants (Neutral, Fiery, Eclipse, Scarred, Clone)
- **Visual Effects** — Shatter/sparks particle effects, fade transitions, and frame-based sprite animation via a custom `AnimationManager`
- **HUD** — Real-time health, score, and combat feedback display
- **Audio** — Dedicated `SoundManager` for sound effects and music
- **Score Tracking & History** — Persistent score/history saving (`save.json`)

## Project Structure

```
LunarAttack/
├── main.py                  # Game entry point and main loop
├── MainMenu.py / PauseMenu.py / GameOver.py / History.py / Credits.py
├── Player.py / Weapon.py / Projectile.py
├── Boss.py / BossFight.py    # Boss encounter logic and battle sequence
├── enemy/
│   ├── Alien.py
│   ├── Formation.py
│   ├── EnemyManager.py
│   └── EnemyProjectile.py
├── AnimationManager.py        # Sprite animation playback
├── AssetManager.py              # Texture/animation loading
├── SoundManager.py                # Audio playback
├── ScoreManager.py                  # Score tracking
├── ShatterEffect.py / ShatterParticle.py / SparksEffect.py / FadeTransition.py
├── HUD.py / PlayScreen.py / background.py / globals.py / utils.py
└── save.json                          # Persisted score/history data
```

## Getting Started

1. Clone the repository
2. (Recommended) Create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```
   pip install pygame opencv-python numpy
   ```
4. Run the game:
   ```
   python main.py
   ```

## Contributions

- Richardo Osmond: Designed and implemented the entire **boss battle system** (`Boss.py` and `BossFight.py`), including the boss's phase-based HP states, scripted intro sequence, special attacks (beam/gamma beam), and the asteroid attack system along all the other attacks and a simple decision tree.
