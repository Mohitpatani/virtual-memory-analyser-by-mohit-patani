let frames = [];
let pageFaults = 0;
let totalAccesses = 0;
let currentAlgorithm = "FIFO";
let pageTableSize = 8;
let frameCount = 3;

document.addEventListener("DOMContentLoaded", () => {
    const accessBtn = document.getElementById("access-btn");
    const runBtn = document.getElementById("run-seq-btn");
    const resetBtn = document.getElementById("reset-btn");
    const algoSelect = document.getElementById("algo-select");

    algoSelect.onchange = async () => {
        await setAlgorithm(algoSelect.value);
    };

    accessBtn.onclick = async () => {
        const page = parseInt(document.getElementById("access-page").value);
        if (!isNaN(page)) await accessPage(page);
    };

    runBtn.onclick = async () => {
        const seq = document.getElementById("access-seq").value
            .split(",")
            .map(n => parseInt(n.trim()))
            .filter(n => !isNaN(n));

        for (let p of seq) {
            await new Promise(r => setTimeout(r, 400));
            await accessPage(p);
        }
    };

    resetBtn.onclick = resetSimulation;
});

/* -------------------- API CALLS -------------------- */

async function setAlgorithm(algorithm) {
    await fetch("/set_algorithm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm })
    });

    resetSimulation();
}

/* -------------------- PAGE ACCESS -------------------- */

async function accessPage(page) {
    const response = await fetch("/access", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page })
    });

    const data = await response.json();
    updateState(data);
}

/* -------------------- UI UPDATE ---------------------- */

function updateState(data) {
    totalAccesses = data.total_accesses;
    pageFaults = data.total_faults;
    frames = data.frames;

    document.getElementById("total-access").textContent = totalAccesses;
    document.getElementById("total-faults").textContent = pageFaults;

    const rate = ((totalAccesses - pageFaults) / totalAccesses * 100).toFixed(2);
    document.getElementById("fault-rate").textContent = rate + "%";

    updateFramesUI();
    updatePageTableUI(data.page_table);
    logAccess(data);
}

function updateFramesUI() {
    const frameDiv = document.getElementById("frames");
    frameDiv.innerHTML = "";

    frames.forEach(p => {
        const div = document.createElement("div");
        div.className = "frame-block";
        div.textContent = "P" + p;
        frameDiv.appendChild(div);
    });
}

function updatePageTableUI(tbl) {
    let container = document.getElementById("page-table");
    container.innerHTML = "";

    Object.keys(tbl).forEach(k => {
        const div = document.createElement("div");
        div.className = tbl[k] === 1 ? "page loaded" : "page unloaded";
        div.textContent = "P" + k;
        container.appendChild(div);
    });
}

function logAccess(data) {
    const log = document.getElementById("log");
    const li = document.createElement("li");
    li.style.color = data.last_fault ? "red" : "green";
    li.textContent = `Page ${data.frames[data.frames.length - 1]} → ${data.last_fault ? "FAULT" : "HIT"}`;
    log.appendChild(li);
}

/* -------------------- RESET ---------------------- */

function resetSimulation() {
    frames = [];
    pageFaults = 0;
    totalAccesses = 0;

    document.getElementById("frames").innerHTML = "";
    document.getElementById("page-table").innerHTML = "";
    document.getElementById("log").innerHTML = "";

    document.getElementById("total-access").textContent = "0";
    document.getElementById("total-faults").textContent = "0";
    document.getElementById("fault-rate").textContent = "0%";
}
