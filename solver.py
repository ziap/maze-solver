from numba import njit
from math import floor, ceil

import numpy as np
import heapq as hq

from util import bound_check

@njit(cache=True)
def preprocess(maze, start, end):
    visited = np.zeros(maze.shape, dtype=np.bool8)
    come_from = np.full((*maze.shape, 2), -1)
    queue = [start]
    front = 0

    while front < len(queue):
        x, y = queue[front]
        front += 1

        if (x, y) == end:
            walkable = np.zeros(maze.shape, dtype=np.bool8)
            while (x, y) != start:
                walkable[x, y] = True
                x, y = come_from[x, y]

            walkable[x, y] = True
            return walkable
        
        for i, j in [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]:
            if bound_check(maze, i, j) and not bound_check(visited, i, j):
                visited[i, j] = True
                come_from[i, j] = [x, y]
                queue.append((i, j))


@njit(cache=True)
def pathfind(maze, start, end):
    width, height = maze.shape
    sqrt2 = np.sqrt(2)

    g = np.full((width + 1, height + 1), np.inf)
    come_from = np.full((width + 1, height + 1, 2), -1)

    g[start] = 0
    open = [(g[start], start)]

    hq.heapify(open)

    while len(open) > 0:
        _, (x, y) = hq.heappop(open)

        if (x, y) == end:
            path = []

            while (x, y) != start:
                path.append((x, y))
                x, y = come_from[x, y]
            path.append(start)

            return path

        neighbors = []
        if bound_check(maze, x, y) or bound_check(maze, x, y - 1):
            neighbors.append((1, x + 1, y))
        if bound_check(maze, x, y) or bound_check(maze, x - 1, y):
            neighbors.append((1, x, y + 1))
        if bound_check(maze, x - 1, y) or bound_check(maze, x - 1, y - 1):
            neighbors.append((1, x - 1, y))
        if bound_check(maze, x, y - 1) or bound_check(maze, x - 1, y - 1):
            neighbors.append((1, x, y - 1))
        
        if bound_check(maze, x, y):
            neighbors.append((sqrt2, x + 1, y + 1))
        if bound_check(maze, x, y - 1):
            neighbors.append((sqrt2, x + 1, y - 1))
        if bound_check(maze, x - 1, y):
            neighbors.append((sqrt2, x - 1, y + 1))
        if bound_check(maze, x - 1, y - 1):
            neighbors.append((sqrt2, x - 1, y - 1))

        for w, i, j in neighbors:
            if g[i, j] > g[x, y] + w:
                g[i, j] = g[x, y] + w
                come_from[i, j] = [x, y]
                hq.heappush(open, (g[i, j], (i, j)))

    assert False, "Maze isn't solvable"


@njit(cache=True)
def get_tiles(p):
    x, y = p
    tiles = set()
    for i in (floor(x), ceil(x) - 1):
        for j in (floor(y), ceil(y) - 1):
            if (i, j) not in tiles:
                tiles.add((i, j))

    return tiles


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
    start_tile, end_tile = (-1, -1), (-1, -1)

    for i, j in get_tiles(start):
        if bound_check(maze, i, j):
            start_tile = (i, j)
            break

    for i, j in get_tiles(end):
        if bound_check(maze, i, j):
            end_tile = (i, j)
            break

    assert start_tile != (-1, -1), "Start not in maze"
    assert end_tile != (-1, -1), "End not in maze"

    tunnel = preprocess(maze, start_tile, end_tile)
    path = pathfind(tunnel, start, end)

    stop = False
    while not stop:
        stop = True
        tmp_path = []

        for p in path:
            if len(tmp_path) > 1 and visible(tunnel, p, tmp_path[-2]):
                tmp_path[-1] = p
                stop = False
            else:
                tmp_path.append(p)
        path = tmp_path

    return path
