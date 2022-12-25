from numba import njit
from math import floor, ceil

import numpy as np
import heapq as hq

from util import bound_check, distance


@njit(cache=True)
def get_tiles(vertex):
    x, y = vertex
    tiles = set()
    for i in (floor(x), ceil(x) - 1):
        for j in (floor(y), ceil(y) - 1):
            tiles.add((i, j))

    return tiles


@njit(cache=True)
def get_vertices(tile):
    x, y = tile
    return [
        (x, y),
        (x + 1, y),
        (x, y + 1),
        (x + 1, y + 1)
    ]


@njit(cache=True)
def colinear(a, b, c):
    xa, ya = a
    xb, yb = b
    xc, yc = c

    return xa == xb == xc or ya == yb == yc


@njit(cache=True)
def preprocess(maze, start, end):
    visited = np.zeros(maze.shape, dtype=np.bool8)
    come_from = np.full((*maze.shape, 2), -1)
    queue = [i for i in start]
    front = len(queue) - 1

    while front < len(queue):
        x, y = queue[front]
        front += 1

        if (x, y) in end:
            walkable = []

            while not (x, y) in start:
                if len(walkable) > 1 and colinear(walkable[-2], walkable[-1], (x, y)):
                    walkable[-1] = (x, y)
                else:
                    walkable.append((x, y))
                x, y = come_from[x, y]

            if len(walkable) > 1 and colinear(walkable[-2], walkable[-1], (x, y)):
                walkable[-1] = (x, y)
            else:
                walkable.append((x, y))

            if len(walkable) <= 2:
                return np.empty((0, 2), dtype=np.uint32)
            
            return np.array(walkable[-2:0:-1], dtype=np.uint32)
            
    
        for i, j in [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]:
            if bound_check(maze, i, j) and not bound_check(visited, i, j):
                visited[i, j] = True
                come_from[i, j] = [x, y]
                queue.append((i, j))

    assert False, "Maze isn't solvable"


@njit(cache=True)
def make_taut(seq, start, end):
    if seq.shape[0] == 0:
        return distance(start, end), np.empty((0, 2), dtype=np.uint32)
    
    verts = [get_vertices(i) for i in seq]
    come_from = np.full((seq.shape[0], 4), -1)
    dists = np.full((seq.shape[0], 4), np.inf)

    for i in range(4):
        dists[0, i] = distance(start, verts[0][i])

    for i in range(1, seq.shape[0]):
        for j in range(4):
            p = verts[i][j]
            for k in range(4):
                d = dists[i - 1, k] + distance(p, verts[i - 1][k])
                if d < dists[i, j]:
                    dists[i, j] = d
                    come_from[i, j] = k

    come_from_end = -1
    dist_end = np.inf

    for i in range(4):
        d = dists[-1, i] + distance(verts[-1][i], end)
        if d < dist_end:
            dist_end = d
            come_from_end = i
    
    path = []
    i = seq.shape[0] - 1
    j = come_from_end

    while i > 0:
        path.append(verts[i][j])
        j = come_from[i, j]
        i -= 1
    
    path.append(verts[i][j])
    return dist_end, np.array(path[::-1], dtype=np.uint32)


@njit(cache=True)
def solve_maze(maze, start, end):
    start_tiles = [(i, j) for i, j in get_tiles(start) if bound_check(maze, i, j)]
    end_tiles = [(i, j) for i, j in get_tiles(end) if bound_check(maze, i, j)]

    assert len(start_tiles) > 0, "Start not in maze"
    assert len(end_tiles) > 0, "End not in maze"

    tunnel = preprocess(maze, start_tiles, end_tiles)
    return make_taut(tunnel, start, end)
