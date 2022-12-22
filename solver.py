from numba import njit
from math import floor, ceil

import numpy as np

from util import bound_check


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
    return set([
        (x, y),
        (x + 1, y),
        (x, y + 1),
        (x + 1, y + 1)
    ])


@njit(cache=True)
def colinear(a, b, c):
    xa, ya = a
    xb, yb = b
    xc, yc = c
    val = (yb - ya) * (xc - xb) - (xb - xa) * (yc - yb)
    return val == 0


@njit(cache=True)
def preprocess(maze, start, end):
    visited = np.zeros(maze.shape, dtype=np.bool8)
    come_from = np.full((*maze.shape, 2), -1)
    queue = [start[0]]
    front = 0

    while front < len(queue):
        x, y = queue[front]
        front += 1

        if (x, y) in end:
            walkable = []
            while not (x, y) in start:
                walkable.append((x, y))
                x, y = come_from[x, y]
            
            walkable.append((x, y))
            return walkable
        
        for i, j in [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]:
            if bound_check(maze, i, j) and not bound_check(visited, i, j):
                visited[i, j] = True
                come_from[i, j] = [x, y]
                queue.append((i, j))


@njit(cache=True)
def pathfind(tunnel, shape):
    width, height = shape

    walkable = set(tunnel)

    visited = np.zeros((width + 1, height + 1))
    come_from = np.full((width + 1, height + 1, 2), -1)

    start_vertices = get_vertices(tunnel[0])
    end_vertices = get_vertices(tunnel[-1])

    queue = [i for i in start_vertices]
    front = len(queue) - 1

    while front < len(queue):
        x, y = queue[front]
        front += 1

        if (x, y) in end_vertices:
            path = []

            while not (x, y) in start_vertices:
                path.append((x, y))
                x, y = come_from[x, y]

            path.append((x, y))

            return path

        neighbors = []
        if (x, y) in walkable or (x, y - 1) in walkable:
            neighbors.append((x + 1, y))
        if (x, y) in walkable or (x - 1, y) in walkable:
            neighbors.append((x, y + 1))
        if (x - 1, y) in walkable or (x - 1, y - 1) in walkable:
            neighbors.append((x - 1, y))
        if (x, y - 1) in walkable or (x - 1, y - 1) in walkable:
            neighbors.append((x, y - 1))
        
        if (x, y) in walkable:
            neighbors.append((x + 1, y + 1))
        if (x, y - 1) in walkable:
            neighbors.append((x + 1, y - 1))
        if (x - 1, y) in walkable:
            neighbors.append((x - 1, y + 1))
        if (x - 1, y - 1) in walkable:
            neighbors.append((x - 1, y - 1))

        for i, j in neighbors:
            if not bound_check(visited, i, j):
                visited[i, j] = True
                come_from[i, j] = [x, y]
                queue.append((i, j))

    assert False, "Maze isn't solvable"


@njit(cache=True)
def visible(maze, p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    d = max(abs(dx), abs(dy))

    if d == 1:
        d = 2

    dx, dy = dx / d, dy / d
    x, y = p1[0] + dx, p1[1] + dy

    p2_f = (float(p2[0]), float(p2[1]))

    while not np.allclose((x, y), p2_f, 1e-5, 1e-8, False):
        for i, j in get_tiles((x, y)):
            if not bound_check(maze, i, j):
                return False

        x += dx
        y += dy

    return True


@njit(cache=True)
def solve_maze(maze, start, end):
    start_tiles = [(i, j) for i, j in get_tiles(start) if bound_check(maze, i, j)]
    end_tiles = [(i, j) for i, j in get_tiles(end) if bound_check(maze, i, j)]

    assert len(start_tiles) > 0, "Start not in maze"
    assert len(end_tiles) > 0, "End not in maze"

    tunnel = preprocess(maze, start_tiles, end_tiles)
    path = pathfind(tunnel, maze.shape)

    stop = False
    while not stop:
        stop = True
        tmp_path = []

        for p in path:
            if len(tmp_path) > 1 and visible(maze, p, tmp_path[-2]):
                tmp_path[-1] = p
                stop = False
            else:
                tmp_path.append(p)
        path = tmp_path

    result_path = []
    
    for x, y in path:
        if len(result_path) > 1 and colinear(result_path[-2], result_path[-1], (x, y)):
            result_path[-1] = (float(x), float(y))
        else:
            result_path.append((float(x), float(y)))

    result_path[0] = start
    result_path[-1] = end
    return result_path
