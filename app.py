from flask import Flask, render_template, jsonify, request
import random
from collections import deque
import heapq

app = Flask(__name__)

# Maze dimensions
ROWS, COLS = 25, 35
WALL, PATH = 1, 0


# ----------- Maze Generation -----------
def generate_maze():
    maze = [[WALL for _ in range(COLS)] for _ in range(ROWS)]

    def carve_from(r, c):
        maze[r][c] = PATH
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == WALL:
                maze[r + dr // 2][c + dc // 2] = PATH
                carve_from(nr, nc)

    carve_from(0, 0)
    maze[0][0] = PATH
    maze[ROWS - 1][COLS - 1] = PATH
    return maze


# ----------- BFS -----------
def bfs_with_exploration(maze, start, end):
    ROWS, COLS = len(maze), len(maze[0])
    q = deque([start])
    parent = {start: None}
    explored = []
    found = False

    while q:
        node = q.popleft()
        explored.append(node)
        if node == end:
            found = True
            break
        r, c = node
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            n = (nr, nc)
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == PATH and n not in parent:
                parent[n] = node
                q.append(n)

    path = []
    if found:
        cur = end
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
    return explored, path


# ----------- A* -----------
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_with_exploration(maze, start, end):
    ROWS, COLS = len(maze), len(maze[0])
    gscore = {start: 0}
    fscore = {start: manhattan(start, end)}
    parent = {}
    open_heap = [(fscore[start], start)]
    open_set = {start}
    closed = set()
    explored = []

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        open_set.discard(current)
        closed.add(current)
        explored.append(current)

        if current == end:
            break

        r, c = current
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if maze[nr][nc] == WALL:
                continue
            tentative_g = gscore[current] + 1
            if tentative_g < gscore.get(neighbor, float("inf")):
                parent[neighbor] = current
                gscore[neighbor] = tentative_g
                fscore[neighbor] = tentative_g + manhattan(neighbor, end)
                if neighbor not in open_set and neighbor not in closed:
                    heapq.heappush(open_heap, (fscore[neighbor], neighbor))
                    open_set.add(neighbor)

    path = []
    if end in parent or start == end:
        cur = end
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur, None)
        path.reverse()
    return explored, path

# ----------- DFS -----------
def dfs_with_exploration(maze, start, end):
    stack = [start]
    visited = set([start])
    parent = {}
    explored = []

    while stack:
        node = stack.pop()
        explored.append(node)
        if node == end:
            break
        r, c = node
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            n = (nr, nc)
            if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] == PATH and n not in visited:
                visited.add(n)
                parent[n] = node
                stack.append(n)

    path = []
    if end in parent or start == end:
        cur = end
        while cur in parent or cur == start:
            path.append(cur)
            if cur == start: break
            cur = parent[cur]
        path.reverse()
    return explored, path

# ----------- Dijkstra -----------
def dijkstra_with_exploration(maze, start, end):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(0, start)]
    dist = {start: 0}
    parent = {}
    explored = []

    while pq:
        cost, node = heapq.heappop(pq)
        explored.append(node)
        if node == end:
            break

        r, c = node
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            n = (nr, nc)
            if not (0 <= nr < ROWS and 0 <= nc < COLS): continue
            if maze[nr][nc] == WALL: continue
            new_cost = cost + 1
            if new_cost < dist.get(n, float("inf")):
                dist[n] = new_cost
                parent[n] = node
                heapq.heappush(pq, (new_cost, n))

    path = []
    if end in parent or start == end:
        cur = end
        while cur in parent or cur == start:
            path.append(cur)
            if cur == start: break
            cur = parent[cur]
        path.reverse()
    return explored, path

