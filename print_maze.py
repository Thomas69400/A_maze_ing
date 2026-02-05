from mlx import Mlx
from data_class import XVar
from maze_generator import MazeGenerator
from typing import Optional, Any, Tuple
from functools import wraps


class MazeRepresentation:
    def __init__(self, xvar, maze_gen):
        self.xvar: XVar = xvar
        self.maze_gen: MazeGenerator = maze_gen
        self.path_color = 0xFF1DF21D
        self.wall_color = 0xFFFFFFFF
        self.logo_color = 0xFFFF0000
        self.frame_count = 0
        self.strings_printed = False
        self.path_printed = 0
        self.logo_printed = 0
        self.wall_colored = 0

    def on_frame(self, param: Optional[Any] = None) -> bool:
        self.frame_count += 1

        if self.frame_count == 4 and not self.strings_printed:
            self.print_strings()
            self.strings_printed = True

        return self.frame_count % 2 == 0

    def init_mlx(self):
        self.xvar.mlx = Mlx()
        self.xvar.mlx_ptr = self.xvar.mlx.mlx_init()

    def init_window(self):
        self.xvar.win_ptr = self.xvar.mlx.mlx_new_window(
            self.xvar.mlx_ptr, self.xvar.win_w, self.xvar.win_h, "A-Maze-Ing")
        self.xvar.mlx.mlx_clear_window(self.xvar.mlx_ptr, self.xvar.win_ptr)
        if not self.xvar.win_ptr:
            raise Exception("Can't create main window")

    def put_img_to_window(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.xvar.mlx.mlx_put_image_to_window(
                self.xvar.mlx_ptr,
                self.xvar.win_ptr,
                self.xvar.img_ptr,
                0,
                0
            )
            return
        return wrapper

    def clear_window(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.xvar.mlx.mlx_clear_window(self.xvar.mlx_ptr,
                                           self.xvar.win_ptr)
            return func(self, *args, **kwargs)
        return wrapper

    def regenerate_img(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.xvar.mlx.mlx_destroy_image(
                self.xvar.mlx_ptr, self.xvar.img_ptr)
            self.generate_img()
            self.get_data_utils()
            try:
                mv = self.xvar.maze_template
                mv[:] = b'\x00' * len(mv)
            except Exception:
                pass
            return func(self, *args, **kwargs)
        return wrapper

    def close_window(self, param: Optional[Any] = None):
        self.xvar.mlx.mlx_loop_exit(self.xvar.mlx_ptr)

    def generate_wall_north(self, pixel: int):
        tmp = self.xvar.maze_template
        bpp = self.xvar.bpp

        for row in range(self.xvar.n_s_height):
            row_off = pixel + (self.xvar.line_len * row)
            for col in range(self.xvar.n_s_width):
                pixel_index = row_off + (col * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) & 0xFF

    def generate_wall_south(self, pixel: int):
        tmp = self.xvar.maze_template
        bpp = self.xvar.bpp

        for row in range(self.xvar.n_s_height):
            row_off = pixel + (self.xvar.line_len * (row + self.xvar.pixel_d))
            for col in range(self.xvar.n_s_width):
                pixel_index = row_off + (col * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) & 0xFF

    def generate_wall_west(self, pixel: int):
        tmp = self.xvar.maze_template
        bpp = self.xvar.bpp

        for row in range(self.xvar.e_w_height):
            row_off = pixel + (self.xvar.line_len * row)
            for col in range(self.xvar.e_w_width):
                pixel_index = row_off + (col * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) & 0xFF

    def generate_wall_east(self, pixel: int):
        tmp = self.xvar.maze_template
        bpp = self.xvar.bpp

        for row in range(self.xvar.e_w_height):
            row_off = pixel + (self.xvar.line_len * row)
            for col in range(self.xvar.e_w_width):
                pixel_index = row_off + ((col + self.xvar.pixel_d) * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) & 0xFF

    def generate_img(self):
        maze_h = self.maze_gen.height * self.xvar.pixel_d * 2
        maze_w = self.maze_gen.width * self.xvar.pixel_d * 2

        self.xvar.image_h = maze_h
        self.xvar.image_w = maze_w

        if self.xvar.image_w <= 0 or self.xvar.image_h <= 0:
            raise Exception(
                f"Invalid image dimensions: {self.xvar.image_w}x"
                f"{self.xvar.image_h}")

        self.xvar.img_ptr = self.xvar.mlx.mlx_new_image(
            self.xvar.mlx_ptr,
            self.xvar.image_w,
            self.xvar.image_h)

        if self.xvar.img_ptr is None:
            raise Exception("mlx_new_image returned None")

    @put_img_to_window
    def generate_maze_pixel(self):
        for row, height in enumerate(self.maze_gen.maze):
            for col, value in enumerate(height):
                pixel: int = int((
                    row * self.xvar.line_len * self.xvar.pixel_d +
                    (col * self.xvar.bpp * self.xvar.pixel_d)
                ))

                if value & 1:
                    self.generate_wall_north(pixel)
                if (value >> 1) & 1:
                    self.generate_wall_east(pixel)
                if (value >> 2) & 1:
                    self.generate_wall_south(pixel)
                if (value >> 3) & 1:
                    self.generate_wall_west(pixel)

    @clear_window
    @regenerate_img
    @put_img_to_window
    def new_maze(self):
        self.maze_gen.path = []
        self.maze_gen.generate_maze()
        self.maze_gen.resolve_maze()
        self.maze_gen.set_maze_to_file()
        self.generate_maze_pixel()
        self.print_strings()
        self.path_printed = 0
        self.logo_printed = 0

    @put_img_to_window
    def fill_case(self, list_case, color):
        tmp = self.xvar.maze_template
        bpp = self.xvar.bpp

        for row, col in list_case:
            pixel: int = int((row * self.xvar.pixel_d * self.xvar.line_len +
                              (col * self.xvar.pixel_d * bpp)))

            for r in range(self.xvar.pixel_d):
                row_off = pixel + (self.xvar.line_len * r)
                for c in range(self.xvar.pixel_d):
                    pixel_index = row_off + (c * bpp)
                    for i in range(bpp):
                        tmp[pixel_index +
                            i] = (color >> (8 * i)) & 0xFF

        self.generate_maze_pixel()

    def get_key(self, key: int, param: Optional[Any] = None):
        if key == 49:  # 1
            self.new_maze()
            return 0
        if key == 50:  # 2
            if self.path_printed == 1:
                self.fill_case(self.maze_gen.path, 0xFF000000)
                self.path_printed = 0
            else:
                self.fill_case(self.maze_gen.path, self.path_color)
                self.path_printed = 1
            return 0
        if key == 51:  # 3
            if self.wall_colored == 0:
                self.wall_color = 0xFFABCDEF
                self.generate_maze_pixel()
                self.wall_colored = 1
            else:
                self.wall_color = 0xFFFFFFFF
                self.generate_maze_pixel()
                self.wall_colored = 0
            return 0
        if len(self.maze_gen.logo) > 0:
            if key == 52:  # 4
                if self.logo_printed == 1:
                    self.fill_case(self.maze_gen.logo, 0xFF000000)
                    self.logo_printed = 0
                else:
                    self.fill_case(self.maze_gen.logo, self.logo_color)
                    self.logo_printed = 1
                return 0
            if key == 53:  # 5
                self.xvar.mlx.mlx_loop_exit(self.xvar.mlx_ptr)
                return 0
        else:
            if key == 52:  # 4
                self.xvar.mlx.mlx_loop_exit(self.xvar.mlx_ptr)
                return 0

    def print_strings(self):
        bottom_string = 120
        if len(self.maze_gen.logo) == 0:
            bottom_string -= 20
        self.xvar.mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "=== A-Maze-ing ==="
        )
        bottom_string -= 20
        self.xvar.mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "1. Re-generate a new maze"
        )
        bottom_string -= 20
        self.xvar.mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "2. Show/Hide path from entry to exit"
        )
        bottom_string -= 20
        self.xvar.mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "3. Rotate maze colors"
        )
        bottom_string -= 20
        if len(self.maze_gen.logo) > 0:
            self.xvar.mlx.mlx_string_put(
                self.xvar.mlx_ptr,
                self.xvar.win_ptr,
                0,
                self.xvar.win_h - bottom_string,
                0xFFFFFF,
                "4. Change 42 color"
            )
            bottom_string -= 20
        self.xvar.mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            f"{'5' if len(self.maze_gen.logo) > 0 else '4'}. Quit"
        )

    def get_data_utils(self):
        self.xvar.maze_template, \
            self.xvar.bpp, \
            self.xvar.line_len, \
            _ = self.xvar.mlx.mlx_get_data_addr(
                self.xvar.img_ptr)

        self.xvar.bpp //= 8
        if self.xvar.maze_template is None:
            raise Exception("maze_template is None")

    @staticmethod
    def get_window_dimension(height: int, width: int) -> Tuple[int, int]:
        pixel_d = 12
        min_h = height * pixel_d + 150
        min_w = width * pixel_d + 50

        win_h = max(min_h, 1000)
        win_w = max(min_w, 1000)

        return win_h, win_w
