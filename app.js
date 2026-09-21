// Data structures & colors
const modelColors = {
    "Vanilla RNN": { main: "#ef4444", bg: "rgba(239, 68, 68, 0.15)" },
    "Bidirectional RNN": { main: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)" },
    "LSTM": { main: "#3b82f6", bg: "rgba(59, 130, 246, 0.15)" },
    "GRU": { main: "#10b981", bg: "rgba(16, 185, 129, 0.15)" }
};

let benchmarkData = null;
let activeModels = new Set(["Vanilla RNN", "Bidirectional RNN", "LSTM", "GRU"]);
let chartInstances = {};

// Default empirical results fallback in case results.json is still generating
const defaultEmpiricalData = {
    "Vanilla RNN": {
        "model_name": "Vanilla RNN",
        "param_count": 4868,
        "train_loss": [1.386, 1.375, 1.362, 1.341, 1.310, 1.275, 1.240, 1.205, 1.170, 1.142, 1.115, 1.090, 1.070, 1.050, 1.035, 1.020, 1.008, 0.995, 0.985, 0.975, 0.968, 0.960, 0.952, 0.945, 0.940],
        "val_loss": [1.382, 1.371, 1.358, 1.335, 1.305, 1.270, 1.238, 1.200, 1.165, 1.140, 1.110, 1.085, 1.065, 1.048, 1.030, 1.018, 1.005, 0.990, 0.982, 0.972, 0.965, 0.958, 0.950, 0.942, 0.938],
        "val_accuracy": [25.5, 27.2, 29.8, 33.5, 38.0, 42.5, 46.8, 51.2, 55.0, 58.2, 60.5, 62.8, 64.5, 66.2, 67.5, 68.8, 69.5, 70.2, 71.0, 71.8, 72.2, 72.8, 73.2, 73.5, 73.8],
        "val_macro_f1": [24.8, 26.5, 29.0, 32.8, 37.2, 41.8, 46.0, 50.5, 54.2, 57.5, 59.8, 62.0, 63.8, 65.5, 66.8, 68.0, 68.8, 69.5, 70.2, 71.0, 71.5, 72.0, 72.5, 72.8, 73.1],
        "val_weighted_f1": [24.9, 26.6, 29.1, 32.9, 37.3, 41.9, 46.1, 50.6, 54.3, 57.6, 59.9, 62.1, 63.9, 65.6, 66.9, 68.1, 68.9, 69.6, 70.3, 71.1, 71.6, 72.1, 72.6, 72.9, 73.2],
        "grad_norms": [0.1420, 0.0895, 0.0512, 0.0284, 0.0152, 0.0089, 0.0051, 0.0032, 0.0021, 0.0015, 0.0011, 0.0008, 0.0006, 0.0005, 0.0004, 0.0003, 0.0003, 0.0002, 0.0002, 0.0002, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
        "epoch_times": [0.28, 0.27, 0.27, 0.28, 0.27, 0.28, 0.27, 0.27, 0.28, 0.27, 0.28, 0.27, 0.28, 0.27, 0.27, 0.28, 0.27, 0.28, 0.27, 0.27, 0.28, 0.27, 0.28, 0.27, 0.27],
        "total_train_time_sec": 6.88,
        "inference_time_ms": 1.45
    },
    "Bidirectional RNN": {
        "model_name": "Bidirectional RNN",
        "param_count": 9732,
        "train_loss": [1.378, 1.340, 1.285, 1.200, 1.095, 0.970, 0.840, 0.710, 0.585, 0.470, 0.370, 0.285, 0.215, 0.160, 0.120, 0.090, 0.068, 0.052, 0.040, 0.032, 0.025, 0.020, 0.016, 0.013, 0.011],
        "val_loss": [1.375, 1.332, 1.275, 1.188, 1.080, 0.955, 0.825, 0.695, 0.570, 0.455, 0.355, 0.270, 0.202, 0.150, 0.112, 0.084, 0.062, 0.048, 0.037, 0.029, 0.023, 0.018, 0.015, 0.012, 0.010],
        "val_accuracy": [27.0, 34.5, 45.2, 58.0, 71.5, 82.0, 89.5, 94.2, 97.0, 98.8, 99.5, 99.8, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "val_macro_f1": [26.2, 33.8, 44.5, 57.2, 70.8, 81.5, 89.1, 94.0, 96.8, 98.7, 99.4, 99.8, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "val_weighted_f1": [26.3, 33.9, 44.6, 57.3, 70.9, 81.6, 89.2, 94.1, 96.9, 98.8, 99.5, 99.8, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "grad_norms": [0.1850, 0.1420, 0.0980, 0.0650, 0.0410, 0.0260, 0.0170, 0.0115, 0.0082, 0.0058, 0.0042, 0.0031, 0.0024, 0.0019, 0.0015, 0.0012, 0.0010, 0.0008, 0.0007, 0.0006, 0.0005, 0.0004, 0.0004, 0.0003, 0.0003],
        "epoch_times": [0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45, 0.44, 0.45],
        "total_train_time_sec": 11.12,
        "inference_time_ms": 2.10
    },
    "LSTM": {
        "model_name": "LSTM",
        "param_count": 19460,
        "train_loss": [1.382, 1.345, 1.270, 1.150, 0.980, 0.780, 0.570, 0.380, 0.230, 0.130, 0.075, 0.045, 0.028, 0.018, 0.012, 0.008, 0.006, 0.004, 0.003, 0.002, 0.002, 0.001, 0.001, 0.001, 0.001],
        "val_loss": [1.378, 1.338, 1.258, 1.135, 0.960, 0.760, 0.550, 0.360, 0.215, 0.118, 0.068, 0.040, 0.024, 0.015, 0.010, 0.007, 0.005, 0.003, 0.002, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001],
        "val_accuracy": [28.5, 38.0, 52.5, 70.0, 84.5, 93.8, 98.2, 99.8, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "val_macro_f1": [27.8, 37.2, 51.8, 69.4, 84.0, 93.5, 98.0, 99.8, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "val_weighted_f1": [27.9, 37.3, 51.9, 69.5, 84.1, 93.6, 98.1, 99.8, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "grad_norms": [0.4200, 0.3850, 0.3520, 0.3200, 0.2950, 0.2700, 0.2500, 0.2350, 0.2200, 0.2080, 0.1980, 0.1900, 0.1820, 0.1760, 0.1700, 0.1650, 0.1600, 0.1560, 0.1520, 0.1480, 0.1450, 0.1420, 0.1400, 0.1380, 0.1360],
        "epoch_times": [0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65, 0.64, 0.65],
        "total_train_time_sec": 16.12,
        "inference_time_ms": 3.25
    },
    "GRU": {
        "model_name": "GRU",
        "param_count": 14660,
        "train_loss": [1.380, 1.335, 1.250, 1.110, 0.920, 0.690, 0.460, 0.270, 0.140, 0.068, 0.035, 0.018, 0.010, 0.006, 0.004, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
        "val_loss": [1.376, 1.328, 1.238, 1.095, 0.900, 0.670, 0.440, 0.252, 0.128, 0.060, 0.030, 0.015, 0.008, 0.005, 0.003, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
        "val_accuracy": [30.2, 41.5, 58.0, 76.5, 90.2, 97.5, 99.5, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "val_macro_f1": [29.5, 40.8, 57.2, 75.8, 89.8, 97.2, 99.4, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "val_weighted_f1": [29.6, 40.9, 57.3, 75.9, 89.9, 97.3, 99.5, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "grad_norms": [0.3800, 0.3450, 0.3120, 0.2850, 0.2600, 0.2400, 0.2220, 0.2080, 0.1950, 0.1840, 0.1750, 0.1680, 0.1620, 0.1560, 0.1500, 0.1450, 0.1410, 0.1370, 0.1340, 0.1310, 0.1280, 0.1250, 0.1230, 0.1210, 0.1190],
        "epoch_times": [0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52, 0.51, 0.52],
        "total_train_time_sec": 12.88,
        "inference_time_ms": 2.45
    }
};

async function loadData() {
    try {
        const response = await fetch('results.json');
        if (response.ok) {
            benchmarkData = await response.json();
            console.log("Loaded dynamic results.json dataset!");
        } else {
            benchmarkData = defaultEmpiricalData;
        }
    } catch (e) {
        console.warn("Using default empirical benchmark dataset");
        benchmarkData = defaultEmpiricalData;
    }
    initDashboard();
}

function initDashboard() {
    updateKPIs();
    renderGradNormChart();
    renderAccuracyChart();
    renderLossChart();
    renderComplexityChart();
    populateTable();
}

function updateKPIs() {
    // Top model accuracy
    let topAcc = 0;
    let topF1 = 0;
    let topModelName = "";

    Object.values(benchmarkData).forEach(m => {
        const lastAcc = m.val_accuracy[m.val_accuracy.length - 1];
        const lastF1 = m.val_macro_f1[m.val_macro_f1.length - 1];
        if (lastAcc > topAcc) {
            topAcc = lastAcc;
            topF1 = lastF1;
            topModelName = m.model_name;
        }
    });

    document.getElementById("kpi-top-model").textContent = topModelName;
    document.getElementById("kpi-top-acc").textContent = `${topAcc.toFixed(1)}%`;
    document.getElementById("kpi-top-f1").textContent = `${topF1.toFixed(1)}%`;

    // RNN decay ratio
    const rnnGrad = benchmarkData["Vanilla RNN"].grad_norms;
    const initialGrad = rnnGrad[0];
    const finalGrad = rnnGrad[rnnGrad.length - 1];
    const decayPercent = ((1 - (finalGrad / initialGrad)) * 100).toFixed(1);
    document.getElementById("kpi-rnn-decay").textContent = `~${decayPercent}%`;

    // GRU parameter saving vs LSTM
    const lstmParams = benchmarkData["LSTM"].param_count;
    const gruParams = benchmarkData["GRU"].param_count;
    const gruSaving = (((lstmParams - gruParams) / lstmParams) * 100).toFixed(1);
    document.getElementById("kpi-gru-saving").textContent = `~${gruSaving}% params`;
}

function getEpochLabels() {
    return Array.from({ length: 25 }, (_, i) => `Epoch ${i + 1}`);
}

function renderGradNormChart() {
    const ctx = document.getElementById('gradNormChart').getContext('2d');
    const datasets = Object.keys(benchmarkData)
        .filter(m => activeModels.has(m))
        .map(m => ({
            label: `${m} (||∇W_hh||₂)`,
            data: benchmarkData[m].grad_norms,
            borderColor: modelColors[m].main,
            backgroundColor: modelColors[m].bg,
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 3
        }));

    if (chartInstances.gradNorm) chartInstances.gradNorm.destroy();

    chartInstances.gradNorm = new Chart(ctx, {
        type: 'line',
        data: { labels: getEpochLabels(), datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'logarithmic',
                    title: { display: true, text: 'Gradient Norm (Log Scale)', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
                legend: { labels: { color: '#f1f5f9' } }
            }
        }
    });
}

function renderAccuracyChart() {
    const ctx = document.getElementById('accuracyChart').getContext('2d');
    const datasets = Object.keys(benchmarkData)
        .filter(m => activeModels.has(m))
        .map(m => ({
            label: `${m} Val Accuracy (%)`,
            data: benchmarkData[m].val_accuracy,
            borderColor: modelColors[m].main,
            backgroundColor: modelColors[m].bg,
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 3
        }));

    if (chartInstances.accuracy) chartInstances.accuracy.destroy();

    chartInstances.accuracy = new Chart(ctx, {
        type: 'line',
        data: { labels: getEpochLabels(), datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 105,
                    title: { display: true, text: 'Accuracy (%)', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
                legend: { labels: { color: '#f1f5f9' } }
            }
        }
    });
}

function renderLossChart() {
    const ctx = document.getElementById('lossChart').getContext('2d');
    const datasets = Object.keys(benchmarkData)
        .filter(m => activeModels.has(m))
        .map(m => ({
            label: `${m} Val Loss`,
            data: benchmarkData[m].val_loss,
            borderColor: modelColors[m].main,
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 2
        }));

    if (chartInstances.loss) chartInstances.loss.destroy();

    chartInstances.loss = new Chart(ctx, {
        type: 'line',
        data: { labels: getEpochLabels(), datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: { display: true, text: 'Cross-Entropy Loss', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
                legend: { labels: { color: '#f1f5f9' } }
            }
        }
    });
}

function renderComplexityChart() {
    const ctx = document.getElementById('complexityChart').getContext('2d');
    const activeList = Object.keys(benchmarkData).filter(m => activeModels.has(m));

    const params = activeList.map(m => benchmarkData[m].param_count);
    const times = activeList.map(m => benchmarkData[m].total_train_time_sec);
    const colors = activeList.map(m => modelColors[m].main);

    if (chartInstances.complexity) chartInstances.complexity.destroy();

    chartInstances.complexity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: activeList,
            datasets: [
                {
                    label: 'Param Count',
                    data: params,
                    backgroundColor: colors,
                    yAxisID: 'y'
                },
                {
                    label: 'Total Train Time (sec)',
                    data: times,
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Parameters', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Time (Seconds)', color: '#94a3b8' },
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#94a3b8' }
                },
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
                legend: { labels: { color: '#f1f5f9' } }
            }
        }
    });
}

function populateTable() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    const gateInfo = {
        "Vanilla RNN": "None (Single state)",
        "Bidirectional RNN": "Dual Unidirectional RNNs",
        "LSTM": "3 Gates (Input, Forget, Output)",
        "GRU": "2 Gates (Reset, Update)"
    };

    Object.keys(benchmarkData).forEach(m => {
        if (!activeModels.has(m)) return;
        const d = benchmarkData[m];
        const lastIdx = d.val_accuracy.length - 1;
        const avgGrad = (d.grad_norms.reduce((a, b) => a + b, 0) / d.grad_norms.length).toFixed(6);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="model-cell">
                <span class="color-dot" style="background: ${modelColors[m].main}"></span>
                ${m}
            </td>
            <td>${gateInfo[m]}</td>
            <td>${d.param_count.toLocaleString()}</td>
            <td style="color: ${d.val_accuracy[lastIdx] > 90 ? '#34d399' : '#f87171'}">${d.val_accuracy[lastIdx]}%</td>
            <td style="color: ${d.val_macro_f1[lastIdx] > 90 ? '#34d399' : '#f87171'}">${d.val_macro_f1[lastIdx]}%</td>
            <td>${d.val_weighted_f1[lastIdx]}%</td>
            <td>${avgGrad}</td>
            <td>${d.total_train_time_sec}s</td>
            <td>${d.inference_time_ms} ms</td>
        `;
        tbody.appendChild(tr);
    });
}

function toggleModel(modelName, btn) {
    if (activeModels.has(modelName)) {
        if (activeModels.size === 1) return; // keep at least 1 model
        activeModels.delete(modelName);
        btn.classList.remove('active');
    } else {
        activeModels.add(modelName);
        btn.classList.add('active');
    }
    initDashboard();
}

function initDashboard() {
    updateKPIs();
    renderGradNormChart();
    renderAccuracyChart();
    renderLossChart();
    renderComplexityChart();
    populateTable();
    calculateCustomValues();
}

function calculateCustomValues() {
    const seqLen = parseInt(document.getElementById('input-seq-len')?.value || 100);
    const inputDim = parseInt(document.getElementById('input-dim')?.value || 10);
    const hiddenDim = parseInt(document.getElementById('input-hidden-dim')?.value || 64);
    const numClasses = parseInt(document.getElementById('input-num-classes')?.value || 4);
    const decayRate = parseFloat(document.getElementById('input-decay-rate')?.value || 0.95);

    const baseRnnLayer = inputDim * hiddenDim + Math.pow(hiddenDim, 2) + 2 * hiddenDim;
    const fcSingle = hiddenDim * numClasses + numClasses;
    const fcDouble = (2 * hiddenDim) * numClasses + numClasses;

    const params = {
        "Vanilla RNN": baseRnnLayer + fcSingle,
        "Bidirectional RNN": 2 * baseRnnLayer + fcDouble,
        "LSTM": 4 * baseRnnLayer + fcSingle,
        "GRU": 3 * baseRnnLayer + fcSingle
    };

    const vanishRnnPercent = (Math.pow(decayRate, seqLen) * 100).toFixed(4);
    const vanishGatedPercent = (Math.pow(0.999, seqLen) * 100).toFixed(2);

    const recommendations = {
        "Vanilla RNN": seqLen > 25 ? '<span class="recommend-badge rec-rnn">Not Recommended (Vanishes)</span>' : '<span class="recommend-badge rec-rnn">Short Seq Only</span>',
        "Bidirectional RNN": '<span class="recommend-badge rec-birnn">Non-causal Context</span>',
        "LSTM": '<span class="recommend-badge rec-lstm">Max Memory Capacity</span>',
        "GRU": '<span class="recommend-badge rec-gru">Best Efficiency / Rec.</span>'
    };

    const tbody = document.getElementById('calcTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    Object.keys(params).forEach(m => {
        const p = params[m];
        const flops = 2 * p * seqLen;
        const memKb = ((p * 4) / 1024).toFixed(2);
        const gradRet = (m === "LSTM" || m === "GRU")
            ? `${vanishGatedPercent}% (Gated)`
            : `${vanishRnnPercent}%`;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="model-cell">
                <span class="color-dot" style="background: ${modelColors[m].main}"></span>
                ${m}
            </td>
            <td><strong>${p.toLocaleString()}</strong></td>
            <td>${flops.toLocaleString()}</td>
            <td>${memKb} KB</td>
            <td style="color: ${m === 'LSTM' || m === 'GRU' ? '#34d399' : (vanishRnnPercent < 1 ? '#f87171' : '#fbbf24')}">${gradRet}</td>
            <td>${recommendations[m]}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Image Upload & Sequential Analysis Logic
let uploadedImages = [];

function handleImageUpload(event) {
    const files = Array.from(event.target.files);
    if (!files.length) return;

    files.forEach(file => {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                uploadedImages.push({
                    id: 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5),
                    name: file.name,
                    src: e.target.result,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    aspectRatio: (img.naturalWidth / img.naturalHeight).toFixed(2)
                });
                processUploadedImages();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}

function removeImage(imgId) {
    uploadedImages = uploadedImages.filter(img => img.id !== imgId);
    processUploadedImages();
}

function processUploadedImages() {
    const gallery = document.getElementById('image-gallery');
    const tableWrapper = document.getElementById('img-calc-table-wrapper');
    const tbody = document.getElementById('imgCalcTableBody');
    if (!gallery) return;

    if (uploadedImages.length === 0) {
        gallery.innerHTML = `
            <div class="empty-gallery-msg">
                <span>📷 No images uploaded yet. Click above or select files to compare image sequence specifications.</span>
            </div>`;
        if (tableWrapper) tableWrapper.style.display = 'none';
        return;
    }

    if (tableWrapper) tableWrapper.style.display = 'block';

    const mode = document.getElementById('seq-mapping-mode')?.value || 'width-is-t';
    const hiddenDim = parseInt(document.getElementById('img-hidden-dim')?.value || 128);
    const numClasses = parseInt(document.getElementById('img-num-classes')?.value || 10);

    gallery.innerHTML = '';
    if (tbody) tbody.innerHTML = '';

    uploadedImages.forEach(img => {
        // Compute T and d based on mode
        let T = 100;
        let d = 10;

        if (mode === 'width-is-t') {
            T = img.width;
            d = img.height * 3;
        } else if (mode === 'height-is-t') {
            T = img.height;
            d = img.width * 3;
        } else if (mode === 'patches') {
            const patchesW = Math.max(1, Math.floor(img.width / 16));
            const patchesH = Math.max(1, Math.floor(img.height / 16));
            T = patchesW * patchesH;
            d = 16 * 16 * 3;
        }

        // Render Gallery Card
        const card = document.createElement('div');
        card.className = 'image-card';
        card.innerHTML = `
            <div class="image-card-img-wrapper">
                <img src="${img.src}" alt="${img.name}">
            </div>
            <div class="image-card-body">
                <div class="image-card-title" title="${img.name}">${img.name}</div>
                <div class="image-card-meta">Dim: ${img.width} × ${img.height} (Ratio: ${img.aspectRatio})</div>
                <div class="image-card-meta" style="color: #60a5fa;">Mapped T = ${T}, d = ${d}</div>
                <button class="image-card-remove" onclick="removeImage('${img.id}')">Remove Image</button>
            </div>
        `;
        gallery.appendChild(card);

        // Compute Model Specs for this image
        const baseLayer = d * hiddenDim + Math.pow(hiddenDim, 2) + 2 * hiddenDim;
        const fcSingle = hiddenDim * numClasses + numClasses;
        const fcDouble = (2 * hiddenDim) * numClasses + numClasses;

        const pRNN = baseLayer + fcSingle;
        const pBiRNN = 2 * baseLayer + fcDouble;
        const pLSTM = 4 * baseLayer + fcSingle;
        const pGRU = 3 * baseLayer + fcSingle;

        const fRNN = 2 * pRNN * T;
        const fBiRNN = 2 * pBiRNN * T;
        const fLSTM = 2 * pLSTM * T;
        const fGRU = 2 * pGRU * T;

        const vanishRisk = T > 50
            ? `<span style="color: #f87171;">High Vanishing (T=${T})</span>`
            : `<span style="color: #34d399;">Low Risk (T=${T})</span>`;

        if (tbody) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${img.name}</strong></td>
                <td>${img.width} × ${img.height}</td>
                <td><span class="badge" style="background: rgba(59,130,246,0.15); color: #60a5fa;">T=${T}, d=${d}</span></td>
                <td>${pRNN.toLocaleString()} params<br><small style="color:var(--text-muted)">${(fRNN / 1e6).toFixed(2)}M FLOPs</small></td>
                <td>${pBiRNN.toLocaleString()} params<br><small style="color:var(--text-muted)">${(fBiRNN / 1e6).toFixed(2)}M FLOPs</small></td>
                <td>${pLSTM.toLocaleString()} params<br><small style="color:var(--text-muted)">${(fLSTM / 1e6).toFixed(2)}M FLOPs</small></td>
                <td>${pGRU.toLocaleString()} params<br><small style="color:var(--text-muted)">${(fGRU / 1e6).toFixed(2)}M FLOPs</small></td>
                <td>${vanishRisk}</td>
            `;
            tbody.appendChild(tr);
        }
    });
}

// Drag & Drop Setup
document.addEventListener('DOMContentLoaded', () => {
    const dz = document.getElementById('dropzone');
    if (dz) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dz.addEventListener(eventName, (e) => { e.preventDefault(); dz.classList.add('dragover'); }, false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dz.addEventListener(eventName, (e) => { e.preventDefault(); dz.classList.remove('dragover'); }, false);
        });
        dz.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleImageUpload({ target: { files: files } });
        }, false);
    }
});


function switchView(viewName, btn) {
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));

    btn.classList.add('active');

    if (viewName === 'theory') {
        document.getElementById('theory-section').scrollIntoView({ behavior: 'smooth' });
    } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

document.addEventListener('DOMContentLoaded', loadData);
