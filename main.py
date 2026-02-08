"""Entrypoint for the maze generator command-line script.

This module provides the main entry point for the A-Maze-ing application.
It parses configuration from a file (defaults to ``default_config.txt``),
generates and resolves a maze using the ``MazeGenerator`` class, then
displays it interactively using MLX graphics library.

Functions:
    main: Execute the maze generation and visualization flow.
"""

import sys
from typing import Any, Dict

from src.data_class import XVar
from src.maze_generator import MazeGenerator
from src.parsing import get_config
from src.print_maze import MazeRepresentation


def main() -> None:
    """Run the maze generation and visualization flow.

    Reads a configuration file (from command-line argument or default),
    creates a MazeGenerator instance, generates and resolves the maze,
    then initializes the MLX graphics window for interactive display.

    The function handles all initialization steps for MLX, window creation,
    image generation, and event hooks. Errors at critical stages cause
    the program to exit with status code 1.

    Raises:
        SystemExit: If MLX initialization, window creation, or maze
            display fails.

    Note:
        Configuration file path can be provided as first command-line
        argument. If not provided, defaults to ``default_config.txt``.
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

    h: int
    w: int
    h, w = MazeRepresentation.get_window_dimension(maze_gen.height,
                                                   maze_gen.width)

    maze_represent: MazeRepresentation = MazeRepresentation(
        XVar(maze_gen, w, h), maze_gen)
    try:
        maze_represent.init_mlx()
    except Exception as e:
        print(f"Error: Can't initialize MLX: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        maze_represent.init_window()
    except Exception as e:
        print(f"Error Win create: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        mlx = maze_represent._mlx()
        mlx.mlx_key_hook(
            maze_represent.xvar.win_ptr,
            maze_represent.get_key, None)
    except Exception as e:
        print(f"Error: Can't make action: {e}")
        sys.exit(1)

    try:
        maze_represent.generate_img()
        maze_represent.get_data_utils()
        maze_represent.generate_maze_pixel()
    except Exception as e:
        print(f"Error: Can't display maze: {e}")
        sys.exit(1)

    mlx.mlx_hook(
        maze_represent.xvar.win_ptr,
        33,
        0,
        maze_represent.close_window,
        None)

    mlx.mlx_loop_hook(
        maze_represent.xvar.mlx_ptr,
        maze_represent.on_frame,
        None
    )

    mlx.mlx_loop(maze_represent.xvar.mlx_ptr)


if __name__ == "__main__":
    main()
