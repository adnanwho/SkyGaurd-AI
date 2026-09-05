const DATA_URL = '../outputs/exports/anomaly_detection_results.csv';
const API_DATA = 'api/data';
const API_REFRESH = 'api/refresh';
const state = { rows: [], filtered: [], visibleRows: 10, liveFeed: false };
const $ = (id) => document.getElementById(id);

function parseCSV(text) {
    const records = []; let row = []; let value = ''; let quoted = false;
    for (let index = 0; index < text.length; index += 1) {
        const character = text[index];
        if (character === '"' && text[index + 1] === '"' && quoted) { value += '"'; index += 1; }
        else if (character === '"') quoted = !quoted;
        else if (character === ',' && !quoted) { row.push(value); value = ''; }
        else if ((character === '\n' || character === '\r') && !quoted) {
            if (character === '\r' && text[index + 1] === '\n') index += 1;
            row.push(value); value = ''; if (row.some((cell) => cell.trim())) records.push(row); row = [];
        } else value += character;
    }
    if (value || row.length) { row.push(value); records.push(row); }
    const headers = (records.shift() || []).map((header) => header.trim());
    return records.map((cells) => headers.reduce((record, header, index) => ({ ...record, [header]: cells[index] ?? '' }), {}));
}

const number = (value) => Number.parseFloat(value) || 0;
const field = (row, canonical, legacy = canonical) => row[canonical] ?? row[legacy] ?? '';
const station = (row) => field(row, 'station_id', 'Location');
const timestamp = (row) => field(row, 'timestamp', 'DateTime');
const anomaly = (row) => Number(field(row, 'Final_Anomaly', 'Ensemble_Anomaly')) === 1;
const score = (row) => number(field(row, 'Final_Score', 'Ensemble_Score'));
const formatNumber = (value, digits = 0) => new Intl.NumberFormat('en-IN', { maximumFractionDigits: digits }).format(value);
const formatDate = (value, includeTime = true) => {
    const raw = String(value || ''); const normalized = raw.includes('T') ? raw : raw.replace(' ', 'T');
    const date = new Date(normalized); if (Number.isNaN(date.getTime())) return raw || 'Unavailable';
    return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', ...(includeTime ? { hour: '2-digit', minute: '2-digit' } : {}) }).format(date);
};
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[character]));

function setSync(label) { $('sync-label').textContent = label; }
function showToast(message) { const toast = $('toast'); toast.textContent = message; toast.classList.add('visible'); setTimeout(() => toast.classList.remove('visible'), 3500); }

const sortByTimeDesc = (rows) => rows.sort((a, b) => new Date(timestamp(b)) - new Date(timestamp(a)));

async function loadData(rows = null, source = 'Stored analysis') {
    // Uploaded rows are a client-side preview only — no backend round-trip.
    if (rows) {
        state.rows = sortByTimeDesc(rows); setSync(source); render(); return;
    }
    setSync('Loading analysis');
    // 1) Live backend feed (server.py). Used automatically when the page is
    //    served by the SkyGuard server; provides on-demand re-analysis.
    try {
        const response = await fetch(`${API_DATA}?v=${Date.now()}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`API HTTP ${response.status}`);
        const payload = await response.json();
        if (payload.error) throw new Error(payload.error);
        state.liveFeed = true;
        state.rows = sortByTimeDesc(payload.rows || []);
        setSync(payload.updated ? `Live feed · updated ${formatDate(payload.updated)}` : 'Live feed connected');
        render(); return;
    } catch (_apiError) {
        state.liveFeed = false; // backend not present — fall back to the static export
    }
    // 2) Static CSV fallback (plain http.server or opening the file directly).
    try {
        const response = await fetch(`${DATA_URL}?v=${Date.now()}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`CSV HTTP ${response.status}`);
        state.rows = sortByTimeDesc(parseCSV(await response.text()));
        setSync('Stored analysis (static)'); render();
    } catch (error) {
        state.rows = []; setSync('Data unavailable'); showToast(`Could not load analysis: ${error.message}`); render();
    }
}

