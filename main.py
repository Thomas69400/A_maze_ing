"""Entrypoint for the maze generator command-line script.

This module parses a configuration file (defaults to
``default_config.txt``) then generates and resolves a maze using the
``MazeGenerator`` class.
"""

from typing import Dict, Any
from parsing import get_config
from maze_generator import MazeGenerator
from print_maze import MazeRepresentation
from data_class import XVar
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

    h, w = MazeRepresentation.get_window_dimension(maze_gen.height,
                                                   maze_gen.width)

    maze_represent = MazeRepresentation(XVar(maze_gen, w, h), maze_gen)
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
        maze_represent.xvar.mlx.mlx_key_hook(
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

    maze_represent.xvar.mlx.mlx_hook(
        maze_represent.xvar.win_ptr,
        33,
        0,
        maze_represent.close_window,
        None)

    maze_represent.xvar.mlx.mlx_loop_hook(
        maze_represent.xvar.mlx_ptr,
        maze_represent.on_frame,
        None
    )

    maze_represent.xvar.mlx.mlx_loop(maze_represent.xvar.mlx_ptr)


if __name__ == "__main__":
    main()
