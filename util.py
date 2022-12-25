from numba import njit
import numpy as np

EMPTY_POINT = (-1, -1)


@njit(cache=True)
def bound_check(data, x, y):
    width, height = data.shape
    return x >= 0 and x < width and y >= 0 and y < height and data[x, y]


@njit(cache=True)
def from_screen(p, size, offset, scale):
    x, y = p
    w, h = size
    off_x, off_y = offset
    return ((x - w / 2 + off_x) / scale, (y - h / 2 + off_y) / scale)


@njit(cache=True)
def to_screen(p, size, offset, scale):
    x, y = p
    w, h = size
    off_x, off_y = offset
    return (int(x * scale + w / 2 - off_x), int(y * scale + h / 2 - off_y))


@njit(cache=True)
def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1

    return np.sqrt(dx * dx + dy * dy)