async function refresh() {
    const button = $('refresh-button');
    if (!state.liveFeed) { loadData(); return; } // static mode: re-fetch the export
    button.disabled = true; button.classList.add('busy');
    setSync('Running live analysis…');
    showToast('Running live analysis — the full pipeline can take a couple of minutes.');
    try {
        const response = await fetch(API_REFRESH, { method: 'POST' });
        const payload = await response.json();
        if (!response.ok || payload.error) throw new Error(payload.error || `Refresh HTTP ${response.status}`);
        state.rows = sortByTimeDesc(payload.rows || []);
        setSync(payload.updated ? `Live feed · updated ${formatDate(payload.updated)}` : 'Live feed connected');
        showToast(`Live analysis complete · ${formatNumber(payload.count || state.rows.length)} observations`);
        render();
    } catch (error) {
        setSync('Refresh failed'); showToast(`Live refresh failed: ${error.message}`);
    } finally {
        button.disabled = false; button.classList.remove('busy');
    }
}

function render() {
    const rows = state.rows; const anomalies = rows.filter(anomaly); const stations = [...new Set(rows.map(station).filter(Boolean))];
    const agreementRows = rows.filter((row) => number(row.Model_Agreement) >= 3);
    const dates = rows.map(timestamp).filter(Boolean).sort();
    $('active-anomalies').textContent = formatNumber(anomalies.length);
    $('anomaly-rate').textContent = `${((anomalies.length / Math.max(rows.length, 1)) * 100).toFixed(2)}% of observations`;
    $('station-count').textContent = formatNumber(stations.length);
    $('observation-count').textContent = formatNumber(rows.length);
    $('agreement-rate').textContent = `${((agreementRows.length / Math.max(rows.length, 1)) * 100).toFixed(1)}%`;
    $('data-window').textContent = dates.length ? `· ${formatDate(dates[0], false)} to ${formatDate(dates.at(-1), false)}` : '· No data';
    $('observation-window').textContent = dates.length ? `${formatDate(dates[0], false)} - ${formatDate(dates.at(-1), false)}` : 'No data available';
    $('updated-at').textContent = formatDate(timestamp(rows[0])); $('station-panel-count').textContent = `${anomalies.length} flagged`;
    renderStations(rows, stations); renderTable(); drawTrend(rows);
}

function renderStations(rows, stations) {
    const stationData = stations.map((name) => {
        const stationRows = rows.filter((row) => station(row) === name); const anomalyCount = stationRows.filter(anomaly).length;
        const maxScore = Math.max(...stationRows.map(score), 0); return { name, anomalyCount, maxScore };
    }).sort((a, b) => b.anomalyCount - a.anomalyCount || b.maxScore - a.maxScore).slice(0, 5);
    $('station-list').innerHTML = stationData.length ? stationData.map((item) => `<button class="station-row" type="button" data-station="${escapeHtml(item.name)}"><span><span class="station-name">${escapeHtml(item.name)}</span><span class="station-meta">${item.anomalyCount ? `${item.anomalyCount} flagged reading${item.anomalyCount === 1 ? '' : 's'}` : 'No flagged readings'}</span></span><span class="station-bar"><span style="width:${Math.max(item.maxScore * 100, 2)}%"></span></span><span class="station-score">${Math.round(item.maxScore * 100)}%</span></button>`).join('') : '<div class="loading-row">No station data available</div>';
    document.querySelectorAll('[data-station]').forEach((button) => button.addEventListener('click', () => { $('search-input').value = button.dataset.station; renderTable(); $('observation-table').scrollIntoView({ behavior: 'smooth', block: 'center' }); }));
}

