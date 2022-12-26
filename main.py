import tkinter as tk
import numpy as np
import sys

from tkinter import font
from math import floor
from PIL import Image, ImageTk

from util import bound_check, from_screen, EMPTY_POINT
from renderer import render
from generator import create_maze
from solver import solve_maze

class Display(tk.Label):
    INIT_TILE_SIZE = 10

    def __init__(self, master, maze, display_start, display_end, display_dist):
        tk.Label.__init__(self, master, background='#ffffff')

        self.width = 0
        self.height = 0
        self.tile_size = self.INIT_TILE_SIZE
        self.display_start = display_start
        self.display_end = display_end
        self.display_dist = display_dist
        self.set_start = True

        self.start_pos = EMPTY_POINT
        self.end_pos = EMPTY_POINT
        self.path = np.empty((0, 2))

        self.update_maze(maze)
        self.bind("<Configure>", self.resize)

        self.pressed = False

        self.bind("<Button-1>", self.mouse_down) 
        self.bind("<ButtonRelease-1>", self.mouse_up) 
        self.bind("<Button1-Motion>", self.mouse_move)
        self.bind("<Button-4>", self.mouse_wheel)
        self.bind("<Button-5>", self.mouse_wheel)
        self.bind("<MouseWheel>", self.mouse_wheel)


    def from_screen(self, p):
        return from_screen(p, (self.width, self.height), self.offset, self.tile_size)


    def redraw(self):
        if self.width * self.height > 0:
            buf = render(self.maze, (self.width, self.height), self.offset, self.tile_size, self.start_pos, self.end_pos, self.path)
            img = Image.fromarray(buf)
            self.image = ImageTk.PhotoImage(img)
            self.configure(image=self.image)


    def update_maze(self, new_maze):
        self.maze = new_maze
        maze_w, maze_h = self.maze.shape

        self.tile_size = self.INIT_TILE_SIZE
        self.offset = (self.tile_size * maze_w / 2, self.tile_size * maze_h / 2)
        self.start_pos = EMPTY_POINT
        self.end_pos = EMPTY_POINT
        self.set_start = True
        self.path = np.empty((0, 2))
        self.redraw()


    def resize(self, event):
        self.width = event.width // 2 * 2
        self.height = event.height // 2 * 2

        self.configure(width=event.width, height=event.height)
        self.redraw()


    def mouse_down(self, e):
        x, y = self.offset
        self.last_x = x + e.x
        self.last_y = y + e.y

        self.last_offset = self.offset

    
    def mouse_up(self, e):
        last_x, last_y = self.last_offset
        dx = abs(self.last_x - e.x - last_x)
        dy = abs(self.last_y - e.y - last_y)
        if max(dx, dy) < self.tile_size / 10:
            x, y = self.from_screen((e.x, e.y))
            x_tile, y_tile = floor(x), floor(y)
            
            if bound_check(self.maze, x_tile, y_tile):
                if self.set_start:
                    self.start_pos = (x, y)
                    self.display_start(x, y)
                else:
                    self.end_pos = (x, y)
                    self.display_end(x, y)
                
                if self.end_pos != EMPTY_POINT:
                    dist, self.path = solve_maze(self.maze, self.start_pos, self.end_pos)
                    self.display_dist(dist)
                self.set_start = not self.set_start
                self.redraw()


    def mouse_move(self, e):
        self.offset = (self.last_x - e.x, self.last_y - e.y)
        self.redraw()


    def mouse_wheel(self, e):
        x, y = self.offset
        
        x += e.x - self.width / 2
        y += e.y - self.height / 2
        x /= self.tile_size
        y /= self.tile_size

        if e.delta:
            self.tile_size += e.delta / 120
        else:
            self.tile_size += 1 if e.num == 4 else -1
            self.tile_size = max(self.tile_size, 3)

        x *= self.tile_size
        y *= self.tile_size
        x -= e.x - self.width / 2
        y -= e.y - self.height / 2

        self.offset = (x, y)
        self.redraw()


