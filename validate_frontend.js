const fs = require('fs');
const path = require('path');

// Copy parseCSV and helpers from app.js
const parseCSV = (text) => {
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
};

const number = (value) => Number.parseFloat(value) || 0;
const field = (row, canonical, legacy = canonical) => row[canonical] ?? row[legacy] ?? '';
const station = (row) => field(row, 'station_id', 'Location');
const timestamp = (row) => field(row, 'timestamp', 'DateTime');
const anomaly = (row) => Number(field(row, 'Final_Anomaly', 'Ensemble_Anomaly')) === 1;
const score = (row) => number(field(row, 'Final_Score', 'Ensemble_Score'));

const csvPath = path.join(__dirname, 'outputs/exports/anomaly_detection_results.csv');
const text = fs.readFileSync(csvPath, 'utf8');
const rows = parseCSV(text);

console.log('Parsed rows:', rows.length);
console.log('First row keys count:', Object.keys(rows[0] || {}).length);

const firstRow = rows[0];
if (firstRow) {
    console.log('First row station_id:', firstRow.station_id);
    console.log('First row timestamp:', firstRow.timestamp);
    console.log('First row Final_Anomaly:', firstRow.Final_Anomaly);
    console.log('First row Model_Agreement:', firstRow.Model_Agreement);
    console.log('First row IF_Score:', firstRow.IF_Score);
    console.log('First row ECOD_Score:', firstRow.ECOD_Score);
    console.log('First row SHAP_Available:', firstRow.SHAP_Available);
    console.log('First row SHAP_Top_Feature:', firstRow.SHAP_Top_Feature);
}

const anomalies = rows.filter(r => Number(r.Final_Anomaly) === 1);
console.log('Anomalies:', anomalies.length);

const agreement3 = rows.filter(r => Number(r.Model_Agreement) >= 3);
console.log('Model agreement >=3:', agreement3.length);

const stations = [...new Set(rows.map(r => r.station_id).filter(Boolean))];
console.log('Stations:', stations.length);

const emptyEcod = rows.filter(r => r.ECOD_Score === '' || r.ECOD_Score === undefined);
console.log('Empty ECOD_Score:', emptyEcod.length);

const nanEcod = rows.filter(r => r.ECOD_Score === 'NaN' || r.ECOD_Score === 'nan' || r.ECOD_Score === 'N/A');
console.log('NaN-string ECOD_Score:', nanEcod.length);

// Test sorting
const sorted = rows.sort((a, b) => new Date(timestamp(b)) - new Date(timestamp(a)));
console.log('Sorted first timestamp:', timestamp(sorted[0]));
console.log('Sorted last timestamp:', timestamp(sorted[sorted.length - 1]));

// Test render logic
const sortedAnomalies = sorted.filter(anomaly);
const sortedStations = [...new Set(sorted.map(station).filter(Boolean))];
const agreementRows = sorted.filter((row) => number(row.Model_Agreement) >= 3);
const dates = sorted.map(timestamp).filter(Boolean).sort();

console.log('\nRender metrics:');
console.log('Active anomalies:', sortedAnomalies.length);
console.log('Anomaly rate:', ((sortedAnomalies.length / Math.max(sorted.length, 1)) * 100).toFixed(2) + '%');
console.log('Station count:', sortedStations.length);
console.log('Observation count:', sorted.length);
console.log('Agreement rate:', ((agreementRows.length / Math.max(sorted.length, 1)) * 100).toFixed(1) + '%');

// Test first anomaly details
const firstAnomaly = anomalies[0];
if (firstAnomaly) {
    console.log('\nFirst anomaly details:');
    console.log('Station:', station(firstAnomaly));
    console.log('Timestamp:', timestamp(firstAnomaly));
    console.log('Root cause:', field(firstAnomaly, 'root_cause'));
    console.log('Severity:', field(firstAnomaly, 'severity', 'Anomaly_Severity'));
    console.log('Confidence:', (number(field(firstAnomaly, 'confidence')) * 100).toFixed(0) + '%');
    console.log('SHAP_Top_Feature:', field(firstAnomaly, 'SHAP_Top_Feature'));
    console.log('SHAP_Note:', field(firstAnomaly, 'SHAP_Note'));
    console.log('Explanation:', field(firstAnomaly, 'explanation'));
    
    const modelRows = [['Isolation Forest', firstAnomaly.IF_Anomaly], ['ECOD', firstAnomaly.ECOD_Anomaly], ['COPOD', firstAnomaly.COPOD_Anomaly], ['HBOS', firstAnomaly.HBOS_Anomaly]];
    console.log('Models:', modelRows.map(([name, value]) => `${name}: ${Number(value) === 1 ? 'ANOMALY' : 'NORMAL'}`).join(', '));
}

// Check for any rows where key fields are missing
const missingStation = rows.filter(r => !r.station_id && !r.Location);
const missingTemp = rows.filter(r => r.temperature === '' && r.Temperature_C === '');
console.log('Missing station:', missingStation.length);
console.log('Missing temperature:', missingTemp.length);

// Check QC flags
const qcFlagsRows = rows.filter(r => r.qc_flags && r.qc_flags.trim() !== '');
console.log('Rows with QC flags:', qcFlagsRows.length);
if (qcFlagsRows.length > 0) {
    console.log('Sample QC flags:', qcFlagsRows[0].qc_flags);
}

console.log('\nValidation complete.');