function renderTable() {
    const query = $('search-input').value.toLowerCase().trim(); const filter = $('status-filter').value;
    state.filtered = state.rows.filter((row) => { const matchesSearch = station(row).toLowerCase().includes(query); const matchesFilter = filter === 'all' || (filter === 'anomaly' && anomaly(row)) || (filter === 'normal' && !anomaly(row)); return matchesSearch && matchesFilter; });
    const visible = state.filtered.slice(0, state.visibleRows);
    $('observation-table').innerHTML = visible.length ? visible.map((row, index) => {
        const flagged = anomaly(row); const agreement = field(row, 'Model_Agreement') || '0'; const severity = field(row, 'severity', 'Anomaly_Severity') || 'NORMAL';
        return `<tr data-row-index="${state.filtered.indexOf(row)}" tabindex="0"><td>${escapeHtml(station(row))}</td><td class="muted-cell">${formatDate(timestamp(row))}</td><td>${formatNumber(number(field(row, 'temperature', 'Temperature_C')), 1)} °C</td><td>${formatNumber(number(field(row, 'humidity', 'Humidity_Percent')), 1)}%</td><td>${formatNumber(number(field(row, 'pressure', 'Pressure_hPa')), 1)} hPa</td><td>${agreement}/4</td><td class="score ${score(row) >= .7 ? 'high' : ''}">${Math.round(score(row) * 100)}%</td><td><span class="status ${flagged ? 'anomaly' : ''}">${flagged ? escapeHtml(severity) : 'Normal'}</span></td></tr>`;
    }).join('') : '<tr><td colspan="8" class="loading-row">No observations match this view</td></tr>';
    $('table-summary').textContent = state.filtered.length ? `Showing ${visible.length} of ${state.filtered.length} observations` : 'No matching observations'; $('load-more').disabled = state.visibleRows >= state.filtered.length;
    document.querySelectorAll('[data-row-index]').forEach((row) => row.addEventListener('click', () => openDetails(state.filtered[Number(row.dataset.rowIndex)])));
}

function openDetails(row) {
    if (!row) return;
    $('dialog-title').textContent = `${station(row)} · ${formatDate(timestamp(row))}`;
    const modelRows = [['Isolation Forest', row.IF_Anomaly], ['ECOD', row.ECOD_Anomaly], ['COPOD', row.COPOD_Anomaly], ['HBOS', row.HBOS_Anomaly]];
    const modelMarkup = modelRows.map(([name, value]) => `${name}: ${Number(value) === 1 ? 'ANOMALY' : 'NORMAL'}`).join('<br>');
    const qcRaw = field(row, 'qc_failed');
    const qcFlags = field(row, 'qc_flags');
    const qcDetail = qcRaw === '' ? 'Unavailable' : `${String(qcRaw).toLowerCase() === 'true' ? 'FAIL' : 'PASS'}${qcFlags ? ` · ${qcFlags.split(',').join(', ')}` : ''}`;
    const healthStatus = field(row, 'health_status');
    const healthScoreRaw = field(row, 'health_score');
    const healthDetail = healthStatus ? `${healthStatus}${healthScoreRaw === '' ? '' : ` · ${Math.round(number(healthScoreRaw))}%`}` : 'Unavailable';
    const maintenance = field(row, 'maintenance_recommendation');
    const shapAvailable = String(field(row, 'SHAP_Available')).toLowerCase() === 'true';
    const shapContribRaw = field(row, 'SHAP_Top_Contribution');
    const shapDetail = shapAvailable
        ? `${field(row, 'SHAP_Top_Feature') || 'Unavailable'}${shapContribRaw === '' ? '' : ` (contribution ${Number(shapContribRaw).toFixed(3)})`} · ${field(row, 'SHAP_Note') || 'Feature contribution only; not causal proof.'}`
        : (field(row, 'SHAP_Note') || 'SHAP attribution unavailable for this observation.');
    $('dialog-content').innerHTML = `<div class="detail-item"><small>Status</small><strong>${anomaly(row) ? 'ANOMALY' : 'NORMAL'}</strong></div><div class="detail-item"><small>Model agreement</small><strong>${field(row, 'Model_Agreement') || 0}/4</strong></div><div class="detail-item"><small>Root cause</small><strong>${escapeHtml(field(row, 'root_cause') || 'Not assigned')}</strong></div><div class="detail-item"><small>Severity / confidence</small><strong>${escapeHtml(field(row, 'severity') || 'LOW')} / ${(number(field(row, 'confidence')) * 100).toFixed(0)}%</strong></div><div class="detail-item"><small>QC status</small><strong>${escapeHtml(qcDetail)}</strong></div><div class="detail-item"><small>Sensor health</small><strong>${escapeHtml(healthDetail)}</strong></div><div class="detail-item detail-wide"><small>Models</small><strong>${modelMarkup}</strong></div><div class="detail-item detail-wide"><small>Explanation</small><strong>${escapeHtml(field(row, 'explanation') || 'No explanation available.')}</strong></div><div class="detail-item detail-wide"><small>SHAP</small><strong>${escapeHtml(shapDetail)}</strong></div>${maintenance ? `<div class="detail-item detail-wide"><small>Maintenance</small><strong>${escapeHtml(maintenance)}</strong></div>` : ''}`;
    $('observation-dialog').showModal();
}

