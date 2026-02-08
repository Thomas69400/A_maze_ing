"""Data container module for maze visualization variables.

Provides the XVar class which holds all necessary variables for managing
the MLX window and maze image rendering state.
"""

from typing import Any, Optional
from src.maze_generator import MazeGenerator

from mlx import Mlx


class XVar:
    """Container for maze visualization and MLX window variables.

    This class holds all state information needed for maze rendering,
    including MLX pointers, window dimensions, image data, and maze
    cell dimensions.

    Attributes:
        maze_gen: The maze generator instance.
        mlx: MLX graphics library instance.
        mlx_ptr: Pointer to the MLX instance.
        win_ptr: Pointer to the MLX window.
        win_w: Window width in pixels (default: 700).
        win_h: Window height in pixels (default: 700).
        image_w: Image width in pixels.
        image_h: Image height in pixels.
        img_ptr: Pointer to the MLX image.
        line_len: Pixel line length for image data.
        bpp: Bytes per pixel in image data.
        maze_template: Memory buffer for maze template data.
        n_s_width: North/South wall width in pixels (default: 12).
        n_s_height: North/South wall height in pixels (default: 4).
        e_w_width: East/West wall width in pixels (default: 4).
        e_w_height: East/West wall height in pixels (default: 16).
        pixel_d: Pixel dimension for each maze cell (default: 12).
    """

    def __init__(self, maze_gen: Any,
                 win_w: int = 700,
                 win_h: int = 700) -> None:
        """Initialize the XVar container.

        Args:
            maze_gen: The maze generator instance.
            win_w: Window width in pixels. Defaults to 700.
            win_h: Window height in pixels. Defaults to 700.
        """
        self.maze_gen: MazeGenerator = maze_gen
        self.mlx: Optional[Mlx] = None
        self.mlx_ptr: Optional[Any] = None
        self.win_ptr: Optional[Any] = None
        self.win_w: int = win_w
        self.win_h: int = win_h
        self.image_w: int = 0
        self.image_h: int = 0
        self.img_ptr: Optional[Any] = None
        self.line_len: int = 0
        self.bpp: int = 0
        self.maze_template: Optional[Any] = None
        self.n_s_width: int = 12
        self.n_s_height: int = 4
        self.e_w_width: int = 4
        self.e_w_height: int = 16
        self.pixel_d: int = 12
