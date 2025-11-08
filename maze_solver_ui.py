"""
maze_solver_ui.py
Interactive Maze Solver with Tkinter
- Generate random maze (recursive backtracker)
- Click to toggle walls
- Right-click to set Start/End (first right-click = Start, second = End, then toggles)
- Solve with BFS or A* (animated)
- Speed control slider

Run: python maze_solver_ui.py
"""

import tkinter as tk
from tkinter import ttk
import random
import time
import heapq
from collections import deque

# ---------- Config ----------
ROWS = 25
COLS = 35
CELL_SIZE = 22
WALL = 1
PATH = 0

# Colors
COLOR_PATH = "white"
COLOR_WALL = "black"
COLOR_START = "green"
COLOR_END = "red"
COLOR_VISITED = "lightblue"
COLOR_FRONTIER = "cyan"
COLOR_FINAL_PATH = "yellow"

# ---------- Maze and UI state ----------
maze = [[WALL for _ in range(COLS)] for _ in range(ROWS)]
start = (0, 0)
end = (ROWS - 1, COLS - 1)
placing_start = True  # toggles when user right-clicks first/second
animating = False

# ---------- Tkinter setup ----------
root = tk.Tk()
root.title("Intelligent Maze Solver — BFS and A*")

canvas_width = COLS * CELL_SIZE
canvas_height = ROWS * CELL_SIZE

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

# Speed slider label
speed_var = tk.DoubleVar(value=0.01)

# ---------- Utility functions ----------
def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def neighbors(r, c):
    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc):
            yield nr, nc

# ---------- Drawing ----------
rect_ids = [[None]*COLS for _ in range(ROWS)]

def draw_cell(r, c, color):
    x1 = c * CELL_SIZE
    y1 = r * CELL_SIZE
    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE
    if rect_ids[r][c] is None:
        rect_ids[r][c] = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
    else:
        canvas.itemconfig(rect_ids[r][c], fill=color)
    return rect_ids[r][c]

def draw_maze():
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == WALL:
                draw_cell(r, c, COLOR_WALL)
            else:
                draw_cell(r, c, COLOR_PATH)
    sr, sc = start
    er, ec = end
    draw_cell(sr, sc, COLOR_START)
    draw_cell(er, ec, COLOR_END)

