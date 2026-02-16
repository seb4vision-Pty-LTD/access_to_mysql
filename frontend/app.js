/**
 * Access to MySQL Converter - Frontend Application
 * Production-ready JavaScript with full API integration
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
const SESSION_ID = 'session_' + Date.now();

// Application State
const state = {
    accessConnected: false,
    mysqlConnected: false,
    accessFilepath: null,
    accessTables: [],
    selectedTables: new Set(),
    mysqlTables: [],
    uploadedFilename: null
};

/**
 * Utility Functions
 */
function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    element.innerHTML = `
        <div class="status ${type}">
            <span>${icons[type] || ''}</span>
            <span>${message}</span>
        </div>
    `;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showLoader(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '<div class="loader"></div>';
}

/**
 * Access Database Functions
 */
async function uploadAndConnectAccess() {
    const fileInput = document.getElementById('accessFile');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showStatus('connectionStatus', 'Please select an Access database file', 'error');
        return;
    }

    const file = fileInput.files[0];
    
    try {
        showStatus('connectionStatus', 'Uploading Access database file...', 'info');
        
        // Upload file (include session id so backend can cleanup previous uploads)
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', SESSION_ID);
        
        const uploadResponse = await fetch(`${API_BASE_URL}/upload-access`, {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error('Failed to upload file');
        }
        
        const uploadData = await uploadResponse.json();
        state.uploadedFilename = uploadData.filename;
        state.accessFilepath = uploadData.filepath;
        
        showStatus('connectionStatus', 'Connecting to Access database...', 'info');
        const payload = JSON.stringify({
                filename: state.uploadedFilename,
                session_id: SESSION_ID
            });
        // Connect to Access database
        const connectResponse = await fetch(`${API_BASE_URL}/connect-access`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: payload
        });
        
        if (!connectResponse.ok) {
            const error = await connectResponse.json();
            throw new Error(error.error || 'Failed to connect to Access database');
        }
        
        const connectData = await connectResponse.json();
        console.log('Access connection data:', connectData);
        state.accessConnected = true;
        state.accessTables = connectData.tables;
        
        document.getElementById('accessStatus').className = 'connection-status connected';
        document.getElementById('loadTablesBtn').disabled = false;
        
        showStatus('connectionStatus', 
            `✅ Successfully connected to ${file.name} (${connectData.table_count} tables found)`, 
            'success');
        
        // Auto-load tables
        await loadAccessTables();
        
    } catch (error) {
        console.error('Error connecting to Access:', error);
        showStatus('connectionStatus', 
            `Error connecting to Access database: ${error.message}`, 
            'error');
    }
}


/**
 * Purge all uploaded files on the server
 */
