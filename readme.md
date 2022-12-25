# Maze solver and generator

## Algorithms

### Maze generation

See [generator.py](generator.py).

This program uses the [growing tree algorithm][1] for generating mazes. However, the algorithm keeps track of a list of edges instead of cells, similar to the randomized Prim's algorithm.

This creates a 2d NumPy array of boolean with the value of `True` representing walkable tiles.

### Solving mazes

See [solver.py](solver.py).

The goal is to find the [Euclidean distance optimal][2] path between any points in the maze. Because I had the luxury of working with mazes with one solution, I have done some clever optimizations to speed up the search drastically.

The maze is pre-processed with a tile-to-tile search to find which tiles are part of the resulting path. Otherwise, they are not considered during the main pathfinding. Because the grid is a non-weighted graph, a simple [Breadth-first-search][3] is sufficient and can be done in linear time.

Once we have a list of tiles to navigate - which I'll call a "tunnel" - we need to find the most optimal way to move between them. For this, we can use [Dynamic programming][4] to iteratively build a taut path between both ends of the tunnel. 

## Result

![](result.png)

## Usage

### Dependencies

- Python (tested with 3.10)
- NumPy
- Numba
- PIL (pillow fork)

### Installation

```bash
python -m venv .venv

.venv/bin/pip install numpy numba pillow
.venv/bin/python main.py
```

**Note:** Numba's first-time compilation can be slow (up to a few seconds). So make sure to warm up if you're going to benchmark this program.

## License

This project is licensed under the [MIT license](LICENSE).

[//]: # (References)
[1]: <https://weblog.jamisbuck.org/2011/1/27/mhze-generation-growing-tree-algorithm>
[2]: <https://en.wikipedia.org/wiki/Any-angle_path_planning>
[3]: <https://en.wikipedia.org/wiki/Breadth-first_search>
[4]: <https://en.wikipedia.org/wiki/Dynamic_programming>
