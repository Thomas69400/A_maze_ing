"""Maze generation utilities.

This module provides a MazeGenerator class that can create mazes using
Wilson's algorithm. All public functions and classes use Google-style
docstrings and explicit typing.
"""

from typing import Tuple, List, Union, Dict, Set, Optional
from random import choice
from enum import Enum


class PathEnumerate(Enum):
    """Enum for cardinal directions represented as bit flags.

    Values are chosen so that opposing directions have distinct bit masks.
    """

    N: Tuple[int, int] = (1, 0)
    E: Tuple[int, int] = (2, 1)
    S: Tuple[int, int] = (4, 2)
    W: Tuple[int, int] = (8, 3)

    @staticmethod
    def oppose_bit(bit: int) -> int:
        """Return the opposing direction bit for a given direction bit.

        Args:
            bit: Bit integer representing a direction.

        Returns:
            The integer bit representing the opposing direction.
        """

        if bit == PathEnumerate.N.value[0]:
            return PathEnumerate.S.value[0]
        if bit == PathEnumerate.S.value[0]:
            return PathEnumerate.N.value[0]
        if bit == PathEnumerate.E.value[0]:
            return PathEnumerate.W.value[0]
        if bit == PathEnumerate.W.value[0]:
            return PathEnumerate.E.value[0]
        raise ValueError("Invalid direction bit")


