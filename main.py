from parsing import get_config
from maze_generator import MazeGenerator


def main():
    try:
        config = get_config()
        maze_gen: MazeGenerator = MazeGenerator.from_dict(config)
    except Exception as e:
        print(f"Error main: {e}")
        return

    maze_gen.generate_maze()
    maze_gen.print_maze()


if __name__ == "__main__":
    main()
