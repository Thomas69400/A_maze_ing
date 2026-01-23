from typing import Tuple, List, Union


class MazeGenerator:

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

    def generate_maze(self) -> None:

        self.maze = [[5 for _ in range(self.width + 1)]
                     for _ in range(self.height + 1)]

        # Entry and Exit points
        # self.maze[self.entry_point[1] + 1][self.entry_point[0] + 1] = 1
        # self.maze[self.exit_point[1]][self.exit_point[0]] = 1

    def print_maze(self) -> None:

        for x in self.maze:
            for y in x:
                print(y, end="")
            print()

        print()
        print(str(self.entry_point[0]) + "," + str(self.entry_point[1]))
        print(str(self.exit_point[0]) + "," + str(self.exit_point[1]))
        print(self.path)
