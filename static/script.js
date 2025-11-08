const canvas = document.getElementById("mazeCanvas");
const ctx = canvas.getContext("2d");
const generateBtn = document.getElementById("generateBtn");
const solveBtn = document.getElementById("solveBtn");
const algoSelect = document.getElementById("algoSelect");
const resetBtn = document.getElementById("resetBtn");
const easyBtn = document.getElementById("easyBtn"); //accepts the difficulty levels 
const mediumBtn = document.getElementById("mediumBtn");
const hardBtn = document.getElementById("hardBtn");

let maze = [];
let cellSize = 20;
let explored = [];
let path = [];
let player = { r: 0, c: 0 };
let endPos = null;
let userPath = [];
let gameActive = false;
let timer = 0;
let timerInterval = null;
let bestPathLength = 0;

// ----------------- Maze Size ---------
async function generateMaze(rows = 25, cols = 35) {
  const res = await fetch(`/generate?rows=${rows}&cols=${cols}`);
  maze = await res.json();
  adjustCanvas();
  resetPlayer();
  drawMaze();
  gameActive = true;
  resetStats();
}
// Difficulty Buttons
easyBtn.onclick = () => generateMaze(10, 15);  // <- need to change manually by now 
mediumBtn.onclick = () => generateMaze(25, 35);
hardBtn.onclick = () => generateMaze(40, 50);

// ------------- GENERATE MAZE -------------
async function generateMaze() {
  const res = await fetch("/generate");
  maze = await res.json();
  adjustCanvas();
  resetPlayer();
  drawMaze();
  gameActive = true;
  resetStats();
}

function adjustCanvas() {
  const maxWidth = Math.min(window.innerWidth - 60, 1000);
  const cols = maze[0].length;
  const rows = maze.length;
  cellSize = Math.floor(maxWidth / cols);
  canvas.width = cols * cellSize;
  canvas.height = rows * cellSize;
  endPos = { r: rows - 1, c: cols - 1 };
}

function drawMaze() {
  for (let r = 0; r < maze.length; r++) {
    for (let c = 0; c < maze[0].length; c++) {
      ctx.fillStyle = maze[r][c] === 1 ? "#000" : "#fff";
      ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
    }
  }

  // Draw user path
  for (const step of userPath) {
    ctx.fillStyle = "#90EE90"; // light green
    ctx.fillRect(step.c * cellSize, step.r * cellSize, cellSize, cellSize);
  }

  // Start and End
  ctx.fillStyle = "green";
  ctx.fillRect(0, 0, cellSize, cellSize);
  ctx.fillStyle = "red";
  ctx.fillRect((maze[0].length - 1) * cellSize, (maze.length - 1) * cellSize, cellSize, cellSize);

  // Player position
  // below has the box shape 

  // ctx.fillStyle = "#38bdf8"; // cyan player
  // ctx.fillRect(player.c * cellSize, player.r * cellSize, cellSize, cellSize);


// below is for the player to appear as circle
const playerX = player.c * cellSize + cellSize / 2;
const playerY = player.r * cellSize + cellSize / 2;
const radius = cellSize * 0.35;

ctx.beginPath();
ctx.arc(playerX, playerY, radius, 0, 2 * Math.PI);
ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; // dark shadow
ctx.fill();
ctx.closePath();

// add a small highlight (head light or reflection)
ctx.beginPath();
ctx.arc(playerX - radius / 3, playerY - radius / 3, radius * 0.2, 0, 2 * Math.PI);
ctx.fillStyle = "rgba(255, 255, 255, 0.3)";
ctx.fill();
ctx.closePath();


}

// ------------- PLAYER MOVEMENT -------------
document.addEventListener("keydown", handleMove);

function handleMove(e) {
  if (!gameActive) return;

  let dr = 0, dc = 0;
  if (e.key === "ArrowUp" || e.key === "w") dr = -1;
  else if (e.key === "ArrowDown" || e.key === "s") dr = 1;
  else if (e.key === "ArrowLeft" || e.key === "a") dc = -1;
  else if (e.key === "ArrowRight" || e.key === "d") dc = 1;
  else if (e.key === "h" || e.key === "H") {
    if (maze.length) showHint(); // hint mode
    return;
  } else return;

  // Start timer on first move
  if (timer === 0 && !timerInterval) startTimer();

  const nr = player.r + dr;
  const nc = player.c + dc;

  if (nr < 0 || nc < 0 || nr >= maze.length || nc >= maze[0].length) return;
  if (maze[nr][nc] === 1) return; // wall

  player = { r: nr, c: nc };

  // Add to path if new cell
  if (!userPath.some(p => p.r === nr && p.c === nc)) {
    userPath.push({ r: nr, c: nc });
    updateStats();
  }

  drawMaze();
  checkWin();
}

