// ETR Web Application - Frontend JavaScript

// State management
const appState = {
    uploadedFile: null,
    processedResult: null,
    currentChart: null,
    systemStatus: null
};

// API Base URL
const API_BASE = '/api';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkSystemStatus();
});

// Initialize application
function initializeApp() {
    console.log('ETR Web Application initialized');
}

// Setup event listeners
function setupEventListeners() {
    // File upload
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');

    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Process button
    document.getElementById('processBtn').addEventListener('click', processFile);

    // Demo button
    document.getElementById('runDemoBtn').addEventListener('click', runDemo);

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

// Check system status
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();

        appState.systemStatus = data;
        updateStatusIndicator(data);
        updateSystemInfo(data);
    } catch (error) {
        console.error('Failed to check system status:', error);
        updateStatusIndicator({ status: 'error' });
    }
}

// Update status indicator
function updateStatusIndicator(status) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = indicator.querySelector('.status-text');
    const statusDot = indicator.querySelector('.status-dot');

    if (status.status === 'running') {
        statusText.textContent = 'System Ready';
        statusDot.style.background = 'var(--success-color)';
    } else {
        statusText.textContent = 'System Error';
        statusDot.style.background = 'var(--danger-color)';
    }
}

// Update system info
function updateSystemInfo(status) {
    const systemStatus = document.getElementById('systemStatus');
    const deps = status.dependencies;

    const html = `
        <p><span class="${deps.numpy ? 'available' : 'unavailable'}">●</span> NumPy: ${deps.numpy ? 'Available' : 'Not installed'}</p>
        <p><span class="${deps.torch ? 'available' : 'unavailable'}">●</span> PyTorch: ${deps.torch ? 'Available' : 'Not installed'}</p>
        <p><span class="${deps.point_cloud_loader ? 'available' : 'unavailable'}">●</span> Point Cloud Loader: ${deps.point_cloud_loader ? 'Available' : 'Not installed'}</p>
        <p><span class="${deps.etr_core ? 'available' : 'unavailable'}">●</span> ETR Core: ${deps.etr_core ? 'Available' : 'Not installed'}</p>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
            <p><strong>Statistics:</strong></p>
            <p>Uploads: ${status.statistics.uploads}</p>
            <p>Results: ${status.statistics.results}</p>
        </div>
    `;

    systemStatus.innerHTML = html;
}

