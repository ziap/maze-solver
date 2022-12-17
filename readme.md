# Maze solver and generator

## Dependencies

- Python (tested with 3.10)
- Numpy
- Numba
- Matplotlib (for visualization, will be replaced with a tkinter UI)

## Algorithms

### Maze generation

See [generator.py](generator.py).

This program uses the [growing tree algorithm][1] for generating mazes. However, the algorithm keeps track of a list of edges instead of cells, similar to the randomized Prim's algorithm.

This creates a 2d numpy array of boolean with the value of `True` representing walkable tiles.

### Solving mazes

See [solver.py](solver.py).

The goal is to find the [Euclidean distance optimal path][2] between any points in the maze. This can be done by using the [Dijkstra's algorithm][3] on the vertices of the tilemap, with a post-processing step to produce the taut path and a pre-processing step to reduce the amount of vertices. Because I had the luxury of working with mazes with one solution, I have done some clever optimizations to speed up the search drastically. 

To pre-process the maze, a tile-to-tile traversal are performed to find out which tiles are part of the resulting path, all other tiles are not considered during the main search. Because there's only one path for any pairs of tiles (hence the one solution), any graph traversal algorithm can be used. I used the breadth-first-search algorithm because it's very fast and easy to implement.

Once we have a list of tiles to navigate which I'll call "tunnel", we need to find out the most optimal way to move between them. One way of doing this is to build a [Visibility graph][4] then traverses it, but we can reduce the time by traversing the vertices of the tunnel in 8 directions to create a sub-optimal solution, then optimize it during the post-processing step. The Dijkstra's algorithm are chosen over [A*][5] because after pre-processing it's also guaranteed that there's no path leading away from the end point, thus rendering A* useless.

Finally, to get the optimal path I used [path smoothing][6], which is fairly simple and straightforward. In theory it will also produce the optimal path but I can't be bothered to explain why or prove it. It's also very fast because calculating line-of-sight on a tilemap can be done efficiently using the [DDA algorithm][7].

## Result

![](result.png)

## License

This project is licensed under the [MIT license](LICENSE).

[//]: # (References)
[1]: <https://weblog.jamisbuck.org/2011/1/27/mhze-generation-growing-tree-algorithm>
[2]: <https://en.wikipedia.org/wiki/Any-angle_path_planning>
[3]: <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>
[4]: <https://en.wikipedia.org/wiki/Visibility_graph>
[5]: <https://en.wikipedia.org/wiki/A*_search_algorithm>
[6]: <https://theory.stanford.edu/~amitp/GameProgramming/MapRepresentations.html#path-smoothing>
[7]: <https://en.wikipedia.org/wiki/Digital_differential_analyzer_(graphics_algorithm)>
