"""Maze visualization and rendering module.

Provides the MazeRepresentation class for rendering and displaying mazes
using the MLX graphics library with interactive controls.
"""

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from src.data_class import XVar
from src.maze_generator import MazeGenerator
from mlx import Mlx


class MazeRepresentation:
    """Handles maze visualization and rendering with MLX graphics library.

    This class manages the display of generated mazes, including pixel
    generation, path visualization, and interactive controls for maze
    manipulation.

    Attributes:
        xvar: Container for MLX window and image data.
        maze_gen: The maze generator instance.
        path_color: RGB color value for the path (default: green).
        wall_color: RGB color value for walls (default: white).
        logo_color: RGB color value for logo (default: red).
        frame_count: Current frame counter.
        strings_printed: Flag indicating if UI strings have been printed.
        path_printed: Flag for path visibility state (0 or 1).
        logo_printed: Flag for logo visibility state (0 or 1).
        wall_colored: Flag for wall color state (0 or 1).
    """

    def __init__(self, xvar: XVar, maze_gen: MazeGenerator) -> None:
        """Initialize the MazeRepresentation.

        Args:
            xvar: Container for MLX window and image data.
            maze_gen: The maze generator instance.
        """
        self.xvar: XVar = xvar
        self.maze_gen: MazeGenerator = maze_gen
        self.path_color: int = 0xFF1DF21D
        self.wall_color: int = 0xFFFFFFFF
        self.logo_color: int = 0xFFFF0000
        self.frame_count: int = 0
        self.strings_printed: bool = False
        self.path_printed: int = 0
        self.logo_printed: int = 0
        self.wall_colored: int = 0

    def on_frame(self, param: Optional[Any] = None) -> bool:
        """Handle frame update event.

        Args:
            param: Optional parameter for event callback.

        Returns:
            True if frame count is even, False otherwise.
        """
        self.frame_count += 1

        if self.frame_count == 4 and not self.strings_printed:
            self.print_strings()
            self.strings_printed = True

        return self.frame_count % 2 == 0

    def init_mlx(self) -> None:
        """Initialize the MLX graphics library."""
        self.xvar.mlx = Mlx()
        self.xvar.mlx_ptr = self.xvar.mlx.mlx_init()

    def _mlx(self) -> Mlx:
        """Return a non-None MLX instance or raise if not initialized.

        This helper narrows the Optional[Mlx] to Mlx for callers so mypy
        can safely access MLX methods without union-attr errors.
        """
        mlx = self.xvar.mlx
        if mlx is None:
            raise RuntimeError("MLX is not initialized")
        return mlx

    def init_window(self) -> None:
        """Initialize the MLX window.

        Raises:
            Exception: If window creation fails.
        """
        mlx = self._mlx()
        self.xvar.win_ptr = mlx.mlx_new_window(
            self.xvar.mlx_ptr, self.xvar.win_w, self.xvar.win_h,
            "A-Maze-Ing")
        mlx.mlx_clear_window(self.xvar.mlx_ptr, self.xvar.win_ptr)
        if not self.xvar.win_ptr:
            raise Exception("Can't create main window")

    @staticmethod
    def put_img_to_window(
            func: Callable[..., None]) -> Callable[..., None]:
        """Decorator to put image to window after function execution.

        Args:
            func: The function to decorate.

        Returns:
            Wrapped function that puts image to window after execution.
        """
        @wraps(func)
        def wrapper(self: "MazeRepresentation", *args: Any,
                    **kwargs: Any) -> None:
            func(self, *args, **kwargs)
            mlx = self._mlx()
            mlx.mlx_put_image_to_window(
                self.xvar.mlx_ptr,
                self.xvar.win_ptr,
                self.xvar.img_ptr,
                0,
                0
            )
            return
        return wrapper

    @staticmethod
    def clear_window(
            func: Callable[..., None]) -> Callable[..., None]:
        """Decorator to clear window before function execution.

        Args:
            func: The function to decorate.

        Returns:
            Wrapped function that clears window before execution.
        """
        @wraps(func)
        def wrapper(self: "MazeRepresentation", *args: Any,
                    **kwargs: Any) -> None:
            mlx = self._mlx()
            mlx.mlx_clear_window(self.xvar.mlx_ptr, self.xvar.win_ptr)
            func(self, *args, **kwargs)
            return
        return wrapper

    @staticmethod
    def regenerate_img(
            func: Callable[..., None]) -> Callable[..., None]:
        """Decorator to regenerate image before function execution.

        Args:
            func: The function to decorate.

        Returns:
            Wrapped function that regenerates image before execution.
        """
        @wraps(func)
        def wrapper(self: "MazeRepresentation", *args: Any,
                    **kwargs: Any) -> None:
            mlx = self._mlx()
            mlx.mlx_destroy_image(self.xvar.mlx_ptr, self.xvar.img_ptr)
            self.generate_img()
            self.get_data_utils()
            try:
                mv: Any = self.xvar.maze_template
                mv[:] = b'\x00' * len(mv)
            except Exception:
                pass
            func(self, *args, **kwargs)
            return
        return wrapper

    def close_window(self, param: Optional[Any] = None) -> None:
        """Close the MLX window.

        Args:
            param: Optional parameter for event callback.
        """
        mlx = self._mlx()
        mlx.mlx_loop_exit(self.xvar.mlx_ptr)

    def generate_wall_north(self, pixel: int) -> None:
        """Generate the north wall of a maze cell.

        Args:
            pixel: The pixel offset to start drawing.
        """
        tmp: Any = self.xvar.maze_template
        bpp: int = self.xvar.bpp

        for row in range(self.xvar.n_s_height):
            row_off: int = pixel + (self.xvar.line_len * row)
            for col in range(self.xvar.n_s_width):
                pixel_index: int = row_off + (col * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) \
                        & 0xFF

    def generate_wall_south(self, pixel: int) -> None:
        """Generate the south wall of a maze cell.

        Args:
            pixel: The pixel offset to start drawing.
        """
        tmp: Any = self.xvar.maze_template
        bpp: int = self.xvar.bpp

        for row in range(self.xvar.n_s_height):
            row_off: int = pixel + \
                (self.xvar.line_len * (row + self.xvar.pixel_d))
            for col in range(self.xvar.n_s_width):
                pixel_index: int = row_off + (col * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) \
                        & 0xFF

    def generate_wall_west(self, pixel: int) -> None:
        """Generate the west wall of a maze cell.

        Args:
            pixel: The pixel offset to start drawing.
        """
        tmp: Any = self.xvar.maze_template
        bpp: int = self.xvar.bpp

        for row in range(self.xvar.e_w_height):
            row_off: int = pixel + (self.xvar.line_len * row)
            for col in range(self.xvar.e_w_width):
                pixel_index: int = row_off + (col * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) \
                        & 0xFF

    def generate_wall_east(self, pixel: int) -> None:
        """Generate the east wall of a maze cell.

        Args:
            pixel: The pixel offset to start drawing.
        """
        tmp: Any = self.xvar.maze_template
        bpp: int = self.xvar.bpp

        for row in range(self.xvar.e_w_height):
            row_off: int = pixel + (self.xvar.line_len * row)
            for col in range(self.xvar.e_w_width):
                pixel_index: int = row_off + ((col + self.xvar.pixel_d) * bpp)
                for i in range(bpp):
                    tmp[pixel_index + i] = (self.wall_color >> (8 * i)) \
                        & 0xFF

    def generate_img(self) -> None:
        """Generate the image buffer for the maze.

        Raises:
            Exception: If image dimensions are invalid or image creation
                fails.
        """
        maze_h: int = self.maze_gen.height * self.xvar.pixel_d * 2
        maze_w: int = self.maze_gen.width * self.xvar.pixel_d * 2

        self.xvar.image_h = maze_h
        self.xvar.image_w = maze_w

        if self.xvar.image_w <= 0 or self.xvar.image_h <= 0:
            raise Exception(
                f"Invalid image dimensions: {self.xvar.image_w}x"
                f"{self.xvar.image_h}")

        mlx = self._mlx()
        self.xvar.img_ptr = mlx.mlx_new_image(
            self.xvar.mlx_ptr,
            self.xvar.image_w,
            self.xvar.image_h)

        if self.xvar.img_ptr is None:
            raise Exception("mlx_new_image returned None")

    @put_img_to_window
    def generate_maze_pixel(self) -> None:
        """Generate and render the maze pixels based on maze data."""
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
    def new_maze(self) -> None:
        """Generate and display a new maze."""
        self.maze_gen.path = []
        self.maze_gen.generate_maze()
        self.maze_gen.resolve_maze()
        self.maze_gen.set_maze_to_file()
        self.generate_maze_pixel()
        self.print_strings()
        self.path_printed = 0
        self.logo_printed = 0

    @put_img_to_window
    def fill_case(self, list_case: List[Tuple[int, int]],
                  color: int) -> None:
        """Fill maze cells with a specific color.

        Args:
            list_case: List of (row, col) tuples to fill.
            color: RGB color value to fill with.
        """
        tmp: Any = self.xvar.maze_template
        bpp: int = self.xvar.bpp

        for row, col in list_case:
            pixel: int = int((row * self.xvar.pixel_d * self.xvar.line_len +
                              (col * self.xvar.pixel_d * bpp)))

            for r in range(self.xvar.pixel_d):
                row_off: int = pixel + (self.xvar.line_len * r)
                for c in range(self.xvar.pixel_d):
                    pixel_index: int = row_off + (c * bpp)
                    for i in range(bpp):
                        tmp[pixel_index +
                            i] = (color >> (8 * i)) & 0xFF

        self.generate_maze_pixel()

    def get_key(self, key: int,
                param: Optional[Any] = None) -> int:
        """Handle keyboard input events.

        Args:
            key: The key code pressed.
            param: Optional parameter for event callback.

        Returns:
            0 on success.
        """
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
                self._mlx().mlx_loop_exit(self.xvar.mlx_ptr)
                return 0
        else:
            if key == 52:  # 4
                self._mlx().mlx_loop_exit(self.xvar.mlx_ptr)
                return 0

        return 0

    def print_strings(self) -> None:
        """Print UI strings on the window."""
        bottom_string: int = 120
        if len(self.maze_gen.logo) == 0:
            bottom_string -= 20
        mlx = self._mlx()
        mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "=== A-Maze-ing ==="
        )
        bottom_string -= 20
        mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "1. Re-generate a new maze"
        )
        bottom_string -= 20
        mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "2. Show/Hide path from entry to exit"
        )
        bottom_string -= 20
        mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            "3. Rotate maze colors"
        )
        bottom_string -= 20
        if len(self.maze_gen.logo) > 0:
            mlx.mlx_string_put(
                self.xvar.mlx_ptr,
                self.xvar.win_ptr,
                0,
                self.xvar.win_h - bottom_string,
                0xFFFFFF,
                "4. Change 42 color"
            )
            bottom_string -= 20
        mlx.mlx_string_put(
            self.xvar.mlx_ptr,
            self.xvar.win_ptr,
            0,
            self.xvar.win_h - bottom_string,
            0xFFFFFF,
            f"{'5' if len(self.maze_gen.logo) > 0 else '4'}. Quit"
        )

    def get_data_utils(self) -> None:
        """Extract data address information from the image buffer.

        Raises:
            Exception: If maze_template is None.
        """
        mlx = self._mlx()
        self.xvar.maze_template, \
            self.xvar.bpp, \
            self.xvar.line_len, \
            _ = mlx.mlx_get_data_addr(self.xvar.img_ptr)

        self.xvar.bpp //= 8
        if self.xvar.maze_template is None:
            raise Exception("maze_template is None")

    @staticmethod
    def get_window_dimension(height: int,
                             width: int) -> Tuple[int, int]:
        """Calculate appropriate window dimensions for maze display.

        Args:
            height: Maze height in cells.
            width: Maze width in cells.

        Returns:
            Tuple of (window_height, window_width) in pixels.
        """
        pixel_d: int = 12
        min_h: int = height * pixel_d + 150
        min_w: int = width * pixel_d + 50

        win_h: int = max(min_h, 1000)
        win_w: int = max(min_w, 1000)

        return win_h, win_w
