from parsing import get_config
from maze_generator import MazeGenerator
import sys


def main():
    try:
        if len(sys.argv) <= 1:
            config = get_config()
        else:
            config = get_config(sys.argv[1])
        maze_gen: MazeGenerator = MazeGenerator.from_dict(config)

    except Exception as e:
        print(f"Error main: {e}")
        return

    maze_gen.generate_maze()
    maze_gen.find_path()
    maze_gen.set_maze_to_file()


if __name__ == "__main__":
    main()