class MazeGenerator:
    """Maze generator using Wilson's algorithm for perfect mazes.

    Attributes:
        width: Maze width (number of columns).
        height: Maze height (number of rows).
        entry_point: Tuple[row, col] for maze entry.
        exit_point: Tuple[row, col] for maze exit.
        perfect: If True, generate a perfect maze (no loops).
        output_file: Path to output file (not used by generator logic).
        maze: 2D grid storing cell bitmasks or hex chars after conversion.
        path: Optional path string used for later output.
    """

    dir: Dict[PathEnumerate, Tuple[int, int]] = {
        PathEnumerate.E: (0, 1),
        PathEnumerate.W: (0, -1),
        PathEnumerate.N: (-1, 0),
        PathEnumerate.S: (1, 0)
    }

    def __init__(
        self,
        width: int,
        height: int,
        entry_point: Tuple[int, int],
        exit_point: Tuple[int, int],
        perfect: bool,
        output_file: str
    ) -> None:
        """Initialize the MazeGenerator.

        Args:
            width: Number of columns.
            height: Number of rows.
            entry_point: (row, col) for entry.
            exit_point: (row, col) for exit.
            perfect: Whether to generate a perfect maze.
            output_file: Output filename (for external use).
        """
        self.width: int = width
        self.height: int = height
        self.entry_point: Tuple[int, int] = entry_point
        self.exit_point: Tuple[int, int] = exit_point
        self.perfect: bool = perfect
        self.output_file: str = output_file
        self.maze: List[List[Union[str, int]]] = []
        self.path: str = ""
        self.logo: Set[Tuple[int, int]] = set()

    @classmethod
    def from_dict(cls, data: dict) -> "MazeGenerator":
        """Create a MazeGenerator from a configuration dictionary.

        Args:
            data: Dictionary with keys WIDTH, HEIGHT, ENTRY, EXIT, PERFECT,
                OUTPUT_FILE.

        Returns:
            An initialized MazeGenerator instance.
        """

        return cls(
            width=data["WIDTH"],
            height=data["HEIGHT"],
            entry_point=tuple(data["ENTRY"]),
            exit_point=tuple(data["EXIT"]),
            perfect=bool(data["PERFECT"]),
            output_file=data["OUTPUT_FILE"],
        )

    def get_maze_config(self) -> str:
        """Return a brief textual description of the current maze config.

        Returns:
            A string describing width, height, entry/exit points and perfect.
        """

        return (
            "Maze(width={0}, height={1}, entry_point={2}, "
            "exit_point={3}, perfect={4})".format(
                self.width,
                self.height,
                self.entry_point,
                self.exit_point,
                self.perfect
            )
        )

    def check_bounds(self, point: Tuple[int, int]) -> bool:
        """Check whether a point (row, col) is within maze bounds.

        Args:
            point: (row, col) to check.

        Returns:
            True if point is inside the maze, False otherwise.
        """

        return (
            0 <= point[0] < self.height
            and 0 <= point[1] < self.width
        )

    def generate_maze(self) -> None:
        """Initialize the maze grid and optionally generate paths.

        The maze grid is initialized with border bits. If self.perfect is True,
        Wilson's algorithm is run to carve a perfect maze.
        """

        self.maze = [[15 for _ in range(self.width)]
                     for _ in range(self.height)]

        for row, height_row in enumerate(self.maze):
            for col, _ in enumerate(height_row):
                mask = 0
                if row == 0:
                    mask |= PathEnumerate.N.value[0]
                if row == self.height - 1:
                    mask |= PathEnumerate.S.value[0]
                if col == 0:
                    mask |= PathEnumerate.W.value[0]
                if col == self.width - 1:
                    mask |= PathEnumerate.E.value[0]
                self.maze[row][col] |= mask

        self.place_42()

        if self.perfect:
            self.wilson()

    def place_42(self) -> None:
        if not (self.width >= 9 and self.height >= 7):
            print("Error, can't place 42. Maze too small.")
            return

        middle_h: int = int(self.height / 2)
        middle_w: int = int(self.width / 2)
        # 4
        self.logo.add((middle_h, middle_w - 2))
        for i in range(3):
            self.logo.add((middle_h - i, middle_w - 3))
            self.logo.add((middle_h + i, middle_w - 1))
        # 2
        self.logo.add((middle_h, middle_w + 2))
        for i in range(3):
            self.logo.add((middle_h - i, middle_w + 3))
            self.logo.add((middle_h + i, middle_w + 1))
            self.logo.add((middle_h + 2, middle_w + i + 1))
            self.logo.add((middle_h - 2, middle_w + i + 1))

        if self.entry_point in self.logo or self.exit_point in self.logo:
            self.logo = set()
            print(
                "Error, can't place 42 on maze : entry or exit is on logo.")

    def wilson(self) -> None:
        """Generate a perfect maze using Wilson's algorithm.

        Maintains sets of visited and unvisited cells and performs loop-erased
        random walks until all cells are visited.
        """

        unvisited: Set[Tuple[int, int]] = set()
        visited: Set[Tuple[int, int]] = {self.entry_point}
        for i, height_row in enumerate(self.maze):
            for j, _ in enumerate(height_row):
                unvisited.add((i, j))

        unvisited.remove(self.entry_point)
        for pos in self.logo:
            unvisited.remove(pos)

        while unvisited:
            start: Tuple[int, int] = choice(list(unvisited))
            path: List[Tuple[int, int]] = [start]
            walls: List[PathEnumerate] = []

            path, walls = self.random_walk(start, path, visited)
            for p_pos in path:
                if p_pos in unvisited:
                    visited.add(p_pos)
                    unvisited.remove(p_pos)

            for i in range(len(walls)):
                pos: Tuple[int, int] = path[i]
                n_pos: Tuple[int, int] = path[i + 1]
                bit: int = walls[i].value[0]
                o_bit: int = PathEnumerate.oppose_bit(walls[i].value[0])
                self.maze[pos[0]][pos[1]] ^= bit
                self.maze[n_pos[0]][n_pos[1]] ^= o_bit

    def random_walk(
        self,
        start: Tuple[int, int],
        path: List[Tuple[int, int]],
        visited: Set[Tuple[int, int]]
    ) -> Tuple[List[Tuple[int, int]], List[PathEnumerate]]:
        """Perform a loop-erased random walk from start until it
        reaches visited.

        Args:
            start: Starting cell (row, col).
            path: Current path list; start should be appended already.
            visited: Set of visited cells that terminate the walk.

        Returns:
            A tuple (path, walls) where path is the walked sequence of cells
            (with loops erased) and walls is the sequence of directions
            (PathEnumerate) taken between successive cells.
        """

        walls: List[PathEnumerate] = []

        while True:
            neighbors: List[Tuple[PathEnumerate, Tuple[int, int]]] = []
            for key, d in self.dir.items():
                n: Tuple[int, int] = (d[0] + start[0], d[1] + start[1])

                if self.check_bounds(n) and n not in self.logo:
                    neighbors.append((key, n))

            if not neighbors:
                return path, walls

            random_value: Tuple[PathEnumerate,
                                Tuple[int, int]] = choice(neighbors)
            path_enum: PathEnumerate = random_value[0]
            random_point: Tuple[int, int] = random_value[1]
            start = random_point
            if random_point in path or random_point in self.logo:
                index: int = path.index(random_point) + 1
                path = path[:index]
                walls = walls[:index - 1]
                start = path[-1]
            else:
                walls.append(path_enum)
                path.append(random_point)
                if random_point in visited:
                    return path, walls

    def convert_to_hex(self) -> None:
        """Convert integer cell bitmasks to hexadecimal character
        representation.
        """

        hex_chars: str = "0123456789ABCDEF"
        for row, height_row in enumerate(self.maze):
            for col, case in enumerate(height_row):
                self.maze[row][col] = hex_chars[case]

    def set_maze_to_file(self) -> None:
        """Write the maze representation and metadata to the output file.

        The maze cells are converted to hexadecimal characters and written
        row-by-row. After the maze grid, this writes a blank line, then
        the entry and exit coordinates on separate lines and finally the
        optional path string stored in :attr:`path`.

        Raises:
            OSError: If the output file cannot be written.
        """

        self.convert_to_hex()
        with open(self.output_file, "w", encoding="utf-8") as file:
            for height_row in self.maze:
                for case in height_row:
                    file.write(case)
                file.write("\n")

            file.write("\n")
            file.write(f"{self.entry_point[0]},{self.entry_point[1]}\n")
            file.write(f"{self.exit_point[0]},{self.exit_point[1]}\n")
            file.write(self.path)

    def check_walls(self, point: Tuple[int, int], dir: PathEnumerate) -> bool:
        """Return whether a wall exists in a given cardinal direction.

        Args:
            point: A (row, col) tuple indicating the cell to inspect.
            dir: A :class:`PathEnumerate` value indicating which
                direction to test (N, E, S, W).

        Returns:
            True if the wall/flag bit is set for that direction, False
            otherwise.
        """

        return bool((self.maze[point[0]][point[1]] >> dir.value[1]) & 1)

    def resolve_maze(self) -> None:
        """Resolve the generated maze then put the path in self"""

        path: Dict[Tuple[int, int], int] = self.get_general_path()

        path_str, f = self.find_quickest_path(path, self.entry_point)
        self.path = path_str

    def find_quickest_path(
        self,
        path: Dict[Tuple[int, int], int],
        pos: Tuple[int, int],
    ) -> Tuple[str, bool]:
        """Recursively construct the shortest path string from ``pos``.

        The function expects a precomputed distance map ``path`` where
        keys are cell coordinates and values are distances from the
        entry point. It walks to neighbouring cells whose distance is
        exactly one greater than the current cell, building a string of
        direction names (e.g. 'NESW').

        Args:
            path: Mapping from cell coordinate to integer distance.
            pos: Current cell coordinate to expand from.

        Returns:
            A tuple (directions, found) where ``directions`` is a
            concatenated string of direction names leading from ``pos``
            to the exit when ``found`` is True. If not found, returns
            ("", False).
        """

        if pos == self.exit_point:
            return "", True

        for key, value in self.dir.items():
            n_pos: Tuple[int, int] = (pos[0] + value[0], pos[1] + value[1])

            if (
                not self.check_walls(pos, key)
                and self.check_bounds(n_pos)
                and path.get(n_pos) == path.get(pos, -1) + 1
                and path.get(n_pos) is not None
            ):

                if n_pos == self.exit_point:
                    return key.name, True

                p, found = self.find_quickest_path(path, n_pos)
                if found:
                    return key.name + p, True

        return "", False

    def get_general_path(self) -> Dict[Tuple[int, int], int]:
        """Compute a breadth-first distance map from the entry point.

        This function performs a BFS starting at :attr:`entry_point` and
        returns a mapping of cell coordinates to their distance (in
        steps) from the entry. Cells that are not reachable will retain
        a value of ``None``.

        Returns:
            A dictionary mapping (row, col) tuples to integer distances.
        """

        q_front: List[Tuple[int, int]] = [self.entry_point]
        q_back: List[Tuple[int, int]] = []
        path: Dict[Tuple[int, int], Optional[int]] = {}

        for row in range(self.height):
            for col in range(self.width):
                path[(row, col)] = None
        path[self.entry_point] = 0

        while q_front:
            start: Tuple[int, int] = q_front[0]
            for key, value in self.dir.items():
                n_point: Tuple[int, int] = (
                    start[0] + value[0], start[1] + value[1]
                )
                if (
                    self.check_bounds(n_point)
                    and not self.check_walls(start, key)
                    and (
                        path[n_point] is None
                        or path[n_point] + 1 < path[start]
                    )
                ):
                    path[n_point] = path[start] + 1
                    q_back.append(n_point)

            if q_back:
                q_front.append(q_back.pop(0))
            q_front.pop(0)

        return {k: v for k, v in path.items()}
