// static/js/script.js
// Compatible with the provided index.html IDs (page-table, frames, total-accesses, page-faults, fault-rate, log-entries, etc.)

let pageTableSize = 8;
let frameCount = 4;
let frames = []; // will hold array of pages or nulls
let totalAccesses = 0;
let pageFaults = 0;

document.addEventListener("DOMContentLoaded", () => {
  // wire up controls (IDs from index.html)
  const accessBtn = document.getElementById("access-btn");
  const runBtn = document.getElementById("run-sequence-btn");
  const resetBtn = document.getElementById("reset-btn");
  const algoSelect = document.getElementById("algo-select");
  const darkModeToggle = document.getElementById("dark-mode-toggle");

  // initial read of inputs
  pageTableSize = parseInt(document.getElementById("page-table-size").value) || pageTableSize;
  frameCount = parseInt(document.getElementById("frame-count").value) || frameCount;

  // build page table UI
  initPageTable();

  // attach events
  accessBtn.onclick = async () => {
    const p = Number(document.getElementById("page-input").value);
    if (!Number.isInteger(p)) return alert("Please enter an integer page to access.");
    await accessPage(p);
  };

  runBtn.onclick = async () => {
    const seqRaw = document.getElementById("access-sequence").value || "";
    const seq = seqRaw.split(",").map(s => s.trim()).filter(s => s !== "").map(Number).filter(n => !isNaN(n));
    for (let i = 0; i < seq.length; i++) {
      await accessPage(seq[i]);
      await new Promise(r => setTimeout(r, 300));
    }
  };

  resetBtn.onclick = async () => {
    await fetch("/reset", { method: "POST", headers: {"Content-Type":"application/json"}});
    // reset client-side too
    frames = [];
    totalAccesses = 0;
    pageFaults = 0;
    initPageTable();
    updateFramesUI();
    updateStatsUI();
    document.getElementById("log-entries").innerHTML = "";
    document.getElementById("last-page").textContent = "-";
  };

  algoSelect.onchange = async () => {
    const algorithm = algoSelect.value;
    // if Optimal, send reference_string (optional) — we'll send nothing here
    const frameInput = parseInt(document.getElementById("frame-count").value) || frameCount;
    await fetch("/set_algorithm", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ algorithm, frame_count: frameInput })
    });
    // reset UI
    frames = [];
    initPageTable();
    updateFramesUI();
    updateStatsUI();
    document.getElementById("log-entries").innerHTML = "";
  };

  // fetch initial state from server
  refreshState();

  // dark mode toggle persists only client-side
  darkModeToggle.onchange = () => {
    document.body.classList.toggle("dark-mode", darkModeToggle.checked);
  };
});

/* ---------------- helper UI functions ---------------- */

function initPageTable() {
  const table = document.getElementById("page-table");
  table.innerHTML = "";
  for (let i = 0; i < pageTableSize; i++) {
    const cell = document.createElement("div");
    cell.id = `page-${i}`;
    cell.className = "grid-cell";
    cell.textContent = i;
    table.appendChild(cell);
  }
}

function updatePageTableFromServer(page_table) {
  // page_table expected as object: { "0": 1, "1": 0, ... } or array-like
  for (let i = 0; i < pageTableSize; i++) {
    const el = document.getElementById(`page-${i}`);
    const loaded = page_table.hasOwnProperty(i) ? !!page_table[i] : false;
    if (!el) continue;
    el.classList.remove("fault", "hit", "loaded");
    if (loaded) {
      el.classList.add("hit", "loaded");
    } else {
      // leave default look
      el.classList.remove("hit");
    }
  }
}

function updateFramesUI() {
  const frameDiv = document.getElementById("frames");
  frameDiv.innerHTML = "";
  // frames array may contain nulls; ensure length = frameCount
  let arr = Array.isArray(frames) ? frames.slice(0) : [];
  if (arr.length < frameCount) {
    while (arr.length < frameCount) arr.push(null);
  } else if (arr.length > frameCount) {
    arr = arr.slice(0, frameCount);
  }

  arr.forEach(p => {
    const cell = document.createElement("div");
    cell.className = "grid-cell";
    cell.style.minHeight = "48px";
    cell.style.display = "flex";
    cell.style.alignItems = "center";
    cell.style.justifyContent = "center";
    if (p === null || p === undefined) {
      cell.textContent = "";
      cell.style.opacity = "0.4";
    } else {
      cell.textContent = p;
    }
    frameDiv.appendChild(cell);
  });
}

function updateStatsUI() {
  document.getElementById("total-accesses").textContent = totalAccesses;
  document.getElementById("page-faults").textContent = pageFaults;
  const rate = totalAccesses === 0 ? 0 : ((totalAccesses - pageFaults) / totalAccesses * 100).toFixed(2);
  document.getElementById("fault-rate").textContent = `${rate}%`;

  // update hit-rate bar if exists
  const hitBar = document.getElementById("hit-rate-fill");
  if (hitBar) hitBar.style.width = `${rate}%`;
}

function addLogEntry(text, isFault) {
  const ul = document.getElementById("log-entries");
  const li = document.createElement("li");
  li.textContent = text;
  li.style.color = isFault ? "#b71c1c" : "#2e7d32";
  ul.appendChild(li);
  // auto scroll
  ul.scrollTop = ul.scrollHeight;
}

/* ---------------- Networking ---------------- */

async function refreshState() {
  try {
    const resp = await fetch("/state");
    if (!resp.ok) throw new Error("Failed to fetch state");
    const data = await resp.json();
    // data contains: page_table, frames, total_accesses, total_faults, last_fault
    frames = data.frames || [];
    totalAccesses = data.total_accesses || 0;
    pageFaults = data.total_faults || 0;
    updateFramesUI();
    updatePageTableFromServer(data.page_table || {});
    updateStatsUI();
  } catch (e) {
    console.error("refreshState error:", e);
  }
}

async function accessPage(page) {
  // basic validation
  if (page < 0 || page >= pageTableSize) {
    alert(`Page must be between 0 and ${pageTableSize - 1}`);
    return;
  }
  try {
    const resp = await fetch("/access", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ page })
    });
    const data = await resp.json();
    if (data.error) {
      console.error("server error:", data.error);
      alert("Server error: " + data.error);
      return;
    }
    // backend returns state with keys we used earlier in server code
    frames = data.frames || [];
    totalAccesses = data.total_accesses || totalAccesses + 1;
    pageFaults = data.total_faults || pageFaults + (data.last_fault ? 1 : 0);

    updateFramesUI();
    updatePageTableFromServer(data.page_table || {});
    updateStatsUI();

    // log
    const last = data.last_accessed !== undefined ? data.last_accessed : page;
    document.getElementById("last-page").textContent = last;
    addLogEntry(`Page ${page} → ${data.last_fault ? "FAULT" : "HIT"}`, !!data.last_fault);

  } catch (err) {
    console.error("accessPage failed:", err);
  }
}

