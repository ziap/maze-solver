from gui import App

import sys
import numpy as np

def random_point(shape):
    norm = (np.random.normal(0.5, size=2) + 0.5) % 1
    points = norm * (np.array(shape) + 1)
    return (int(points[0]), int(points[1]))

if __name__ == "__main__":
    ws = sys.argv[1:]
    hs = sys.argv[2:]
    
    w = int(ws[0]) if len(ws) else 40
    h = int(hs[0]) if len(hs) else w

    App(w, h).mainloop()
