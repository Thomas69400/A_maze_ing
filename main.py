"""Entrypoint for the maze generator command-line script.

This module parses a configuration file (defaults to
``default_config.txt``) then generates and resolves a maze using the
``MazeGenerator`` class.
"""

from typing import Dict, Any, Tuple, Optional

from parsing import get_config
from maze_generator import MazeGenerator
import sys
from mlx import Mlx


class XVar:
    """Structure for main vars"""

    def __init__(self, maze_gen, win_w: int = 1000, win_h: int = 1000):
        self.maze_gen = maze_gen
        self.mlx: Mlx = None
        self.mlx_ptr = None
        self.win_ptr = None
        self.win_w = win_w
        self.win_h = win_h
        self.img = None
        self.line_len = 0
        self.bpp = 0
        self.maze_template = None
        self.n_s_width = 48
        self.n_s_height = 2
        self.e_w_width = 10
        self.e_w_height = 12
        self.pixel_d = 12


class MazeRepresentation:
    def __init__(self, xvar, maze_gen):
        self.xvar: XVar = xvar
        self.maze_gen: MazeGenerator = maze_gen

    def init_mlx(self):
        self.xvar.mlx = Mlx()
        self.xvar.mlx_ptr = self.xvar.mlx.mlx_init()

    def init_window(self):
        self.xvar.win_ptr = self.xvar.mlx.mlx_new_window(
            self.xvar.mlx_ptr, self.xvar.win_w, self.xvar.win_h, "A-Maze-Ing")
        self.xvar.mlx.mlx_clear_window(self.xvar.mlx_ptr, self.xvar.win_ptr)
        if not self.xvar.win_ptr:
            raise Exception("Can't create main window")

    def close_window(self):
        self.xvar.mlx.mlx_loop_exit(self.xvar.mlx_ptr)

    def generate_wall_north(self, pixel: int, color: int):
        for row in range(self.xvar.n_s_height):
            for col in range(self.xvar.n_s_width):
                self.xvar.maze_template[pixel + col +
                                        (self.xvar.line_len * row)
                                        ] = color & 0xFF

    def generate_wall_south(self, pixel: int, color: int):
        for row in range(self.xvar.n_s_height):
            for col in range(self.xvar.n_s_width):
                self.xvar.maze_template[pixel + col +
                                        (self.xvar.line_len *
                                         (row + self.xvar.e_w_height))
                                        ] = color & 0xFF

    def generate_wall_west(self, pixel: int, color: int):
        for row in range(self.xvar.e_w_height):
            for col in range(self.xvar.e_w_width):
                self.xvar.maze_template[pixel + col +
                                        (self.xvar.line_len * row)
                                        ] = color & 0xFF

    def generate_wall_east(self, pixel: int, color: int):
        for row in range(self.xvar.e_w_height + 2):
            for col in range(self.xvar.e_w_width):
                self.xvar.maze_template[pixel + col + self.xvar.n_s_width +
                                        (self.xvar.line_len * row)
                                        ] = color & 0xFF

    def put_pixel(
        self,
        height: int,
        width: int,
        color: int,
        maze_value: int
    ) -> None:

        pixel: int = int((height * self.xvar.line_len +
                         (width * (self.xvar.bpp // 8))))

        if maze_value & 1:
            self.generate_wall_north(pixel, color)
        if (maze_value >> 1) & 1:
            self.generate_wall_east(pixel, color)
        if (maze_value >> 2) & 1:
            self.generate_wall_south(pixel, color)
        if (maze_value >> 3) & 1:
            self.generate_wall_west(pixel, color)

    def generate_maze_pixel(self):

        for row, height in enumerate(self.maze_gen.maze):
            for col, value in enumerate(height):
                self.put_pixel(row * self.xvar.pixel_d,
                               col * self.xvar.pixel_d, 0xFFFFFF, value)

        self.xvar.mlx.mlx_put_image_to_window(
            self.xvar.mlx_ptr, self.xvar.win_ptr, self.xvar.img, 0, 0)

    def get_key(self, key: int, param: Optional[Any] = None):
        if key == 49:  # 1
            self.maze_gen.generate_maze()
            self.maze_gen.resolve_maze()
            self.maze_gen.set_maze_to_file()
            self.generate_maze_pixel()
            return 0
        if key == 50:  # 2
            return 0
        if key == 51:  # 3
            return 0
        if key == 52:  # 4
            self.xvar.mlx.mlx_loop_exit(self.xvar.mlx_ptr)
            return 0

    def print_strings(self):
        self.xvar.mlx.mlx_string_put(self.xvar.mlx_ptr,
                                     self.xvar.win_ptr,
                                     0,
                                     self.xvar.win_h - 100,
                                     0xFFFFFF,
                                     "=== A-Maze-ing ===")
        self.xvar.mlx.mlx_string_put(self.xvar.mlx_ptr,
                                     self.xvar.win_ptr,
                                     0,
                                     self.xvar.win_h - 80,
                                     0xFFFFFF,
                                     "1. Re-generate a new maze")
        self.xvar.mlx.mlx_string_put(self.xvar.mlx_ptr,
                                     self.xvar.win_ptr,
                                     0,
                                     self.xvar.win_h - 60,
                                     0xFFFFFF,
                                     "2. Show/Hide path from entry to exit")
        self.xvar.mlx.mlx_string_put(self.xvar.mlx_ptr,
                                     self.xvar.win_ptr,
                                     0,
                                     self.xvar.win_h - 40,
                                     0xFFFFFF,
                                     "3. Rotate maze colors")
        self.xvar.mlx.mlx_string_put(self.xvar.mlx_ptr,
                                     self.xvar.win_ptr,
                                     0,
                                     self.xvar.win_h - 20,
                                     0xFFFFFF,
                                     "4. Quit")

    def get_data_utils(self):
        self.xvar.maze_template, \
            self.xvar.bpp, \
            self.xvar.line_len, \
            _ = self.xvar.mlx.mlx_get_data_addr(
                self.xvar.img)

    def generate_img(self):
        self.xvar.img = self.xvar.mlx.mlx_new_image(
            self.xvar.mlx_ptr,
            self.xvar.win_h,
            self.xvar.win_w)

    @staticmethod
    def get_window_dimension(height: int, width: int) -> Tuple[int, int]:
        if height <= 25 and width <= 25:
            return 1000, 1000
        return height * 25, width * 25


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

    maze_represent = MazeRepresentation(XVar(maze_gen, h, w), maze_gen)
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

    maze_represent.print_strings()

    maze_represent.xvar.mlx.mlx_key_hook(
        maze_represent.xvar.win_ptr,
        maze_represent.get_key, None)

    maze_represent.generate_img()
    maze_represent.get_data_utils()
    maze_represent.generate_maze_pixel()

    maze_represent.xvar.mlx.mlx_hook(
        maze_represent.xvar.win_ptr,
        33,
        0,
        maze_represent.close_window,
        maze_represent.xvar)

    maze_represent.xvar.mlx.mlx_loop(maze_represent.xvar.mlx_ptr)


if __name__ == "__main__":
    main()