// File drag handlers
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// File select handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// Upload file
async function uploadFile(file) {
    showLoading('Uploading file...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            appState.uploadedFile = data.file;
            displayFileInfo(data.file);
            showToast('File uploaded successfully!', 'success');
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display file info
function displayFileInfo(file) {
    const section = document.getElementById('fileInfoSection');
    const details = document.getElementById('fileDetails');

    const html = `
        <p><strong>Name:</strong> <span>${file.name}</span></p>
        <p><strong>Size:</strong> <span>${file.size_mb} MB</span></p>
        <p><strong>Format:</strong> <span>${file.extension.toUpperCase()}</span></p>
        <p><strong>Uploaded:</strong> <span>${new Date(file.modified).toLocaleString()}</span></p>
    `;

    details.innerHTML = html;
    section.classList.remove('hidden');
}

// Process file through ETR
async function processFile() {
    if (!appState.uploadedFile) {
        showToast('Please upload a file first', 'warning');
        return;
    }

    showLoading('Processing through ETR...');

    try {
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: appState.uploadedFile.id,
                options: {}
            })
        });

        const data = await response.json();

        if (response.ok) {
            appState.processedResult = data.result;
            displayResults(data.result);
            showToast('Processing completed!', 'success');
        } else {
            throw new Error(data.error || 'Processing failed');
        }
    } catch (error) {
        console.error('Processing error:', error);
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Run ETR demo
async function runDemo() {
    const base = parseFloat(document.getElementById('demoBase').value);
    const height = parseFloat(document.getElementById('demoHeight').value);
    const hypotenuse = parseFloat(document.getElementById('demoHyp').value);
    const levels = parseInt(document.getElementById('demoLevels').value);

    showLoading('Running ETR demo...');

    try {
        const response = await fetch(`${API_BASE}/demo/etr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ base, height, hypotenuse, levels })
        });

        const data = await response.json();

        if (response.ok) {
            displayDemoResults(data);
            showToast('Demo completed!', 'success');
        } else {
            throw new Error(data.error || 'Demo failed');
        }
    } catch (error) {
        console.error('Demo error:', error);
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(result) {
    const content = document.getElementById('resultsContent');

    const html = `
        <div class="result-item">
            <h3>Point Cloud Information</h3>
            <div class="result-grid">
                <div class="result-field">
                    <span class="result-label">Points</span>
                    <span class="result-value">${result.num_points.toLocaleString()}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Colors</span>
                    <span class="result-value">${result.has_colors ? 'Yes' : 'No'}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Normals</span>
                    <span class="result-value">${result.has_normals ? 'Yes' : 'No'}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">ETR Processed</span>
                    <span class="result-value">${result.etr_processed ? 'Yes' : 'No'}</span>
                </div>
            </div>
            <p style="margin-top: 15px; color: var(--text-secondary); font-size: 0.9em;">
                ${result.message}
            </p>
        </div>
    `;

    content.innerHTML = html;
}

// Display demo results
function displayDemoResults(data) {
    const content = document.getElementById('resultsContent');

    let html = `
        <div class="result-item">
            <h3>ETR Transformation Results</h3>
            <p><strong>Input Triangle:</strong> Base=${data.input.base}, Height=${data.input.height}, Hyp=${data.input.hypotenuse}</p>
            <p><strong>Levels Generated:</strong> ${data.levels}</p>
        </div>
    `;

    data.results.forEach((result, idx) => {
        const rt = result.right_triangle;
        const lt = result.left_triangle;

        html += `
            <div class="result-item">
                <h3>Level ${result.level}</h3>
                <div class="result-grid">
                    <div class="result-field">
                        <span class="result-label">RT Base</span>
                        <span class="result-value">${formatNumber(rt.base)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">RT Height</span>
                        <span class="result-value">${formatNumber(rt.height)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">RT Hypotenuse</span>
                        <span class="result-value">${formatNumber(rt.hypotenuse)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Scaling Factor</span>
                        <span class="result-value">${formatNumber(rt.scaling_factor)}</span>
                    </div>
                </div>
                <p style="margin-top: 10px; color: var(--text-secondary); font-size: 0.85em;">
                    Left Triangle: Base=${formatNumber(lt.base)}, Height=${formatNumber(lt.height)}, Hyp=${formatNumber(lt.hypotenuse)}
                </p>
                <p style="color: ${rt.valid && lt.valid ? 'var(--success-color)' : 'var(--danger-color)'}; font-size: 0.85em;">
                    ${rt.valid && lt.valid ? '✓ Valid triangles' : '✗ Invalid triangles'}
                </p>
            </div>
        `;
    });

    content.innerHTML = html;

    // Update chart with demo results
    updateChart(data.results);

    // Update data table
    updateDataTable(data.results);
}

// Update chart
function updateChart(results) {
    const canvas = document.getElementById('resultsChart');
    const ctx = canvas.getContext('2d');

    // Destroy previous chart if exists
    if (appState.currentChart) {
        appState.currentChart.destroy();
    }

    const labels = results.map(r => `Level ${r.level}`);
    const scalingFactors = results.map(r => r.right_triangle.scaling_factor);

    appState.currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Scaling Factor',
                data: scalingFactors,
                borderColor: 'rgba(0, 217, 255, 1)',
                backgroundColor: 'rgba(0, 217, 255, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#eaeaea', font: { size: 14 } }
                },
                tooltip: {
                    backgroundColor: 'rgba(22, 33, 62, 0.9)',
                    titleColor: '#00d9ff',
                    bodyColor: '#eaeaea',
                    borderColor: '#2d3748',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(45, 55, 72, 0.5)' }
                },
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(45, 55, 72, 0.5)' }
                }
            }
        }
    });
}

// Update data table
function updateDataTable(results) {
    const container = document.getElementById('dataTable');

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Level</th>
                    <th>RT Base</th>
                    <th>RT Height</th>
                    <th>RT Hyp</th>
                    <th>Scaling Factor</th>
                    <th>Valid</th>
                </tr>
            </thead>
            <tbody>
    `;

    results.forEach(result => {
        const rt = result.right_triangle;
        html += `
            <tr>
                <td>${result.level}</td>
                <td>${formatNumber(rt.base)}</td>
                <td>${formatNumber(rt.height)}</td>
                <td>${formatNumber(rt.hypotenuse)}</td>
                <td>${formatNumber(rt.scaling_factor)}</td>
                <td style="color: ${rt.valid ? 'var(--success-color)' : 'var(--danger-color)'}">
                    ${rt.valid ? '✓' : '✗'}
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    const tabMap = {
        'chart': 'chartTab',
        '3d': '3dTab',
        'data': 'dataTab'
    };

    const targetPane = document.getElementById(tabMap[tabName]);
    if (targetPane) {
        targetPane.classList.add('active');
    }
}

// Utility functions
function formatNumber(num) {
    if (num === 0) return '0';
    if (Math.abs(num) < 0.001) {
        return num.toExponential(2);
    }
    return num.toFixed(4);
}

function showLoading(message) {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    text.textContent = message;
    overlay.classList.remove('hidden');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    toastMessage.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Export for debugging
window.appState = appState;
window.checkSystemStatus = checkSystemStatus;
