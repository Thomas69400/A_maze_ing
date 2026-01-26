"""Maze generation utilities.

This module provides a MazeGenerator class that can create mazes using
Wilson's algorithm. All public functions and classes use Google-style
docstrings and explicit typing.
"""

from typing import Tuple, List, Union, Dict, Set
from random import choice
from enum import Enum


class PathEnumerate(Enum):
    """Enum for cardinal directions represented as bit flags.

    Values are chosen so that opposing directions have distinct bit masks.
    """

    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

    @staticmethod
    def oppose_bit(bit: int) -> int:
        """Return the opposing direction bit for a given direction bit.

        Args:
            bit: Bit integer representing a direction.

        Returns:
            The integer bit representing the opposing direction.
        """

        if bit == PathEnumerate.NORTH.value:
            return PathEnumerate.SOUTH.value
        if bit == PathEnumerate.SOUTH.value:
            return PathEnumerate.NORTH.value
        if bit == PathEnumerate.EAST.value:
            return PathEnumerate.WEST.value
        if bit == PathEnumerate.WEST.value:
            return PathEnumerate.EAST.value
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
        PathEnumerate.EAST: (0, 1),
        PathEnumerate.WEST: (0, -1),
        PathEnumerate.NORTH: (-1, 0),
        PathEnumerate.SOUTH: (1, 0)
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
                    mask |= PathEnumerate.NORTH.value
                if row == self.height - 1:
                    mask |= PathEnumerate.SOUTH.value
                if col == 0:
                    mask |= PathEnumerate.WEST.value
                if col == self.width - 1:
                    mask |= PathEnumerate.EAST.value
                self.maze[row][col] |= mask

        if self.perfect:
            self.wilson()
        self.convert_to_hex()

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
                bit: int = walls[i].value
                o_bit: int = PathEnumerate.oppose_bit(walls[i].value)
                self.maze[pos[0]][pos[1]] = self.maze[pos[0]][pos[1]] ^ bit
                self.maze[n_pos[0]][n_pos[1]] = (
                    self.maze[n_pos[0]][n_pos[1]] ^ o_bit
                )

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
                if self.check_bounds(n):
                    neighbors.append((key, n))

            if not neighbors:
                return path, walls

            random_value: Tuple[PathEnumerate,
                                Tuple[int, int]] = choice(neighbors)
            path_enum: PathEnumerate = random_value[0]
            random_point: Tuple[int, int] = random_value[1]
            start = random_point
            if random_point in path:
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
                # case is an int here
                self.maze[row][col] = hex_chars[case]

    def set_maze_to_file(self) -> None:

        with open(self.output_file, "w") as file:
            for height_row in self.maze:
                for case in height_row:
                    file.write(case)
                file.write("\n")

            file.write("\n")
            file.write(f"{self.entry_point[0]},{self.entry_point[1]}\n")
            file.write(f"{self.exit_point[0]},{self.exit_point[1]}\n")
            file.write(self.path)
