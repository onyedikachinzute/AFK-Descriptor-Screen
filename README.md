# AFK Descriptor Screen

A fullscreen, animated "away from keyboard" screen for your desktop — instead of a plain lock screen, you get a living cosmic scene: thousands of particles morphing into the word "AFK", a gravity-reactive field of drifting geometric shapes, a pulsing singularity core, streaking comets, and periodic shockwaves. Built with Python and Pygame.

![status](https://img.shields.io/badge/status-active-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-blue)

## Features

- **Particle text morph** — hundreds of glowing particles spring into formation to spell "AFK", with idle drift and shockwave disruption
- **Gravity-reactive shapes** — triangles, squares, hexagons, diamonds, and stars drift across the screen, pulled toward a central "warp core"
- **Autonomous drone cursor** — when the mouse is idle, an invisible "drone" roams the screen and perturbs nearby particles, keeping the scene alive
- **Comets & shockwaves** — random streaking comets and periodic energy shockwaves with screen shake
- **Nebula backdrop, starfield, and vignette** — layered background effects for depth
- **Live status deck** — elapsed AFK time, wall clock, and a custom message displayed in a glowing HUD panel

## Requirements

- Python 3.9+
- [Pygame](https://www.pygame.org/)

Install dependencies:
```bash
pip install pygame
```

## Usage

Run with a default or custom message:
```bash
python afk_screen.py
```

Or pass a custom message directly as an argument:
```bash
python afk_screen.py "Back in a bit — grabbing coffee"
```

If no message is given, you'll be prompted for one via a small popup window.

Press **Esc** at any time to exit.

## Building a standalone .exe (Windows)

Using [PyInstaller](https://pyinstaller.org/):
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=sleeping.ico afk_screen.py
```
The built executable will be in `dist/afk_screen.exe`.

## Configuration

A few constants at the top of `afk_screen.py` control performance/density and can be tuned for slower machines:

| Constant | Description | Default |
|---|---|---|
| `STAR_COUNT` | Number of background starfield particles | 260 |
| `TEXT_PARTICLE_COUNT` | Number of particles forming the "AFK" text | 950 |
| `SHAPE_COUNT` | Number of drifting geometric anomalies | 10 |
| `NEBULA_BLOB_COUNT` | Number of background nebula clouds | 6 |
| `FPS` | Target frame rate | 60 |

## License

MIT — do whatever you want with it.
