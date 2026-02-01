"""Entrypoint for the maze generator command-line script.

This module parses a configuration file (defaults to
``default_config.txt``) then generates and resolves a maze using the
``MazeGenerator`` class.
"""

from typing import Dict, Any

from parsing import get_config
from maze_generator import MazeGenerator
import sys
from mlx import Mlx


class XVar:
    """Structure for main vars"""

    def __init__(self):
        self.mlx: Mlx = None
        self.mlx_ptr = None
        self.screen_w = 0
        self.screen_h = 0
        self.win_ptr = None
        self.img = None
        self.line_len = 0
        self.bpp = 0
        self.maze_template = None


def close_window(xvar: XVar):
    xvar.mlx.mlx_loop_exit(xvar.mlx_ptr)


def put_pixel(xvar: XVar, x: int, y: int, color: int):
    pixel: int = int((y * xvar.line_len + (x * 4)))
    xvar.maze_template[pixel] = color & 0xFF
    xvar.maze_template[pixel + 1] = (color >> 8) & 0xFF
    xvar.maze_template[pixel + 2] = (color >> 16) & 0xFF
    xvar.maze_template[pixel + 3] = (color >> 24) & 0xFF


def get_key(key: int, xvar: XVar):
    if key == 49:  # 1
        return 1
    if key == 50:  # 2
        return 2
    if key == 51:  # 3
        return 3
    if key == 52:  # 4
        xvar.mlx.mlx_loop_exit(xvar.mlx_ptr)
        return 4


def print_strings(xvar: XVar):
    xvar.mlx.mlx_string_put(xvar.mlx_ptr, xvar.win_ptr,
                            0, 900, 0xFFFFFF, "=== A-Maze-ing ===")
    xvar.mlx.mlx_string_put(xvar.mlx_ptr, xvar.win_ptr,
                            0, 920, 0xFFFFFF, "1. Re-generate a new maze")
    xvar.mlx.mlx_string_put(xvar.mlx_ptr, xvar.win_ptr,
                            0, 940, 0xFFFFFF, "2. Show/Hide path from entry to exit")
    xvar.mlx.mlx_string_put(xvar.mlx_ptr, xvar.win_ptr,
                            0, 960, 0xFFFFFF, "3. Rotate maze colors")
    xvar.mlx.mlx_string_put(xvar.mlx_ptr, xvar.win_ptr,
                            0, 980, 0xFFFFFF, "4. Quit")


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

    xvar = XVar()
    try:
        xvar.mlx = Mlx()
    except Exception as e:
        print(f"Error: Can't initialize MLX: {e}", file=sys.stderr)
        sys.exit(1)

    xvar.mlx_ptr = xvar.mlx.mlx_init()

    try:
        xvar.win_ptr = xvar.mlx.mlx_new_window(
            xvar.mlx_ptr, 1000, 1000, "A-Maze-Ing")
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_ptr)
        if not xvar.win_ptr:
            raise Exception("Can't create main window")
    except Exception as e:
        print(f"Error Win create: {e}", file=sys.stderr)
        sys.exit(1)

    print_strings(xvar)
    xvar.mlx.mlx_key_hook(xvar.win_ptr, get_key, xvar)
    xvar.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, 600, 600)
    xvar.maze_template, xvar.bpp, xvar.line_len, endian = xvar.mlx.mlx_get_data_addr(
        xvar.img)

    for i in range(500):
        for j in range(500):
            put_pixel(xvar, i, j, 0xFFFFFF)
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win_ptr, xvar.img, 0, 0)

    for i in range(400, 500):
        for j in range(400, 500):
            put_pixel(xvar, i, j, 0xABCDEF)
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win_ptr, xvar.img, 0, 0)

    xvar.mlx.mlx_hook(xvar.win_ptr, 33, 0, close_window, xvar)
    xvar.mlx.mlx_loop(xvar.mlx_ptr)


if __name__ == "__main__":
    main()