class App(tk.Tk):
    INIT_WIDTH = 1024
    INIT_HEIGHT = 768
    PADDING = 10
    FONT_SIZE = 10

    MAZE_BRANCHING = 0.25


    def __init__(self, maze_width, maze_height):
        tk.Tk.__init__(self, className="mazesolver")

        self.title("Maze solver")
        self.geometry(f"{self.INIT_WIDTH}x{self.INIT_HEIGHT}")

        self.inp_width = tk.StringVar(value=maze_width)
        self.inp_height = tk.StringVar(value=maze_height)

        self.start_pos = EMPTY_POINT
        self.end_pos = EMPTY_POINT

        self.display_start = tk.StringVar(value="Start: (---, ---)")
        self.display_end = tk.StringVar(value="End: (---, ---)")
        self.display_dist = tk.StringVar(value="Distance: ---")
        
        self.font = font.Font(size=self.FONT_SIZE)

        self.top_frame().pack(padx=self.PADDING / 2, pady=self.PADDING, fill='x')

        maze = create_maze(maze_width, maze_height, self.MAZE_BRANCHING)
            
        update_start = lambda x, y: self.display_start.set(f"Start: ({x:.2f}, {y:.2f})")
        update_end = lambda x, y: self.display_end.set(f"End: ({x:.2f}, {y:.2f})")
        update_dist = lambda d: self.display_dist.set(f"Distance: {d:.2f}")

        self.renderer = Display(self, maze, update_start, update_end, update_dist)
        self.renderer.pack(fill=tk.BOTH, expand=tk.YES)


    def create_maze(self):
        w_str = self.inp_width.get()
        h_str = self.inp_height.get()

        if w_str == "" or h_str == "":
            return

        w = int(w_str)
        h = int(h_str)

        self.start_pos = EMPTY_POINT
        self.end_pos = EMPTY_POINT
        self.display_start.set("Start: (---, ---)")
        self.display_end.set("End: (---, ---)")
        self.display_dist.set("Distance: ---")

        maze = create_maze(w, h, self.MAZE_BRANCHING)
        self.renderer.update_maze(maze)


    def generator_menu(self, master):
        frame = tk.Frame(master)

        vcmd = (self.register(lambda p: p == "" or p.isdigit()), "%P")
        tk.Label(frame, text="Width:", font=self.font).pack(side=tk.LEFT, padx=self.PADDING / 2)
        tk.Entry(frame, width=6, textvariable=self.inp_width, font=self.font, validate=tk.ALL, validatecommand=vcmd).pack(side=tk.LEFT, padx=self.PADDING / 2)

        tk.Label(frame, text="Height:", font=self.font).pack(side=tk.LEFT, padx=self.PADDING / 2)
        tk.Entry(frame, width=6, textvariable=self.inp_height, font=self.font, validate=tk.ALL, validatecommand=vcmd).pack(side=tk.LEFT, padx=self.PADDING / 2)

        tk.Button(frame, text="Generate Maze", font=self.font, command=self.create_maze).pack(side=tk.LEFT, padx=self.PADDING / 2)

        return frame


    def display_menu(self, master):
        frame = tk.Frame(master)
        
        tk.Label(frame, textvariable=self.display_start, font=self.font).pack(side=tk.LEFT, padx=self.PADDING / 2)
        tk.Label(frame, textvariable=self.display_end, font=self.font).pack(side=tk.LEFT, padx=self.PADDING / 2)
        tk.Label(frame, textvariable=self.display_dist, font=self.font).pack(side=tk.LEFT, padx=self.PADDING / 2)

        return frame


    def top_frame(self):
        frame = tk.Frame(self)

        self.generator_menu(frame).pack(side=tk.LEFT, expand=1, anchor=tk.W)
        self.display_menu(frame).pack(side=tk.LEFT, expand=1, anchor=tk.E)

        return frame 


if __name__ == "__main__":
    ws = sys.argv[1:]
    hs = sys.argv[2:]
    
    w = int(ws[0]) if len(ws) else 40
    h = int(hs[0]) if len(hs) else w

    App(w, h).mainloop()
