// static/js/script.js
let frames = [];
let pageTableSize = 8;
let frameCount = 4;
let pageFaults = 0;
let totalAccesses = 0;
let currentAlgorithm = "FIFO";
let busy = false;
let pageTableFromServer = null;

// Chart placeholders (if using Chart.js)
let pageFaultChart, memoryUsageChart, pageTableStatusChart;

document.addEventListener("DOMContentLoaded", () => {
  const accessBtn = document.getElementById("access-btn");
  const runBtn = document.getElementById("run-sequence-btn");
  const resetBtn = document.getElementById("reset-btn");
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  const algoSelect = document.getElementById("algo-select");

  pageTableSize = parseInt(document.getElementById("page-table-size").value) || pageTableSize;
  frameCount = parseInt(document.getElementById("frame-count").value) || frameCount;

  initPageTable();
  initCharts();
  refreshState();

  document.body.classList.toggle("dark-mode", darkModeToggle.checked);

  algoSelect.onchange = async () => {
    currentAlgorithm = algoSelect.value;
    await setAlgorithm(currentAlgorithm);
  };

  accessBtn.onclick = async () => {
    const raw = document.getElementById("page-input").value;
    const page = Number(raw);
    if (!Number.isInteger(page)) {
      alert("Page must be an integer");
      return;
    }
    try {
      validatePage(page);
    } catch (e) {
      alert(e.message);
      return;
    }
    await accessPage(page);
  };

  runBtn.onclick = async () => {
    const seqInput = document.getElementById("access-sequence").value;
    const seq = parseSequence(seqInput);
    for (let i = 0; i < seq.length; i++) {
      await sleep(350);
      await accessPage(seq[i]);
    }
  };

