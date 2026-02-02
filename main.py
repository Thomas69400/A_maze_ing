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
        self.n_s_width = 30
        self.n_s_height = 3
        self.e_w_width = 10
        self.e_w_height = 25


def mymouse(button, x, y, mystuff):
    print(f"Got mouse event! button {button} at {x},{y}.")


def close_window(xvar: XVar):
    xvar.mlx.mlx_loop_exit(xvar.mlx_ptr)


def generate_wall_north(xvar: XVar, pixel: int, color: int):
    for row in range(xvar.n_s_height):
        for col in range(xvar.n_s_width):
            xvar.maze_template[pixel + col +
                               (xvar.line_len * row)] = color & 0xFF


def generate_wall_south(xvar: XVar, pixel: int, color: int):
    for row in range(xvar.n_s_height):
        for col in range(xvar.n_s_width):
            xvar.maze_template[pixel + col + (xvar.line_len * row) +
                               xvar.e_w_height * xvar.line_len] = color & 0xFF


def generate_wall_west(xvar: XVar, pixel: int, color: int):
    for row in range(xvar.e_w_height):
        for col in range(xvar.e_w_width):
            xvar.maze_template[pixel + col +
                               (xvar.line_len * row)] = color & 0xFF


def generate_wall_east(xvar: XVar, pixel: int, color: int):
    for row in range(xvar.e_w_height):
        for col in range(xvar.e_w_width):
            xvar.maze_template[pixel + col + xvar.n_s_width +
                               (xvar.line_len * row)] = color & 0xFF


def generate_maze_pixel(
    xvar: XVar,
    x: int,
    y: int,
    color: int,
    maze_value: int
) -> None:

    pixel: int = int((y * xvar.line_len + (x * (xvar.bpp // 8))))

    if maze_value & 1:
        generate_wall_north(xvar, pixel, color)
    if (maze_value >> 1) & 1:
        generate_wall_east(xvar, pixel, color)
    if (maze_value >> 2) & 1:
        generate_wall_south(xvar, pixel, color)
    if (maze_value >> 3) & 1:
        generate_wall_west(xvar, pixel, color)


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
            xvar.mlx_ptr, 1500, 1500, "A-Maze-Ing")
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_ptr)
        if not xvar.win_ptr:
            raise Exception("Can't create main window")
    except Exception as e:
        print(f"Error Win create: {e}", file=sys.stderr)
        sys.exit(1)

    print_strings(xvar)
    xvar.mlx.mlx_key_hook(xvar.win_ptr, get_key, xvar)
    xvar.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, 1000, 1000)
    xvar.maze_template, xvar.bpp, xvar.line_len, endian = xvar.mlx.mlx_get_data_addr(
        xvar.img)

    for row, height in enumerate(maze_gen.maze):
        for col, value in enumerate(height):
            generate_maze_pixel(xvar, col * 16,
                                row * 16, 0xFFFFFF, value)

    # generate_maze_pixel(xvar, 1, 1, 0xFFFFFF, 13)
    # generate_maze_pixel(xvar, 8, 1, 0xFFFFFF, 3)
    # generate_maze_pixel(xvar, 16, 1, 0xFFFFFF, 4)
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win_ptr, xvar.img, 0, 0)

    xvar.mlx.mlx_mouse_hook(xvar.win_ptr, mymouse, None)

    xvar.mlx.mlx_hook(xvar.win_ptr, 33, 0, close_window, xvar)
    xvar.mlx.mlx_loop(xvar.mlx_ptr)


if __name__ == "__main__":
    main()