async function purgeUploads() {
    if (!confirm('Purge all uploaded files? This cannot be undone.')) return;

    try {
        showStatus('connectionStatus', 'Purging uploaded files...', 'info');

        const response = await fetch(`${API_BASE_URL}/purge-uploads`, {
            method: 'POST'
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Purge failed');
        }

        const data = await response.json();

        showStatus('connectionStatus', `✅ Purged ${data.removed_count} files`, 'success');

        // If the current session had an uploaded file reference, clear it
        if (state.uploadedFilename) {
            state.uploadedFilename = null;
            state.accessFilepath = null;
            document.getElementById('loadTablesBtn').disabled = true;
            document.getElementById('accessStatus').className = 'connection-status disconnected';
        }

    } catch (error) {
        console.error('Purge uploads error:', error);
        showStatus('connectionStatus', `Purge failed: ${error.message}`, 'error');
    }
}

async function loadAccessTables() {
    if (!state.accessConnected) {
        showStatus('connectionStatus', 'Please connect to Access database first', 'error');
        return;
    }

    const tablesDiv = document.getElementById('accessTables');
    const statsDiv = document.getElementById('tableStats');
    
    showLoader('accessTables');

    try {
        // Display tables
        tablesDiv.innerHTML = state.accessTables.map(table => `
            <div class="table-item" onclick="toggleTableByClick('${table}')">
                <input type="checkbox" id="table_${table}" 
                       onchange="toggleTable('${table}')" 
                       onclick="event.stopPropagation()"
                       ${state.selectedTables.has(table) ? 'checked' : ''}>
                <label for="table_${table}">${table}</label>
            </div>
        `).join('');

        // Show stats
        statsDiv.classList.remove('hidden');
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${state.accessTables.length}</div>
                <div class="stat-label">Total Tables</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${state.selectedTables.size}</div>
                <div class="stat-label">Selected</div>
            </div>
        `;

        updateExportButton();
        
    } catch (error) {
        console.error('Error loading tables:', error);
        showStatus('connectionStatus', `Error loading tables: ${error.message}`, 'error');
    }
}

function toggleTable(tableName) {
    if (state.selectedTables.has(tableName)) {
        state.selectedTables.delete(tableName);
    } else {
        state.selectedTables.add(tableName);
    }
    updateTableStats();
    updateExportButton();
}

function toggleTableByClick(tableName) {
    const checkbox = document.getElementById(`table_${tableName}`);
    checkbox.checked = !checkbox.checked;
    toggleTable(tableName);
}

function selectAllTables() {
    state.accessTables.forEach(table => state.selectedTables.add(table));
    loadAccessTables();
}

function deselectAllTables() {
    state.selectedTables.clear();
    loadAccessTables();
}

function updateTableStats() {
    const statsDiv = document.getElementById('tableStats');
    if (!statsDiv.classList.contains('hidden')) {
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${state.accessTables.length}</div>
                <div class="stat-label">Total Tables</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${state.selectedTables.size}</div>
                <div class="stat-label">Selected</div>
            </div>
        `;
    }
}

/**
 * MySQL Database Functions
 */
async function connectMySQL() {
    const host = document.getElementById('mysqlHost').value;
    const port = document.getElementById('mysqlPort').value;
    const user = document.getElementById('mysqlUser').value;
    const password = document.getElementById('mysqlPassword').value;
    const database = document.getElementById('mysqlDatabase').value;

    if (!host || !user || !database) {
        showStatus('connectionStatus', 'Please fill in all required MySQL fields', 'error');
        return;
    }

    try {
        showStatus('connectionStatus', 'Connecting to MySQL...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/connect-mysql`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                host,
                port: parseInt(port),
                user,
                password,
                database,
                session_id: SESSION_ID
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to connect to MySQL');
        }

        const data = await response.json();
        
        state.mysqlConnected = true;
        state.mysqlTables = data.existing_tables || [];
        
        document.getElementById('mysqlStatus').className = 'connection-status connected';
        document.getElementById('refreshMySQLBtn').disabled = false;
        
        showStatus('connectionStatus', 
            `✅ Successfully connected to MySQL database: ${database}`, 
            'success');
        
        updateExportButton();
        await refreshMySQLTables();
        
    } catch (error) {
        console.error('Error connecting to MySQL:', error);
        showStatus('connectionStatus', 
            `Error connecting to MySQL: ${error.message}`, 
            'error');
    }
}

async function refreshMySQLTables() {
    if (!state.mysqlConnected) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/get-mysql-tables`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: SESSION_ID })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch MySQL tables');
        }

        const data = await response.json();
        state.mysqlTables = data.tables || [];
        
        const select = document.getElementById('mysqlTableSelect');
        select.innerHTML = '<option value="">-- Select a table --</option>' +
            state.mysqlTables.map(table => `<option value="${table}">${table}</option>`).join('');
        
    } catch (error) {
        console.error('Error refreshing MySQL tables:', error);
    }
}

async function viewMySQLTable() {
    const select = document.getElementById('mysqlTableSelect');
    const tableName = select.value;
    
    if (!tableName) {
        document.getElementById('mysqlTablePreview').innerHTML = '';
        return;
    }

    const preview = document.getElementById('mysqlTablePreview');
    showLoader('mysqlTablePreview');

    try {
        const response = await fetch(`${API_BASE_URL}/preview-table`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: SESSION_ID,
                table_name: tableName,
                source: 'mysql',
                limit: 100
            })
        });

        if (!response.ok) {
            throw new Error('Failed to preview table');
        }

        const data = await response.json();
        const previewData = data.data;
        
        preview.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        ${previewData.columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${previewData.rows.map(row => `
                        <tr>
                            ${row.map(cell => `<td>${cell !== null ? cell : '<em>NULL</em>'}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            <p style="margin-top: 15px; color: var(--text-light); text-align: center;">
                Showing ${previewData.row_count} rows
            </p>
        `;
        
    } catch (error) {
        console.error('Error previewing table:', error);
        preview.innerHTML = `
            <div class="status error">
                Failed to load table preview: ${error.message}
            </div>
        `;
    }
}

/**
 * Export Functions
 */
function updateExportButton() {
    const exportBtn = document.getElementById('exportBtn');
    exportBtn.disabled = !(state.accessConnected && 
                           state.mysqlConnected && 
                           state.selectedTables.size > 0);
}

async function startExport() {
    const overrideData = document.getElementById('overrideData').checked;
    const createTables = document.getElementById('createTables').checked;
    const batchSize = parseInt(document.getElementById('batchSize').value);
    
    const progressContainer = document.getElementById('exportProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const resultsDiv = document.getElementById('exportResults');
    
    progressContainer.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    
    showStatus('exportStatus', 'Starting export process...', 'info');

    try {
        const tables = Array.from(state.selectedTables);
        
        progressText.textContent = `Exporting ${tables.length} tables...`;
        
        const response = await fetch(`${API_BASE_URL}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: SESSION_ID,
                tables: tables,
                options: {
                    override_data: overrideData,
                    create_tables: createTables,
                    batch_size: batchSize
                }
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Export failed to start');
        }

        const data = await response.json();
        const jobId = data.job_id;

        showStatus('exportStatus', `Export started (job ${jobId})`, 'info');

        // Disable export button and MySQL refresh while running
        const exportBtn = document.getElementById('exportBtn');
        exportBtn.disabled = true;
        const refreshBtn = document.getElementById('refreshMySQLBtn');
        if (refreshBtn) refreshBtn.disabled = true;

        // Add cancel button next to export button
        let cancelBtn = document.getElementById('cancelExportBtn');
        if (!cancelBtn) {
            cancelBtn = document.createElement('button');
            cancelBtn.id = 'cancelExportBtn';
            cancelBtn.className = 'btn btn-danger';
            cancelBtn.textContent = '⏸️ Cancel Export';
            cancelBtn.style.marginLeft = '12px';
            cancelBtn.onclick = async () => {
                try {
                    await fetch(`${API_BASE_URL}/export-cancel`, { method: 'POST' });
                    showStatus('exportStatus', 'Cancel requested...', 'warning');
                } catch (err) {
                    console.error('Error requesting cancel:', err);
                }
            };

            exportBtn.parentNode.insertBefore(cancelBtn, exportBtn.nextSibling);
        }

        // Poll status
        let polling = true;
        const pollInterval = 1000;

        const poll = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/export-status`);
                if (!res.ok) throw new Error('Failed to fetch export status');
                const s = await res.json();
                const status = s.status || {};

                // Update progress UI
                const total = status.tables_total || 0;
                const done = status.tables_done || 0;
                const current = status.current_table || '';
                const rowsTotal = status.total_rows_exported || 0;

                let percent = 0;
                if (total > 0) {
                    percent = Math.round((done / total) * 100);
                }

                progressFill.style.width = percent + '%';
                progressFill.textContent = percent + '%';

                let text = '';
                if (status.state === 'running') {
                    text = `Table ${done}/${total}` + (current ? ` — ${current}` : '') + ` — ${rowsTotal} rows exported`;
                } else if (status.state === 'completed') {
                    text = `Export completed — ${rowsTotal} rows exported`;
                } else if (status.state === 'failed') {
                    text = `Export failed: ${status.error || 'unknown error'}`;
                } else if (status.state === 'cancelled') {
                    text = 'Export cancelled';
                } else {
                    text = `Status: ${status.state || 'idle'}`;
                }

                progressText.textContent = text;

                // When finished, stop polling and cleanup
                if (['completed', 'failed', 'cancelled'].includes(status.state)) {
                    polling = false;
                    // cleanup UI
                    exportBtn.disabled = false;
                    if (refreshBtn && state.mysqlConnected) refreshBtn.disabled = false;
                    if (cancelBtn && cancelBtn.parentNode) cancelBtn.parentNode.removeChild(cancelBtn);

                    // Final status message
                    if (status.state === 'completed') {
                        showStatus('exportStatus', `✅ Export finished — ${rowsTotal} rows exported`, 'success');
                        // Refresh MySQL tables
                        await refreshMySQLTables();
                    } else if (status.state === 'failed') {
                        showStatus('exportStatus', `❌ Export failed: ${status.error || ''}`, 'error');
                    } else if (status.state === 'cancelled') {
                        showStatus('exportStatus', '⚠️ Export cancelled by user', 'warning');
                    }
                }

            } catch (err) {
                console.error('Polling error:', err);
                // keep polling; show an error indicator
                progressText.textContent = 'Error fetching status';
            }
        };

        // Start polling loop
        const intervalId = setInterval(async () => {
            if (!polling) {
                clearInterval(intervalId);
                return;
            }
            await poll();
        }, pollInterval);

        // run first poll immediately
        await poll();
        
    } catch (error) {
        console.error('Export error:', error);
        showStatus('exportStatus', 
            `Export failed: ${error.message}`, 
            'error');
        
        progressFill.style.width = '0%';
        progressText.textContent = 'Export failed';
    }
}

/**
 * Configuration Management
 */
function showSaveConfigDialog() {
    if (state.selectedTables.size === 0) {
        showStatus('exportStatus', 'Please select tables before saving configuration', 'error');
        return;
    }

    const configName = prompt('Enter a name for this configuration:');
    if (!configName) return;

    saveConfiguration(configName);
}

async function saveConfiguration(configName) {
    try {
        const configData = {
            config_name: configName,
            access_file: {
                filename: state.uploadedFilename,
                filepath: state.accessFilepath
            },
            tables: Array.from(state.selectedTables),
            mysql: {
                host: document.getElementById('mysqlHost').value,
                port: parseInt(document.getElementById('mysqlPort').value),
                user: document.getElementById('mysqlUser').value,
                database: document.getElementById('mysqlDatabase').value
            },
            options: {
                override_data: document.getElementById('overrideData').checked,
                create_tables: document.getElementById('createTables').checked,
                batch_size: parseInt(document.getElementById('batchSize').value)
            }
        };

        const response = await fetch(`${API_BASE_URL}/save-config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_name: configName,
                config_data: configData
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save configuration');
        }

        const data = await response.json();
        
        showStatus('exportStatus', `✅ Configuration "${configName}" saved successfully!`, 'success');
        
        await loadSavedConfigs();
        
    } catch (error) {
        console.error('Error saving configuration:', error);
        showStatus('exportStatus', `Failed to save configuration: ${error.message}`, 'error');
    }
}

async function loadSavedConfigs() {
    const configList = document.getElementById('configList');
    
    try {
        const response = await fetch(`${API_BASE_URL}/list-configs`);
        
        if (!response.ok) {
            throw new Error('Failed to load configurations');
        }

        const data = await response.json();
        const configs = data.configs || [];
        
        if (configs.length === 0) {
            configList.innerHTML = '<p style="color: var(--text-light); text-align: center; padding: 20px;">No saved configurations</p>';
            return;
        }

        configList.innerHTML = configs.map(config => `
            <div class="config-card">
                <div class="config-header">
                    <div>
                        <div class="config-title">${config.config_name}</div>
                        <div class="config-meta">
                            <div>📊 ${config.table_count} tables: ${config.tables.slice(0, 3).join(', ')}${config.table_count > 3 ? '...' : ''}</div>
                            <div>📁 Access: ${config.access_file}</div>
                            <div>🗄️ MySQL: ${config.mysql_database}</div>
                            <div>🕒 ${new Date(config.created_at).toLocaleString()}</div>
                        </div>
                    </div>
                    <div class="button-group" style="flex-direction: column;">
                        <button class="btn btn-secondary" onclick="applyConfig('${config.config_id}')">
                            Apply
                        </button>
                        <button class="btn btn-danger" onclick="deleteConfig('${config.config_id}')">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading configurations:', error);
        configList.innerHTML = `
            <div class="status error">
                Failed to load configurations: ${error.message}
            </div>
        `;
    }
}

async function applyConfig(configId) {
    try {
        const response = await fetch(`${API_BASE_URL}/load-config/${configId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load configuration');
        }

        const data = await response.json();
        const config = data.config;
        
        // Apply MySQL settings
        document.getElementById('mysqlHost').value = config.mysql.host;
        document.getElementById('mysqlPort').value = config.mysql.port;
        document.getElementById('mysqlUser').value = config.mysql.user;
        document.getElementById('mysqlDatabase').value = config.mysql.database;
        
        // Apply options
        document.getElementById('overrideData').checked = config.options.override_data;
        document.getElementById('createTables').checked = config.options.create_tables;
        document.getElementById('batchSize').value = config.options.batch_size;
        
        // Apply table selection
        state.selectedTables = new Set(config.tables);
        
        if (state.accessTables.length > 0) {
            loadAccessTables();
        }
        
        showStatus('exportStatus', `✅ Configuration "${config.config_name}" loaded successfully!`, 'success');
        
    } catch (error) {
        console.error('Error applying configuration:', error);
        showStatus('exportStatus', `Failed to load configuration: ${error.message}`, 'error');
    }
}

async function deleteConfig(configId) {
    if (!confirm('Are you sure you want to delete this configuration?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/delete-config/${configId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete configuration');
        }

        showStatus('exportStatus', 'Configuration deleted successfully', 'info');
        await loadSavedConfigs();
        
    } catch (error) {
        console.error('Error deleting configuration:', error);
        showStatus('exportStatus', `Failed to delete configuration: ${error.message}`, 'error');
    }
}

/**
 * Initialize Application
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Access to MySQL Converter initialized');
    loadSavedConfigs();
});