function checkWin() {
  if (player.r === endPos.r && player.c === endPos.c) {
    gameActive = false;
    stopTimer();
    alert("🎉 You solved the maze yourself!");
    calculateScore();
  }
}

// ------------- SOLVE WITH AI -------------
async function solveMaze() {
  if (!maze.length) return alert("Generate a maze first!");

  const start = [player.r, player.c];
  const end = [endPos.r, endPos.c];
  const algo = algoSelect.value;

  const startTime = performance.now();
  const res = await fetch("/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ maze, start, end, algo }),
  });

  const data = await res.json();
  explored = data.explored || [];
  path = data.path || [];
  const endTime = performance.now();

  if (!path.length) {
    alert("⚠️ No path found!");
  } else {
    bestPathLength = path.length;
    updateStats();
    await animateExplorationThenPath();
    alert(`🤖 AI found the optimal path in ${(endTime - startTime).toFixed(1)} ms`);
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function animateExplorationThenPath() {
  drawMaze();

  // Draw exploration
  for (let i = 0; i < explored.length; i++) {
    const [r, c] = explored[i];
    if ((r === player.r && c === player.c) || (r === endPos.r && c === endPos.c)) continue;
    ctx.fillStyle = "#a0d2ff";
    ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
    if (i % 5 === 0) await sleep(10);
  }

  await sleep(100);

  // Draw final path
  for (let i = 0; i < path.length; i++) {
    const [r, c] = path[i];
    if ((r === player.r && c === player.c) || (r === endPos.r && c === endPos.c)) continue;
    ctx.fillStyle = "#ffd166";
    ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
    await sleep(10);
  }

  drawMaze();
}

// ------------- HINT FEATURE -------------
async function showHint() {
  if (!maze.length) return;

  const start = [player.r, player.c];
  const end = [endPos.r, endPos.c];
  const algo = algoSelect.value;

  const res = await fetch("/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ maze, start, end, algo }),
  });

  const data = await res.json();
  const fullPath = data.path || [];
  if (!fullPath.length) {
    alert("No hint available — no path found!");
    return;
  }

  const hintLength = Math.floor(fullPath.length / 2);
  for (let i = 0; i < hintLength; i++) {
    const [r, c] = fullPath[i];
    ctx.fillStyle = "#ffb347"; // orange hint
    ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
    await sleep(15);
  }

  alert("💡 Hint shown! Continue from the orange path.");
  drawMaze();
}

// ------------- TIMER & STATS -------------
function startTimer() {
  timer = 0;
  timerInterval = setInterval(() => {
    timer += 0.1;
    document.getElementById("timeTaken").innerText = timer.toFixed(1);
  }, 100);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

function resetStats() {
  timer = 0;
  stopTimer();
  document.getElementById("timeTaken").innerText = "0.00";
  document.getElementById("userSteps").innerText = "0";
  document.getElementById("bestPath").innerText = "?";
  document.getElementById("scoreValue").innerText = "0";
  bestPathLength = 0;
}

function updateStats() {
  document.getElementById("userSteps").innerText = userPath.length;
}

function calculateScore() {
  if (bestPathLength === 0) return;
  const efficiency = (bestPathLength / userPath.length) * 100;
  const score = Math.min(100, efficiency.toFixed(1));
  document.getElementById("scoreValue").innerText = score;
}

// ------------- RESET PLAYER -------------
function resetPlayer() {
  player = { r: 0, c: 0 };
  userPath = [];
  explored = [];
  path = [];
  drawMaze();
  resetStats();
}

generateBtn.onclick = generateMaze;
solveBtn.onclick = solveMaze;
resetBtn.onclick = resetPlayer;

window.addEventListener("resize", () => {
  if (maze.length) {
    adjustCanvas();
    drawMaze();
  }
});

// Auto-generate first maze
generateMaze();
