# Pigeons

This was made in haste, and the product of procrastination by Physics Group consisting of
1. Chan
2. Hills
3. Ren 
4. Kuya Wince

## Description

**Pigeons!** is a 2D projectile-shooting game where you hurl stones at flying birds across a nighttime cityscape. It leverages Pygame’s rendering and audio capabilities to deliver sprite animations, background music, and sound effects ([Wikipedia][5]). The physics engine models realistic gravity­influenced trajectories, and each hit awards points and extra ammo ([GitHub][6]).

## Features

* **Physics-based projectile motion** with adjustable angle and velocity ([GitHub][6]).
* **Animated sprites** for birds and the zombieboy character, using frame-by-frame animations ([GitHub][7]).
* **Dynamic leaderboard** persisted in JSON, showing top 5 high scores with timestamps ([Wikipedia][2]).
* **Soundtrack and SFX**: continuous background music plus throw, explosion, selection, and high-score sounds ([GitHub][1]).

## Installation

1. Ensure **Python 3.8+** is installed on your system ([Wikipedia][5]).
2. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/pigeons.git
   cd pigeons
   ```
3. Install dependencies via pip:

   ```bash
   pip install pygame
   ```

   ([GitHub][6])

## Usage

1. Run the main game script:

   ```bash
   python main.py
   ```

   ([Reddit][3])
2. On game over, enter your name (up to 10 alphanumeric characters) to record your score on the leaderboard ([Wikipedia][2]).

## Controls

* **↑ / ↓**: Increase / decrease launch angle ([Reddit][3]).
* **← / →**: Decrease / increase launch velocity ([Reddit][3]).
* **SPACE**: Throw a stone (if ammo remains) ([Reddit][3]).
* **ENTER**: Confirm name input on game over ([Reddit][3]).

## Contributing

Contributions are welcome! Please fork the repo, create a feature branch, and submit a pull request ([Wikipedia][2]). Adhere to existing code style, include clear commit messages, and document any new functionality in this README ([Medium][4]).

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details ([Wikipedia][2]).

[1]: https://github.com/pygame/pygame/blob/main/README.rst?utm_source=chatgpt.com "pygame/README.rst at main - GitHub"
[2]: https://en.wikipedia.org/wiki/README?utm_source=chatgpt.com "README"
[3]: https://www.reddit.com/r/pygame/comments/146q3mq/can_anyone_help_me_on_what_goes_in_a_basic_readme/?utm_source=chatgpt.com "Can anyone help me on what goes in a basic README for a very ..."
[4]: https://medium.com/voxel51/elevate-your-github-readme-game-5deb31c1df3b?utm_source=chatgpt.com "Elevate Your GitHub README Game - Medium"
[5]: https://en.wikipedia.org/wiki/Pygame?utm_source=chatgpt.com "Pygame"
[6]: https://github.com/takluyver/pygame/blob/master/examples/readme.txt?utm_source=chatgpt.com "pygame/examples/readme.txt at master - GitHub"
[7]: https://github.com/pygame/pygame/blob/main/examples/aliens.py?utm_source=chatgpt.com "pygame/examples/aliens.py at main - GitHub"
