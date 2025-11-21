# Nexel Games Launcher

A lightweight command-line launcher inspired by major PC game stores. It lets you manage a local library, simulate installs, and record launches without external services.

## Features
- View all games or only installed titles.
- Search by title or genre.
- Show detailed metadata for a game.
- Simulate installs/uninstalls with a custom install path.
- Launch a game to record the last played time.
- Add new games to the library file.

## Installation
This project has no external dependencies beyond Python 3.10+.

Clone the repository and use the provided CLI:

```bash
python nexel_launcher.py --help
```

## Usage
The launcher reads and writes to `data/library.json`. The file is created automatically with sample entries if it does not exist.

### List games
```bash
python nexel_launcher.py list
python nexel_launcher.py list --installed
```

### Search
```bash
python nexel_launcher.py search "space"
```

### Game details
```bash
python nexel_launcher.py info horizon
```

### Install or uninstall
```bash
python nexel_launcher.py install horizon --path "/games/Horizon"
python nexel_launcher.py uninstall horizon
```

### Launch
```bash
python nexel_launcher.py launch horizon
```

### Add a game
```bash
python nexel_launcher.py add "New Game" --genre "Action" --description "Short pitch"
```

> Tip: the launcher uses the provided ID or generates a slug from the title. IDs must be unique.

## Roadmap
- Integrate download/build steps for real game executables.
- Add authentication and cloud sync.
- Provide a graphical interface.
