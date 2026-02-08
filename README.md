*This project has been created as part of the 42 curriculum by tchemin.*

# Description
-----------
A-Maze-ing is a maze generator and solver with simple file output and an optional 42 logo insertion. The generator implements Wilson's algorithm to produce perfect mazes (no loops) and can optionally break walls to introduce loops. The project provides a reusable MazeGenerator implementation that can be packaged for pip installation.

# Instructions
------------
Quick start (development)

- **Using the Makefile (recommended)**
  1. Create venv and install build tools:
     make setup
     (Equivalent to: python3 -m venv .venv && .venv/bin/python -m pip install --upgrade pip build setuptools wheel)
  2. Activate the virtual environment:
     source .venv/bin/activate
     (Or use your shell's equivalent.)
  3. **Install project dependencies (including mlx):**
     make install
     (Installs dependencies from requirements.txt)
  4. Build the package (wheel + sdist):
     make build
     (Equivalent to: python -m build)
  5. Run the project:
     make run
  6. Cleanup build artifacts:
     make clean

  **Common Makefile targets (for reference)**
  - make setup   : create .venv and install build dependencies
  - make install : install project dependencies from requirements.txt
  - make build   : run python -m build to produce dist/
  - make run     : execute main.py
  - make clean   : remove build/, dist/, *.egg-info

**Dependencies note:**
- This project requires the `mlx` module for graphical display.
- The `mlx` library is provided as a `.whl` file in the `dependencies/` folder and is installed automatically via `make install`.

- **Manual commands (fallback)**
    1. Create and activate a virtual environment:
    python3 -m venv .venv
    source .venv/bin/activate
    2. Install build tools and test dependencies:
    pip install --upgrade pip build setuptools wheel
    3. Build the package:
    python -m build 
    
        **Produces dist/mazegen-<version>-py3-none-any.whl and a .tar.gz**
    
    4. Install the built wheel:
    pip install dist/mazegen-1.0.0-py3-none-any.whl

**Single-file reusable module note:**
- The evaluation requires the reusable module to be available as a single file installable by pip.
- To produce a single-file module, copy the core module (src/maze_generator.py) into a single top-level module named mazegen.py at the repository root, then update pyproject.toml to use py_modules = ["mazegen"] before running python -m build. Example:
  [tool.setuptools]
  py_modules = ["mazegen"]

Config file format (complete structure)
--------------------------------------
MazeGenerator expects a mapping with the following keys (JSON/TOML/Dict representation shown):

```JSON
JSON example:
{
  "WIDTH": 15,
  "HEIGHT": 11,
  "ENTRY": [0, 0],
  "EXIT": [10, 14],
  "PERFECT": true,
  "OUTPUT_FILE": "maze.map"
}
```

Fields:
- **WIDTH**: integer (number of columns)
- **HEIGHT**: integer (number of rows)
- **ENTRY**: [row, col] (start cell)
- **EXIT**: [row, col] (end cell)
- **PERFECT**: boolean (True => perfect maze, False => allow loops)
- **OUTPUT_FILE**: string (path where the hex-map and metadata will be written)

# Maze generation algorithm
-------------------------
Algorithm used: Wilson's algorithm (loop-erased random walks).
Why Wilson's?
- Produces uniform spanning trees (every perfect maze equally likely).
- Guarantees a perfect maze (no cycles) and full connectivity.
- Well-suited for educational and reproducible maze generation.

# Reusable code and how to reuse it
---------------------------------
- Core reusable component: **MazeGenerator class** (src/maze_generator.py).
  Public APIs:
  - MazeGenerator.from_dict(data)
  - generate_maze()
  - resolve_maze()
  - set_maze_to_file()
  - convert_to_hex(...)
- To reuse as a library module:
  - Option A (single-file): copy MazeGenerator contents to mazegen.py at repo root and build with py_modules.
  - Option B (package): keep mazegen/ package and use the package name mazegen; import as from mazegen.maze_generator import MazeGenerator.
- The convert_to_hex and set_maze_to_file functions are small utilities that can be reused independently.

# Build / packaging notes
-----------------------
- Ensure pyproject.toml is configured for setuptools/build. Example minimal [build-system]:
  [build-system]
  requires = ["setuptools>=42", "wheel"]
  build-backend = "setuptools.build_meta"
- For a single-file module distribution, set:
  [tool.setuptools]
  py_modules = ["mazegen"]
- Build commands:
  python -m pip install --upgrade build setuptools wheel
  python -m build
- The evaluator will look for artifacts like:
  - mazegen-1.0.0-py3-none-any.whl
  - mazegen-1.0.0.tar.gz
  in the dist/ directory.

# Example usage
-------------
#### create a MazeGenerator from a JSON-like dict and build a maze file

```python
from mazegen import MazeGenerator

cfg = {
  "WIDTH": 21,
  "HEIGHT": 11,
  "ENTRY": [0, 0],
  "EXIT": [10, 20],
  "PERFECT": True,
  "OUTPUT_FILE": "out.map"
}
m = MazeGenerator.from_dict(cfg)
m.generate_maze()
m.resolve_maze()
m.set_maze_to_file()
```

#### Passing custom parameters (size)

```python
from mazegen import MazeGenerator

cfg = {
  "WIDTH": 31,           # Custom width
  "HEIGHT": 21,          # Custom height
  "ENTRY": [0, 0],
  "EXIT": [20, 30],
  "PERFECT": False,      # Allow loops
  "OUTPUT_FILE": "custom.map",
}
m = MazeGenerator.from_dict(cfg)
m.generate_maze()
```

#### Accessing the generated maze structure

```python
from mazegen import MazeGenerator

m = MazeGenerator.from_dict(cfg)
m.generate_maze()

# Access the internal maze grid (2D list of cell values)
maze_grid = m.maze          # Raw maze structure (walls and passages)
width = m.width             # Maze width
height = m.height           # Maze height
entry = m.entry_point       # Entry coordinates [row, col]
exit_cell = m.exit_point    # Exit coordinates [row, col]
```

#### Accessing the solution path

```python
from mazegen import MazeGenerator

m = MazeGenerator.from_dict(cfg)
m.generate_maze()
m.resolve_maze()

# Access the solution path (list of [row, col] coordinates from entry to exit)
solution_path = m.path  # List of cells forming the solution
```

# Resources
---------
- Wilson, D. B. (1996). Generating random spanning trees more quickly than the cover time.
- Python packaging guide: https://packaging.python.org/
- setuptools docs: https://setuptools.pypa.io/
- mypy docs (module layout): https://mypy.readthedocs.io/

# AI usage disclosure
-------------------
AI assistance was used to:
- Draft README content and build instructions.
- Propose Makefile and pyproject.toml adjustments.
Human review: all code, configuration and final packaging decisions were validated and adjusted by the author.

# Team & project management
-------------------------
- **Author / role**: tchemin — design, implementation, packaging, documentation.

- **Anticipated planning and evolution**:
  - **Week 1**: Research maze algorithms, prototype Wilson's algorithm, implement core MazeGenerator class, add solver.
  - **Week 2**: Add 42 logo feature, implement hex output format, packaging (pyproject.toml, Makefile), documentation, testing.
  
  *Evolution*: Initial plan focused only on generation; solving and hex output were added mid-project. Packaging took longer than expected due to single-file module requirement.

- **What worked well**:
  - Wilson's algorithm provided unbiased mazes and simple deterministic behavior for tests.
  - Separating generation and solving logic made debugging easier.
  - Using a config dict allowed flexible instantiation.

- **What could be improved**:
  - Add more unit tests for edge cases (very small mazes, invalid configs).
  - Implement visualization (ASCII or graphical) for debugging.
  - Consider adding multiple algorithm options (Kruskal, Prim) for comparison.

- **Tools used**: Python 3.10+, setuptools, build, flake8, mypy, pytest, git.

# Contact / Repository
--------------------
Repository: https://github.com/Thomas69400/A_maze_ing
Issues and PRs are welcome.