function drawTrend(rows) {
    const canvas = $('trend-chart'); const empty = $('trend-empty'); if (!rows.length) { empty.style.display = 'block'; return; } empty.style.display = 'none';
    const rect = canvas.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1; canvas.width = rect.width * ratio; canvas.height = rect.height * ratio; const ctx = canvas.getContext('2d'); ctx.scale(ratio, ratio);
    const width = rect.width; const height = rect.height; const pad = { top: 16, right: 10, bottom: 28, left: 35 }; const grouped = new Map();
    rows.forEach((row) => { const key = timestamp(row); if (!grouped.has(key)) grouped.set(key, []); grouped.get(key).push(row); });
    const points = [...grouped.entries()].sort((a, b) => new Date(a[0]) - new Date(b[0])).slice(-30).map(([date, dateRows]) => ({ date, score: Math.max(...dateRows.map(score)), flagged: dateRows.some(anomaly) }));
    const x = (index) => pad.left + (index / Math.max(points.length - 1, 1)) * (width - pad.left - pad.right); const y = (value) => pad.top + (1 - value) * (height - pad.top - pad.bottom);
    ctx.clearRect(0, 0, width, height); ctx.font = '10px DM Sans'; ctx.strokeStyle = '#e5ebea'; ctx.fillStyle = '#8b9697'; ctx.lineWidth = 1;
    [0, .5, 1].forEach((tick) => { ctx.beginPath(); ctx.moveTo(pad.left, y(tick)); ctx.lineTo(width - pad.right, y(tick)); ctx.stroke(); ctx.fillText(`${Math.round(tick * 100)}%`, 0, y(tick) + 3); });
    ctx.beginPath(); points.forEach((point, index) => index ? ctx.lineTo(x(index), y(point.score)) : ctx.moveTo(x(index), y(point.score))); ctx.strokeStyle = '#486e65'; ctx.lineWidth = 2; ctx.stroke();
    points.forEach((point, index) => { if (!point.flagged) return; ctx.beginPath(); ctx.arc(x(index), y(point.score), 3.5, 0, Math.PI * 2); ctx.fillStyle = '#a15d53'; ctx.fill(); });
    ctx.fillStyle = '#8b9697'; ctx.fillText(formatDate(points[0].date, false), pad.left, height - 6); ctx.fillText(formatDate(points.at(-1).date, false), width - 72, height - 6);
}

function handleUpload(event) {
    const file = event.target.files[0]; if (!file) return; const reader = new FileReader();
    reader.onload = () => { try { const rows = parseCSV(reader.result); if (!rows.length) throw new Error('The CSV contains no rows.'); const headers = Object.keys(rows[0]); const required = [['station_id', 'Location'], ['timestamp', 'DateTime'], ['temperature', 'Temperature_C'], ['pressure', 'Pressure_hPa'], ['humidity', 'Humidity_Percent']]; const missing = required.filter(([canonical, legacy]) => !headers.includes(canonical) && !headers.includes(legacy)).map(([canonical]) => canonical); if (missing.length) throw new Error(`Missing required columns: ${missing.join(', ')}`); const hasResults = headers.includes('Final_Anomaly') || headers.includes('Ensemble_Anomaly'); loadData(rows, hasResults ? `Uploaded analysis · ${file.name}` : `Uploaded preview · ${file.name}`); showToast(hasResults ? 'Analysis results loaded.' : 'CSV validated. Backend analysis is required for anomaly results.'); } catch (error) { setSync('Upload rejected'); showToast(error.message); } };
    reader.readAsText(file);
}

$('refresh-button').addEventListener('click', refresh); $('csv-upload').addEventListener('change', handleUpload); $('search-input').addEventListener('input', () => { state.visibleRows = 10; renderTable(); }); $('status-filter').addEventListener('change', () => { state.visibleRows = 10; renderTable(); }); $('load-more').addEventListener('click', () => { state.visibleRows += 10; renderTable(); }); $('dialog-close').addEventListener('click', () => $('observation-dialog').close()); window.addEventListener('resize', () => { if (state.rows.length) drawTrend(state.rows); }); loadData();
