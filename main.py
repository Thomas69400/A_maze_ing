"""Entrypoint for the maze generator command-line script.

This module parses a configuration file (defaults to
``default_config.txt``) then generates and resolves a maze using the
``MazeGenerator`` class.
"""

from typing import Dict, Any

from parsing import get_config
from maze_generator import MazeGenerator
import sys


def main() -> None:
    """Run the maze generation flow using a configuration file.

    The function reads the config file path from ``sys.argv`` if
    provided, otherwise it falls back to the default. It constructs a
    :class:`MazeGenerator`, generates the maze, resolves the path and
    writes the result to the configured output file.
    """
    try:
        if len(sys.argv) <= 1:
            config: Dict[str, Any] = get_config()
        else:
            config = get_config(sys.argv[1])
        maze_gen: MazeGenerator = MazeGenerator.from_dict(config)

    except Exception as exc:
        print(f"Error main: {exc}")
        return

    maze_gen.generate_maze()
    maze_gen.resolve_maze()
    maze_gen.set_maze_to_file()


if __name__ == "__main__":
    main()
