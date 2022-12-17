from generator import create_maze
from util import trace_maze
from solver import solve_maze

from time import perf_counter

import sys
import numpy as np
import matplotlib.pyplot as plt


def display(maze, path):
    x, y = trace_maze(maze)
    px = [i[0] for i in path]
    py = [i[1] for i in path]

    fig = plt.figure(figsize=(w / 4, h / 4))
    fig.clear()
    plt.fill(x, y, facecolor='lightblue', edgecolor='blue', linewidth=1.25)
    plt.plot(px, py, color='red', linewidth=2.0)
    plt.savefig('result.png')


def random_point(shape):
    norm = (np.random.normal(0.5, size=2) + 0.5) % 1
    points = norm * (np.array(shape) + 1)
    return (int(points[0]), int(points[1]))

if __name__ == "__main__":
    ws = sys.argv[1:]
    hs = sys.argv[2:]
    
    w = int(ws[0]) if len(ws) else 40
    h = int(hs[0]) if len(hs) else w

    maze = create_maze(w, h, 0.25)
    
    start = random_point(maze.shape)
    end = random_point(maze.shape)
    
    t = perf_counter()
    path = solve_maze(maze, start, end)
    print((perf_counter() - t) * 1000)
    
    display(maze, path)

