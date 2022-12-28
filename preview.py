from generator import create_maze
from solver import solve_maze
from renderer import render

from PIL import Image
import sys

if __name__ == "__main__":
    ws = sys.argv[1:]
    hs = sys.argv[2:]
    
    w = int(ws[0]) if len(ws) else 40
    h = int(hs[0]) if len(hs) else w

    maze = create_maze(w, h, 0.1)
    tile_size = 3200 // max(maze.shape)

    offset = (tile_size * maze.shape[0] / 2, tile_size * maze.shape[1] / 2)
    img_width = int(tile_size * (maze.shape[0] + 3))
    img_height = int(tile_size * (maze.shape[1] + 3))

    start = (0.5, 0.5)
    end = (maze.shape[0] - 0.5, maze.shape[1] - 0.5)

    dist, path = solve_maze(maze, start, end)
    buf = render(maze, (img_width, img_height), offset, tile_size, start, end, path)

    img = Image.fromarray(buf)
    img.show()
