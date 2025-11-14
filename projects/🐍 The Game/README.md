# 🐍 Snake Game - Retro Edition

A classic Snake game built with Python and Pygame, featuring retro-style graphics, power-ups, and progressive difficulty.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.5.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 📖 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Controls](#-controls)
- [Gameplay](#-gameplay)
- [Power-ups](#-power-ups)
- [Scoring System](#-scoring-system)
- [Technical Details](#-technical-details)
- [Project Structure](#-project-structure)
- [Tips & Strategies](#-tips--strategies)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **Classic Snake Mechanics**: Smooth snake movement with responsive controls
- **Retro-Style Graphics**: Pixel art with a limited color palette for that authentic retro feel
- **Score System**: Earn points by eating food and collecting power-ups
- **Progressive Difficulty**: Game speed increases as your score grows
- **Power-up System**: 5 different power-ups that temporarily alter gameplay
- **Smooth Controls**: Arrow keys or WASD support with instant response
- **Pause Functionality**: Pause and resume the game at any time
- **Visual Feedback**: Active power-ups displayed with timers

## 🎮 Screenshots

*Gameplay with retro-style graphics and power-ups*

## 📋 Requirements

- Python 3.7 or higher
- Pygame 2.5.0 or higher

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "🐍 The Game"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Run the game:
```bash
python snake_game.py
```

## 🕹️ Controls

| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` | Move snake (Arrow keys) |
| `W` `A` `S` `D` | Move snake (WASD) |
| `P` or `SPACE` | Pause/Resume game |
| `R` | Restart game (on game over screen) |
| `ESC` | Quit game |

## 🎯 Gameplay

### Basic Rules

- The snake moves continuously across a grid
- Eat red food squares to grow and earn points
- Avoid hitting walls or your own body
- Power-ups spawn periodically on the field

### Progressive Difficulty

- Game speed increases every 10 points
- Maximum speed is capped for comfortable gameplay
- The challenge intensifies as you progress

### Power-ups

- Power-ups appear on the field every 3 seconds
- Collect them by moving over them
- Some power-ups have temporary effects (shown in top-left corner)
- Multiple power-up effects can stack

## ⚡ Power-ups

| Power-up | Color | Effect | Duration |
|----------|-------|--------|----------|
| ⚡ **Speed Up** | Cyan | Temporarily increases movement speed | 5 seconds |
| 🐌 **Speed Down** | Blue | Temporarily decreases movement speed | 5 seconds |
| 🛡️ **Invincibility** | Yellow | Protection from collisions (snake flickers) | 10 seconds |
| 💎 **Double Points** | Magenta | Doubles points for next 3 food items | 3 food items |
| 📉 **Shrink** | White | Instantly reduces snake size by 1 segment | Instant |

## 📊 Scoring System

- **Regular Food**: 10 points
- **Food with Double Points**: 20 points (applies to next 3 food items)

## 🛠️ Technical Details

| Specification | Value |
|---------------|-------|
| Resolution | 800×600 pixels |
| Grid Size | 20×20 pixels |
| FPS | 60 frames per second |
| Initial Speed | 150ms between movements |
| Minimum Speed | 50ms (maximum difficulty) |
| Grid Dimensions | 40×30 cells |

## 📁 Project Structure

```
🐍 The Game/
├── snake_game.py      # Main game file
├── requirements.txt   # Project dependencies
└── README.md         # Documentation
```

## 💡 Tips & Strategies

1. **Plan Ahead**: Think about your route to avoid dead ends
2. **Strategic Power-ups**:
   - Use **Invincibility** to pass through your own body
   - **Speed Up** helps collect food quickly
   - **Speed Down** is useful in tight situations
3. **Monitor Active Effects**: Keep an eye on the top-left corner for active power-ups
4. **Control Carefully**: As speed increases, be more cautious with your movements
5. **Combine Effects**: Stack power-ups for maximum advantage

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is created for educational purposes.

---

**Enjoy the game! 🐍**

*Made with ❤️ using Python and Pygame*
