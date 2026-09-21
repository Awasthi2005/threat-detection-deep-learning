document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const statTotalPackets = document.getElementById('statTotalPackets');
    const statTotalThreats = document.getElementById('statTotalThreats');
    const statCurrentThreat = document.getElementById('statCurrentThreat');
    const statConfidence = document.getElementById('statConfidence');
    const statLatestTime = document.getElementById('statLatestTime');
    const statDbType = document.getElementById('statDbType');
    
    // Alert Box Elements
    const alertStatusBadge = document.getElementById('alertStatusBadge');
    const threatAlertBox = document.getElementById('threatAlertBox');
    const alertThreatType = document.getElementById('alertThreatType');
    const alertConfidence = document.getElementById('alertConfidence');
    const alertSrcIp = document.getElementById('alertSrcIp');
    const alertDstIp = document.getElementById('alertDstIp');
    const alertProtocol = document.getElementById('alertProtocol');
    const alertTime = document.getElementById('alertTime');
    const alertSeverity = document.getElementById('alertSeverity');

    // Controls
    const simToggle = document.getElementById('simToggle');
    const modeLabel = document.getElementById('modeLabel');
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const threatTableBody = document.getElementById('threatTableBody');

    // Chart.js Setup
    const ctx = document.getElementById('threatChart').getContext('2d');
    const threatChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Normal', 'DoS Attack', 'Probe', 'R2L Attack', 'U2R Attack'],
            datasets: [{
                label: 'Threat Count',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.7)',  // Normal - Green
                    'rgba(239, 68, 68, 0.7)',   // DoS - Red
                    'rgba(245, 158, 11, 0.7)',  // Probe - Yellow
                    'rgba(168, 85, 247, 0.7)',  // R2L - Purple
                    'rgba(236, 72, 153, 0.7)'   // U2R - Pink
                ],
                borderColor: [
                    '#10b981', '#ef4444', '#f59e0b', '#a855f7', '#ec4899'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#9ca3af', precision: 0 },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    ticks: { color: '#f3f4f6' },
                    grid: { display: false }
                }
            }
        }
    });

    // Toggle Simulation Mode
    simToggle.addEventListener('change', async (e) => {
        const isSim = e.target.checked;
        modeLabel.textContent = isSim ? "Simulation Mode" : "Live Packet Capture";
        modeLabel.style.color = isSim ? "var(--accent-cyan)" : "#10b981";

        try {
            await fetch('/api/mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ simulation: isSim })
            });
        } catch (err) {
            console.error("Failed to set monitoring mode", err);
        }
    });

    // Fetch & Update Live Prediction
    async function fetchLivePrediction() {
        try {
            const res = await fetch('/api/live');
            if (!res.ok) return;
            const data = await res.json();
            
            // Update Stat Cards
            statCurrentThreat.textContent = data.threat_type;
            statConfidence.textContent = `${data.confidence}%`;
            statLatestTime.textContent = `Latest: ${data.timestamp.split(' ')[1] || data.timestamp}`;

            // Update Alert Box
            alertThreatType.textContent = data.threat_type;
            alertConfidence.textContent = `${data.confidence}%`;
            alertSrcIp.textContent = data.source_ip;
            alertDstIp.textContent = data.destination_ip;
            alertProtocol.textContent = data.protocol;
            alertTime.textContent = data.timestamp;
            alertSeverity.textContent = data.status;

            // Update Badge & Styles based on threat status
            threatAlertBox.className = 'threat-alert-box';
            alertStatusBadge.className = 'badge';

            if (data.status === 'Critical') {
                threatAlertBox.classList.add('critical');
                alertStatusBadge.classList.add('badge-critical');
                alertStatusBadge.textContent = 'CRITICAL THREAT';
                statCurrentThreat.style.color = 'var(--status-critical)';
            } else if (data.status === 'Warning') {
                threatAlertBox.classList.add('warning');
                alertStatusBadge.classList.add('badge-warning');
                alertStatusBadge.textContent = 'WARNING';
                statCurrentThreat.style.color = 'var(--status-warning)';
            } else {
                alertStatusBadge.classList.add('badge-normal');
                alertStatusBadge.textContent = 'NORMAL';
                statCurrentThreat.style.color = 'var(--status-normal)';
            }
        } catch (err) {
            console.error("Error fetching live data", err);
        }
    }

    // Fetch Stats & Update Graph
    async function fetchStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) return;
            const data = await res.json();

            statTotalPackets.textContent = data.total_monitored.toLocaleString();
            statTotalThreats.textContent = data.total_threats.toLocaleString();
            statDbType.textContent = data.db_type === 'mysql' ? 'MySQL Database' : 'SQLite Fallback';
            statDbType.style.color = data.db_type === 'mysql' ? '#38bdf8' : '#a7f3d0';

            if (data.class_breakdown) {
                const counts = [
                    data.class_breakdown['Normal'] || 0,
                    data.class_breakdown['DoS Attack'] || 0,
                    data.class_breakdown['Probe'] || 0,
                    data.class_breakdown['R2L Attack'] || 0,
                    data.class_breakdown['U2R Attack'] || 0
                ];
                threatChart.data.datasets[0].data = counts;
                threatChart.update();
            }
        } catch (err) {
            console.error("Error fetching stats", err);
        }
    }

    // Fetch & Render Threat History Table
    async function fetchHistory() {
        try {
            const query = new URLSearchParams({
                search: searchInput.value.trim(),
                type: typeFilter.value,
                status: statusFilter.value
            });

            const res = await fetch(`/api/history?${query.toString()}`);
            if (!res.ok) return;
            const threats = await res.json();

            if (threats.length === 0) {
                threatTableBody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted);">No threat records found.</td></tr>`;
                return;
            }

            let html = '';
            threats.forEach(t => {
                const badgeClass = t.status === 'Critical' ? 'badge-critical' : t.status === 'Warning' ? 'badge-warning' : 'badge-normal';
                html += `
                    <tr>
                        <td>#${t.id}</td>
                        <td><strong>${t.type}</strong></td>
                        <td><span class="badge ${badgeClass}">${t.status}</span></td>
                        <td>${t.confidence}%</td>
                        <td><code>${t.source_ip}</code></td>
                        <td><code>${t.destination_ip}</code></td>
                        <td><span style="color: var(--accent-cyan); font-weight: 600;">${t.protocol}</span></td>
                        <td>${t.date}</td>
                        <td>${t.time}</td>
                    </tr>
                `;
            });
            threatTableBody.innerHTML = html;
        } catch (err) {
            console.error("Error fetching history", err);
        }
    }

    // Attach Event Listeners to Search & Filters
    searchInput.addEventListener('input', fetchHistory);
    typeFilter.addEventListener('change', fetchHistory);
    statusFilter.addEventListener('change', fetchHistory);

    // Initial Data Fetch
    fetchLivePrediction();
    fetchStats();
    fetchHistory();

    // Periodic Refresh Loops
    setInterval(fetchLivePrediction, 2000);
    setInterval(fetchStats, 3000);
    setInterval(fetchHistory, 5000);
});