# ---------- Maze generation: Recursive Backtracker ----------
def carve_maze():
    # Start with grid of walls, carve cells (odd indices) to make paths
    global maze
    maze = [[WALL for _ in range(COLS)] for _ in range(ROWS)]
    # ensure odd rows/cols for cells when possible — but we just use backtracker that moves 2 steps
    def carve_from(r, c):
        maze[r][c] = PATH
        dirs = [(0,2),(0,-2),(2,0),(-2,0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if in_bounds(nr, nc) and maze[nr][nc] == WALL:
                # remove wall between
                maze[r + dr//2][c + dc//2] = PATH
                carve_from(nr, nc)
    # choose a random starting cell with odd coordinates (if possible)
    sr = random.randrange(0, ROWS, 2)
    sc = random.randrange(0, COLS, 2)
    carve_from(sr, sc)
    # Ensure start and end are path
    maze[start[0]][start[1]] = PATH
    maze[end[0]][end[1]] = PATH
    draw_maze()

# ---------- Mouse interactions ----------
def toggle_wall(event):
    if animating:
        return
    c = event.x // CELL_SIZE
    r = event.y // CELL_SIZE
    if not in_bounds(r, c):
        return
    # left click toggles wall/path, but don't override start/end
    if (r, c) == start or (r, c) == end:
        return
    maze[r][c] = PATH if maze[r][c] == WALL else WALL
    draw_maze()

def set_start_end(event):
    # right click: first sets start, second sets end, then alternates
    global placing_start, start, end
    if animating:
        return
    c = event.x // CELL_SIZE
    r = event.y // CELL_SIZE
    if not in_bounds(r, c):
        return
    if placing_start:
        # make sure not placing on wall
        maze[r][c] = PATH
        start = (r, c)
    else:
        maze[r][c] = PATH
        end = (r, c)
    placing_start = not placing_start
    draw_maze()

canvas.bind("<Button-1>", toggle_wall)  # left click
canvas.bind("<Button-3>", set_start_end)  # right click (set start/end)

# ---------- Search algorithms (animated) ----------
def animate_delay():
    # small delay controlled by slider
    d = speed_var.get()
    root.update()
    time.sleep(d)

def reconstruct_and_draw(parent, finish):
    # Reconstruct path from finish to start using parent dict {node: parent}
    node = finish
    path = []
    while node and node in parent:
        path.append(node)
        node = parent[node]
    # Draw final path (excluding start & end if you like)
    for r, c in reversed(path):
        if (r, c) == start or (r, c) == end:
            continue
        draw_cell(r, c, COLOR_FINAL_PATH)
        animate_delay()
    draw_cell(start[0], start[1], COLOR_START)
    draw_cell(end[0], end[1], COLOR_END)

def bfs_solve():
    global animating
    if animating:
        return
    animating = True
    sr, sc = start
    er, ec = end
    visited = set()
    parent = {}
    q = deque()
    q.append((sr, sc))
    visited.add((sr, sc))
    found = False

    while q:
        r, c = q.popleft()
        # draw as visited
        if (r, c) != start and (r, c) != end:
            draw_cell(r, c, COLOR_VISITED)
        animate_delay()
        if (r, c) == (er, ec):
            found = True
            break
        for nr, nc in neighbors(r, c):
            if maze[nr][nc] == WALL:
                continue
            if (nr, nc) in visited:
                continue
            visited.add((nr, nc))
            parent[(nr, nc)] = (r, c)
            q.append((nr, nc))
            # optionally draw frontier
            if (nr, nc) != end:
                draw_cell(nr, nc, COLOR_FRONTIER)
        animate_delay()

    if found:
        reconstruct_and_draw(parent, (er, ec))
    else:
        tk.messagebox.showinfo("Result", "No path found.")
    animating = False

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar_solve():
    global animating
    if animating:
        return
    animating = True
    sr, sc = start
    er, ec = end
    start_node = (sr, sc)
    goal = (er, ec)

    gscore = {start_node: 0}
    fscore = {start_node: manhattan(start_node, goal)}
    parent = {}

    open_heap = []
    heapq.heappush(open_heap, (fscore[start_node], start_node))
    open_set = {start_node}
    closed = set()
    found = False

    while open_heap:
        _, current = heapq.heappop(open_heap)
        open_set.discard(current)
        if current in closed:
            continue
        r, c = current

        if current == goal:
            found = True
            break

        closed.add(current)
        # mark visited
        if current != start and current != end:
            draw_cell(r, c, COLOR_VISITED)
        animate_delay()

        for nr, nc in neighbors(r, c):
            if maze[nr][nc] == WALL:
                continue
            tentative_g = gscore[current] + 1
            neighbor = (nr, nc)
            if neighbor in closed and tentative_g >= gscore.get(neighbor, float('inf')):
                continue
            if tentative_g < gscore.get(neighbor, float('inf')):
                parent[neighbor] = current
                gscore[neighbor] = tentative_g
                fscore[neighbor] = tentative_g + manhattan(neighbor, goal)
                if neighbor not in open_set:
                    heapq.heappush(open_heap, (fscore[neighbor], neighbor))
                    open_set.add(neighbor)
                    if neighbor != end:
                        draw_cell(nr, nc, COLOR_FRONTIER)
        animate_delay()

    if found:
        reconstruct_and_draw(parent, goal)
    else:
        tk.messagebox.showinfo("Result", "No path found.")
    animating = False

# ---------- Controls ----------
def on_generate():
    if animating:
        return
    carve_maze()

def clear_paths():
    if animating:
        return
    # redraw maze cells leaving walls in place, reset any visited/path colors
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == WALL:
                draw_cell(r, c, COLOR_WALL)
            else:
                draw_cell(r, c, COLOR_PATH)
    draw_cell(start[0], start[1], COLOR_START)
    draw_cell(end[0], end[1], COLOR_END)

def reset_maze_empty():
    if animating:
        return
    for r in range(ROWS):
        for c in range(COLS):
            maze[r][c] = PATH
    # set border walls if you want — keep open
    draw_maze()

def on_bfs():
    # run BFS in a non-blocking way? we run it directly (with small sleeps), UI remains responsive enough
    clear_paths()
    root.update()
    bfs_solve()

def on_astar():
    clear_paths()
    root.update()
    astar_solve()

def on_reset_start_end():
    global start, end
    start = (0, 0)
    end = (ROWS - 1, COLS - 1)
    draw_maze()

# ---------- Buttons / UI ----------
btn_gen = ttk.Button(root, text="Generate Maze", command=on_generate)
btn_gen.grid(row=1, column=0, padx=4, pady=6)

btn_bfs = ttk.Button(root, text="Solve (BFS)", command=on_bfs)
btn_bfs.grid(row=1, column=1, padx=4)

btn_astar = ttk.Button(root, text="Solve (A*)", command=on_astar)
btn_astar.grid(row=1, column=2, padx=4)

btn_clear = ttk.Button(root, text="Clear Paths", command=clear_paths)
btn_clear.grid(row=1, column=3, padx=4)

btn_reset = ttk.Button(root, text="Reset Start/End", command=on_reset_start_end)
btn_reset.grid(row=1, column=4, padx=4)

btn_empty = ttk.Button(root, text="Empty Maze", command=reset_maze_empty)
btn_empty.grid(row=1, column=5, padx=4)

# Speed slider
tk.Label(root, text="Animation speed (s)").grid(row=2, column=0, pady=(0,10))
speed_slider = tk.Scale(root, variable=speed_var, from_=0.0, to=0.15, orient="horizontal", resolution=0.005, length=200)
speed_slider.grid(row=2, column=1, columnspan=2, pady=(0,10), sticky="w")

# Instructions text
instr_text = (
    "Left-click to toggle wall/path.\n"
    "Right-click to set Start (first) and End (second).\n"
    "Generate -> Solve (BFS/A*)."
)
instr_label = tk.Label(root, text=instr_text, justify="left")
instr_label.grid(row=2, column=3, columnspan=3, sticky="w")

# ---------- Initialize ----------
carve_maze()

# Draw grid lines optional (commented out to keep clean)
# for i in range(ROWS+1):
#     canvas.create_line(0, i*CELL_SIZE, canvas_width, i*CELL_SIZE, fill="gray")
# for j in range(COLS+1):
#     canvas.create_line(j*CELL_SIZE, 0, j*CELL_SIZE, canvas_height, fill="gray")

# ---------- Start Tk loop ----------
root.mainloop()
