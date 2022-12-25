from numba import njit, prange
import numpy as np

from math import floor
from util import bound_check, from_screen


COLOR_FILL = np.array([191, 219, 254])
COLOR_OUTLINE = np.array([7, 99, 235])
COLOR_PATH = np.array([250, 204, 21], dtype=np.uint8)

COLOR_BACKGROUND = np.array([255, 255, 255], dtype=np.uint8)
COLOR_START = np.array([22, 163, 74], dtype=np.uint8)
COLOR_END = np.array([220, 38, 38], dtype=np.uint8)

LINE_WIDTH = 1 / 20
DOT_RADIUS = 3 / 20


@njit(cache=True)
def place_dot(buf, p1, p2, u, v, color):
    if p2 == (-1, -1):
        return False
    x1, y1 = p1
    x2, y2 = p2

    dx = x1 - x2
    dy = y1 - y2

    if dx * dx + dy * dy < DOT_RADIUS * DOT_RADIUS:
        buf[u, v] = color
        return True
    
    return False


@njit(cache=True, parallel=True)
def render(maze, size, offset, scale, start, end, path):
    w, h = size
    buf = np.zeros((h, w, 3), dtype=np.uint8)

    path_verts = set()
    for x, y in path:
        path_verts.add((x, y))

    line_width = max(LINE_WIDTH * scale, 1)
    if LINE_WIDTH * scale < 1:
        line_color = (COLOR_FILL + (COLOR_OUTLINE - COLOR_FILL) * LINE_WIDTH * scale).astype(np.uint8)
    else:
        line_color = COLOR_OUTLINE.astype(np.uint8)


    dot_radius_sqr = scale * scale * DOT_RADIUS * DOT_RADIUS

    for i in prange(h):
        for j in range(w):
            x, y = from_screen((j, i), size, offset, scale)

            if place_dot(buf, (x, y), start, i, j, COLOR_START):
                continue

            if place_dot(buf, (x, y), end, i, j, COLOR_END):
                continue

            tile_x, tile_y = floor(x), floor(y)
            tiles = (
                bound_check(maze, tile_x, tile_y),
                bound_check(maze, tile_x - 1, tile_y),
                bound_check(maze, tile_x + 1, tile_y),
                bound_check(maze, tile_x, tile_y - 1),
                bound_check(maze, tile_x, tile_y + 1),
                bound_check(maze, tile_x + 1, tile_y + 1),
                bound_check(maze, tile_x + 1, tile_y - 1),
                bound_check(maze, tile_x - 1, tile_y - 1),
                bound_check(maze, tile_x - 1, tile_y + 1)
            )
            
            xl = scale * (x - tile_x)
            yl = scale * (y - tile_y)
            xr = scale - xl - 1
            yr = scale - yl - 1

            if xl * xl + yl * yl < dot_radius_sqr and (tiles[0] + tiles[1] + tiles[3] + tiles[7]) % 2 == 1:
                buf[i, j] = COLOR_PATH if (tile_x, tile_y) in path_verts else line_color
            elif xr * xr + yl * yl < dot_radius_sqr and (tiles[0] + tiles[2] + tiles[3] + tiles[6]) % 2 == 1:
                buf[i, j] = COLOR_PATH if (tile_x + 1, tile_y) in path_verts else line_color
            elif xl * xl + yr * yr < dot_radius_sqr and (tiles[0] + tiles[1] + tiles[4] + tiles[8]) % 2 == 1:
                buf[i, j] = COLOR_PATH if (tile_x, tile_y + 1) in path_verts else line_color
            elif xr * xr + yr * yr < dot_radius_sqr and (tiles[0] + tiles[2] + tiles[4] + tiles[5]) % 2 == 1:
                buf[i, j] = COLOR_PATH if (tile_x + 1, tile_y + 1) in path_verts else line_color
            elif (xl < line_width) and (tiles[0] != tiles[1]):
                buf[i, j] = line_color
            elif (xr < line_width) and (tiles[0] != tiles[2]):
                buf[i, j] = line_color
            elif (yl < line_width) and (tiles[0] != tiles[3]):
                buf[i, j] = line_color
            elif (yr < line_width) and (tiles[0] != tiles[4]):
                buf[i, j] = line_color
            elif tiles[0]:
                buf[i, j] = COLOR_FILL
            else:
                buf[i, j] = COLOR_BACKGROUND
    
    return buf


