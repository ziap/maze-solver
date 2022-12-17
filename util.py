from numba import njit

import numpy as np

@njit(cache=True)
def bound_check(data, x, y):
    width, height = data.shape
    return x >= 0 and x < width and y >= 0 and y < height and data[x, y]

@njit(cache=True)
def trace_maze(maze):
    result_x = [0]
    result_y = [0]

    width, height = maze.shape
    visited = np.zeros((width + 1, height + 1), dtype=np.bool8)

    x, y = 0, 0
    while not (bound_check(maze, x, y) or bound_check(maze, x - 1, y) or bound_check(maze, x, y - 1) or bound_check(maze, x - 1, y - 1)):
        x += 1
        if x == width + 1:
            x = 0
            y += 1

    last = -1
    
    while True:
        visited[x, y] = True
        if bound_check(maze, x, y) != bound_check(maze, x, y - 1) and not bound_check(visited, x + 1, y):
            x += 1
            current = 0
        elif bound_check(maze, x, y) != bound_check(maze, x - 1, y) and not bound_check(visited, x, y + 1):
            y += 1
            current = 1
        elif bound_check(maze, x - 1, y) != bound_check(maze, x - 1, y - 1) and not bound_check(visited, x - 1, y):
            x -= 1
            current = 2
        elif bound_check(maze, x, y - 1) != bound_check(maze, x - 1, y - 1) and not bound_check(visited, x, y - 1):
            y -= 1
            current = 3
        else:
            break
        
        if current == last:
            result_x[-1] = x
            result_y[-1] = y

        else:
            last = current
            result_x.append(x)
            result_y.append(y)
    
    return result_x, result_y
