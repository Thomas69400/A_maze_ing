from mlx import Mlx


class XVar:
    """Structure for main vars"""

    def __init__(self, maze_gen, win_w: int = 700, win_h: int = 700):
        self.maze_gen = maze_gen
        self.mlx: Mlx = None
        self.mlx_ptr = None
        self.win_ptr = None
        self.win_w = win_w
        self.win_h = win_h
        self.image_w = 0
        self.image_h = 0
        self.img_ptr = None
        self.line_len = 0
        self.bpp = 0
        self.maze_template = None
        self.n_s_width = 12
        self.n_s_height = 4
        self.e_w_width = 4
        self.e_w_height = 16
        self.pixel_d = 12