# ----------- Greedy Best-First Search -----------
def greedy_best_first(maze, start, end):
    ROWS, COLS = len(maze), len(maze[0])
    open_heap = [(manhattan(start, end), start)]
    parent = {}
    visited = set()
    explored = []

    while open_heap:
        _, node = heapq.heappop(open_heap)
        if node in visited:
            continue
        visited.add(node)
        explored.append(node)
        if node == end:
            break

        r, c = node
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            n = (nr, nc)
            if not (0 <= nr < ROWS and 0 <= nc < COLS): continue
            if maze[nr][nc] == WALL or n in visited: continue
            parent[n] = node
            heapq.heappush(open_heap, (manhattan(n, end), n))

    path = []
    if end in parent or start == end:
        cur = end
        while cur in parent or cur == start:
            path.append(cur)
            if cur == start: break
            cur = parent[cur]
        path.reverse()
    return explored, path

# ----------- Bidirectional BFS -----------
def bidirectional_bfs(maze, start, end):
    from collections import deque
    ROWS, COLS = len(maze), len(maze[0])
    q1, q2 = deque([start]), deque([end])
    visited1, visited2 = {start: None}, {end: None}
    explored = []

    meet_point = None

    while q1 and q2:
        # Expand forward search
        for _ in range(len(q1)):
            node = q1.popleft()
            explored.append(node)
            if node in visited2:
                meet_point = node
                break
            r, c = node
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                n = (nr, nc)
                if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == PATH and n not in visited1:
                    visited1[n] = node
                    q1.append(n)

        if meet_point: break

        # Expand backward search
        for _ in range(len(q2)):
            node = q2.popleft()
            explored.append(node)
            if node in visited1:
                meet_point = node
                break
            r, c = node
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                n = (nr, nc)
                if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == PATH and n not in visited2:
                    visited2[n] = node
                    q2.append(n)

        if meet_point: break

    path = []
    if meet_point:
        # reconstruct from both sides
        node = meet_point
        while node is not None:
            path.append(node)
            node = visited1[node]
        path.reverse()
        node = visited2[meet_point]
        while node is not None:
            path.append(node)
            node = visited2[node]
    return explored, path



# ----------- Routes -----------
@app.route("/")
def index():
    return render_template("index.html")

# below is the original generate route without parameters a static maze size
# @app.route("/generate")
# def generate():
#     maze = generate_maze()
#     return jsonify(maze)

# below will allow difficulty parameters here has the option to set rows and cols via query parameters
@app.route("/generate")
def generate():
    # Get optional difficulty parameters from the request
    rows = int(request.args.get("rows", 25))
    cols = int(request.args.get("cols", 35))
    
    global ROWS, COLS
    ROWS, COLS = rows, cols

    maze = generate_maze()
    return jsonify(maze)



# @app.route("/solve", methods=["POST"])
# def solve():
#     data = request.json
#     maze = data.get("maze")
#     start = tuple(data.get("start", (0, 0)))
#     end = tuple(data.get("end", (len(maze) - 1, len(maze[0]) - 1)))
#     algo = data.get("algo", "astar")

#     if algo == "bfs":
#         explored, path = bfs_with_exploration(maze, start, end)
#     else:
#         explored, path = astar_with_exploration(maze, start, end)

#     return jsonify({
#         "explored": [[r, c] for r, c in explored],
#         "path": [[r, c] for r, c in path]
#     })

@app.route("/solve", methods=["POST"])
def solve():
    data = request.json
    maze = data.get("maze")
    start = tuple(data.get("start", (0, 0)))
    end = tuple(data.get("end", (len(maze) - 1, len(maze[0]) - 1)))
    algo = data.get("algo", "astar")

    if algo == "bfs":
        explored, path = bfs_with_exploration(maze, start, end)
    elif algo == "dfs":
        explored, path = dfs_with_exploration(maze, start, end)
    elif algo == "dijkstra":
        explored, path = dijkstra_with_exploration(maze, start, end)
    elif algo == "greedy":
        explored, path = greedy_best_first(maze, start, end)
    elif algo == "bidirectional":
        explored, path = bidirectional_bfs(maze, start, end)
    else:
        explored, path = astar_with_exploration(maze, start, end)

    return jsonify({
        "explored": [[r, c] for r, c in explored],
        "path": [[r, c] for r, c in path]
    })


if __name__ == "__main__":
    app.run(debug=True)
