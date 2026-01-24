from typing import Tuple, List, Union, Dict, Set
from random import randint
from enum import Enum


class PathEnumerate(Enum):
    NORTH: int = 0
    EAST: int = 1
    SOUTH: int = 2
    WEST: int = 3


class MazeGenerator:

    dir_height: Dict[PathEnumerate, int] = {PathEnumerate.EAST: 0,
                                            PathEnumerate.WEST: 0,
                                            PathEnumerate.NORTH: -1,
                                            PathEnumerate.SOUTH: 1}
    dir_width: Dict[PathEnumerate, int] = {PathEnumerate.EAST: 1,
                                           PathEnumerate.WEST: -1,
                                           PathEnumerate.NORTH: 0,
                                           PathEnumerate.SOUTH: 0}

    def __init__(self,
                 width: int,
                 height: int,
                 entry_point: Tuple[int, int],
                 exit_point: Tuple[int, int],
                 perfect: bool,
                 output_file: str) -> None:

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

        return cls(
            width=data["WIDTH"],
            height=data["HEIGHT"],
            entry_point=tuple(data["ENTRY"]),
            exit_point=tuple(data["EXIT"]),
            perfect=bool(data["PERFECT"]),
            output_file=data["OUTPUT_FILE"],
        )

    def get_maze_config(self) -> str:

        return (f"Maze(width={self.width}, height={self.height}, "
                f"entry_point={self.entry_point}, "
                f"exit_point={self.exit_point}, "
                f"perfect={self.perfect})")

    def check_bounds(self, point: Tuple[int, int]):
        return (point[0] < self.height and point[0] >= 0
                and point[1] < self.width and point[1] >= 0)

    def generate_maze(self) -> None:
        # setup maze
        self.maze = [['F' for _ in range(self.width)]
                     for _ in range(self.height)]
        self.maze[self.entry_point[0]][self.entry_point[1]] = 'i'
        unvisited: Set[Tuple[int, int]] = set{}
        visited: List[Tuple[int, int]] = [self.entry_point]
        for i, height in enumerate(self.maze):
            for j, _ in enumerate(height):
                unvisited.add((i, j))

        unvisited.remove((self.entry_point[0], self.entry_point[1]))

        # loop to find path
        while len(unvisited) > 0:
            next_start: Tuple[int, int] = unvisited[randint(
                0, len(unvisited) - 1)]
            path: List[Tuple[int, int]] = []
            while 1:
                for _, value in self.dir_height.items():
                    next_point: Tuple[int, int] = ((value + next_start[0]),
                                                   (value + next_start[1]))
                    bound: bool = self.check_bounds(next_point)
                    if next_point in path:
                        continue
                    if not bound:
                        continue
                path.append(next_point)

            # add path to visited + remove from unvisited
            for p_pos in path:
                for i, u_pos in enumerate(unvisited):
                    if u_pos == p_pos:
                        self.maze[p_pos[0]][p_pos[1]] = 'x'
                        visited.append(p_pos)
                        unvisited.remove(i)

    def print_maze(self) -> None:

        for height in self.maze:
            for width in height:
                print(width, end="")
            print()

        print()
        print(str(self.entry_point[0]) + "," + str(self.entry_point[1]))
        print(str(self.exit_point[0]) + "," + str(self.exit_point[1]))
        print(self.path)
