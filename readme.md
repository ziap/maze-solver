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

Once we have a list of tiles to navigate - which I'll call a "tunnel" - we need to find the most optimal way to move between them. One way of doing this is to build a [Visibility graph][4] and then search it. However, we can reduce the time by traversing the tunnel in 8 directions, corner-to-corner, creating a sub-optimal solution, then optimizing it during the post-processing step. [Dijkstra's algorithm][5] is chosen over [A*][6] because the pre-processing step also guarantees no path leading away from the endpoint, thus rendering A* useless.

Finally, I used [path smoothing][7] to convert an 8-angle solution to an any-angle solution. In theory, it will also create the optimal solution because there's only one path for any pair of tiles. It's also reasonably fast because calculating line-of-sight on a tilemap can be done efficiently using the [DDA algorithm][8].

## Result

![](result.png)

## Usage

### Dependencies

- Python (tested with 3.10)
- NumPy
- Numba
- Matplotlib (for visualization, will be replaced with a tkinter UI)

### Installation

```bash
python -m venv .venv

.venv/bin/pip install numpy numba matplotlib
.venv/bin/python main.py
```

**Note:** Numba's first-time compilation can be slow (up to a few seconds). So make sure to warm up if you're going to benchmark this program.

## License

This project is licensed under the [MIT license](LICENSE).

[//]: # (References)
[1]: <https://weblog.jamisbuck.org/2011/1/27/mhze-generation-growing-tree-algorithm>
[2]: <https://en.wikipedia.org/wiki/Any-angle_path_planning>
[3]: <https://en.wikipedia.org/wiki/Breadth-first_search>
[4]: <https://en.wikipedia.org/wiki/Visibility_graph>
[5]: <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>
[6]: <https://en.wikipedia.org/wiki/A*_search_algorithm>
[7]: <https://theory.stanford.edu/~amitp/GameProgramming/MapRepresentations.html#path-smoothing>
[8]: <https://en.wikipedia.org/wiki/Digital_differential_analyzer_(graphics_algorithm)>
