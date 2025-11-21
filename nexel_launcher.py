from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Game:
    id: str
    title: str
    genre: str
    description: str
    status: str = "available"
    install_path: Optional[str] = None
    last_played: Optional[str] = None

    def matches(self, query: str) -> bool:
        lowered = query.lower()
        return lowered in self.title.lower() or lowered in self.genre.lower()

    def display(self) -> str:
        status = f"{self.status}" if self.status else "available"
        path_info = f" @ {self.install_path}" if self.install_path else ""
        last_played = f" | Last played: {self.last_played}" if self.last_played else ""
        return f"{self.title} [{status}{path_info}]{last_played}"


class GameLibrary:
    def __init__(self, library_path: Path) -> None:
        self.library_path = library_path
        self.games: List[Game] = []
        self.library_path.parent.mkdir(parents=True, exist_ok=True)
        if self.library_path.exists():
            self._load()
        else:
            self._create_default()

    def _create_default(self) -> None:
        sample = [
            Game(
                id="horizon",
                title="Horizon Skies",
                genre="Adventure",
                description="Explore floating isles in a sprawling single-player story.",
            ),
        ]
        self.games = sample
        self._save()

    def _load(self) -> None:
        raw = json.loads(self.library_path.read_text())
        self.games = [Game(**item) for item in raw]

    def _save(self) -> None:
        data = [asdict(game) for game in self.games]
        self.library_path.write_text(json.dumps(data, indent=2))

    def list_games(self, installed_only: bool = False) -> List[Game]:
        games = self.games
        if installed_only:
            games = [game for game in games if game.status == "installed"]
        return sorted(games, key=lambda game: game.title)

    def search(self, query: str) -> List[Game]:
        return [game for game in self.games if game.matches(query)]

    def get(self, game_id: str) -> Game:
        for game in self.games:
            if game.id == game_id:
                return game
        raise ValueError(f"No game with id '{game_id}' found.")

    def add_game(
        self,
        title: str,
        genre: str,
        description: str,
        game_id: Optional[str] = None,
    ) -> Game:
        new_id = game_id or title.lower().replace(" ", "-")
        if any(game.id == new_id for game in self.games):
            raise ValueError(f"Game id '{new_id}' already exists.")
        game = Game(id=new_id, title=title, genre=genre, description=description)
        self.games.append(game)
        self._save()
        return game

    def install(self, game_id: str, install_path: Optional[str]) -> Game:
        game = self.get(game_id)
        game.status = "installed"
        game.install_path = install_path or f"/games/{game.title.replace(' ', '')}"
        self._save()
        return game

    def uninstall(self, game_id: str) -> Game:
        game = self.get(game_id)
        game.status = "available"
        game.install_path = None
        self._save()
        return game

    def launch(self, game_id: str) -> Game:
        game = self.get(game_id)
        if game.status != "installed":
            raise ValueError(f"Install '{game.title}' before launching.")
        game.last_played = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        self._save()
        return game


class NexelCLI:
    def __init__(self, library: GameLibrary) -> None:
        self.library = library
        self.parser = argparse.ArgumentParser(
            description="Manage and launch games through the Nexel CLI."
        )
        subparsers = self.parser.add_subparsers(dest="command", required=True)

        list_parser = subparsers.add_parser("list", help="List games in your library.")
        list_parser.add_argument("--installed", action="store_true", help="Only show installed games.")

        search_parser = subparsers.add_parser("search", help="Search by title or genre.")
        search_parser.add_argument("query", help="Search string.")

        info_parser = subparsers.add_parser("info", help="Show detailed info for a game.")
        info_parser.add_argument("id", help="Game id.")

        install_parser = subparsers.add_parser("install", help="Simulate a game install.")
        install_parser.add_argument("id", help="Game id.")
        install_parser.add_argument("--path", help="Custom install directory.")

        uninstall_parser = subparsers.add_parser("uninstall", help="Simulate removing a game.")
        uninstall_parser.add_argument("id", help="Game id.")

        launch_parser = subparsers.add_parser("launch", help="Record a game launch.")
        launch_parser.add_argument("id", help="Game id.")

        add_parser = subparsers.add_parser("add", help="Add a game to the library.")
        add_parser.add_argument("title", help="Game title.")
        add_parser.add_argument("--genre", required=True, help="Primary genre.")
        add_parser.add_argument("--description", required=True, help="One-line description.")
        add_parser.add_argument("--id", dest="game_id", help="Optional explicit id.")

    def run(self, args: Optional[list[str]] = None) -> None:
        parsed = self.parser.parse_args(args)
        command = parsed.command

        if command == "list":
            games = self.library.list_games(installed_only=parsed.installed)
            for game in games:
                print(game.display())
        elif command == "search":
            matches = self.library.search(parsed.query)
            if not matches:
                print("No results found.")
                return
            for game in matches:
                print(game.display())
        elif command == "info":
            game = self.library.get(parsed.id)
            print(f"Title: {game.title}\nGenre: {game.genre}\nStatus: {game.status}")
            if game.install_path:
                print(f"Installed at: {game.install_path}")
            if game.last_played:
                print(f"Last played: {game.last_played}")
            print(f"Description: {game.description}")
        elif command == "install":
            game = self.library.install(parsed.id, parsed.path)
            print(f"Installed {game.title} to {game.install_path}")
        elif command == "uninstall":
            game = self.library.uninstall(parsed.id)
            print(f"Uninstalled {game.title}")
        elif command == "launch":
            try:
                game = self.library.launch(parsed.id)
                print(f"Launching {game.title}... Last played updated to {game.last_played}")
            except ValueError as error:
                print(error)
        elif command == "add":
            try:
                game = self.library.add_game(
                    title=parsed.title,
                    genre=parsed.genre,
                    description=parsed.description,
                    game_id=parsed.game_id,
                )
                print(f"Added '{game.title}' with id '{game.id}'.")
            except ValueError as error:
                print(error)


def main() -> None:
    library_path = Path("data/library.json")
    library = GameLibrary(library_path)
    NexelCLI(library).run()


if __name__ == "__main__":
    main()
