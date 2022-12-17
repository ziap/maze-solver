from numba import njit

import heapq as hq
import numpy as np

@njit(cache=True)
def get_edge_heap(heap, nodes):
    while (len(heap) > 0):
        l, r = hq.heappop(heap)[1]
        if not nodes[r]:
            return l, r

    assert False, "Unreachable"


@njit(cache=True)
def get_edge_stack(stack, nodes):
    while (len(stack) > 0):
        l, r = hq.heappop(stack[-1])[1]
        if len(stack[-1]) == 0:
            stack.pop()
        if not nodes[r]:
            return l, r
    
    assert False, "Unreachable"


@njit(cache=True)
def create_maze(width, height, threshold=0.5):
    nodes = np.zeros((width, height), dtype=np.bool8)
    h_edges = np.zeros((width - 1, height), dtype=np.bool8)
    v_edges = np.zeros((width, height - 1), dtype=np.bool8)

    heap = []
    stack = []

    x = np.random.randint(0, width)
    y = np.random.randint(0, height)

    nodes[x, y] = True
    if x > 0:
        heap.append((np.random.rand(), ((x, y), (x - 1, y))))
    if x < width - 1:
        heap.append((np.random.rand(), ((x, y), (x + 1, y))))
    if y > 0:
        heap.append((np.random.rand(), ((x, y), (x, y - 1))))
    if y < height - 1:
        heap.append((np.random.rand(), ((x, y), (x, y + 1))))

    hq.heapify(heap)
    stack.append([i for i in heap])


    remaining = width * height - 1

    while remaining > 0:
        if np.random.rand() < threshold:
            l, r = get_edge_heap(heap, nodes)
        else:
            l, r = get_edge_stack(stack, nodes)

        nodes[r] = True
        remaining -= 1

        if r[0] != l[0]:
            h_edges[min(r[0], l[0]), l[1]] = True
        else:
            v_edges[l[0], min(r[1], l[1])] = True

        x, y = r
        next = []

        if x > 0 and x != l[0] + 1:
            next.append((np.random.rand(), (r, (x - 1, y))))
        if x < width - 1 and x != l[0] - 1:
            next.append((np.random.rand(), (r, (x + 1, y))))
        if y > 0 and y != l[1] + 1:
            next.append((np.random.rand(), (r, (x, y - 1))))
        if y < height - 1 and y != l[1] - 1:
            next.append((np.random.rand(), (r, (x, y + 1))))

        for i in next:
            hq.heappush(heap, i)

        hq.heapify(next)    
        stack.append(next)
    
    maze = np.zeros((2 * (width - 1) + 1, 2 * (height - 1) + 1), dtype=np.bool8)
    maze[::2, ::2] = True
    maze[1::2, ::2] = h_edges
    maze[::2, 1::2] = v_edges
    
    return maze
