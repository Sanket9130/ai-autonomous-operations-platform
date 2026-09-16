/**
 * Autonomous Operations Platform Frontend Application
 * Interacts with Backend Orchestrator APIs (Port 5000)
 */

const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000';

// App State
const state = {
  assets: [],
  inventory: [],
  technicians: [],
  logs: [],
  activeTab: 'tab-assets',
  executingAssetId: null,
};

// DOM Element References
const elements = {
  backendStatusText: document.getElementById('backend-status-text'),
  backendStatusPill: document.getElementById('backend-status-pill'),
  aiStatusText: document.getElementById('ai-status-text'),
  
  // KPI Elements
  valTotalAssets: document.getElementById('val-total-assets'),
  valCriticalAssets: document.getElementById('val-critical-assets'),
  valTotalInventory: document.getElementById('val-total-inventory'),
  valActiveTechs: document.getElementById('val-active-techs'),

  // Containers
  assetsContainer: document.getElementById('assets-container'),
  inventoryTbody: document.getElementById('inventory-tbody'),
  techniciansContainer: document.getElementById('technicians-container'),
  logsTbody: document.getElementById('logs-tbody'),

  // Tabs
  tabBtns: document.querySelectorAll('.tab-btn'),
  tabPanes: document.querySelectorAll('.tab-pane'),

  // Error Banner
  globalErrorBanner: document.getElementById('global-error-banner'),
  globalErrorMsg: document.getElementById('global-error-msg'),
  btnRetryConnection: document.getElementById('btn-retry-connection'),

  // Refresh Buttons
  btnRefreshAssets: document.getElementById('btn-refresh-assets'),
  btnRefreshInventory: document.getElementById('btn-refresh-inventory'),
  btnRefreshTechnicians: document.getElementById('btn-refresh-technicians'),
  btnRefreshLogs: document.getElementById('btn-refresh-logs'),

  // Modal
  decisionModal: document.getElementById('decision-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  btnModalDismiss: document.getElementById('btn-modal-dismiss'),

  // Modal fields
  modalActionBadge: document.getElementById('modal-action-badge'),
  modalAssetTitle: document.getElementById('modal-asset-title'),
  modalSummaryText: document.getElementById('modal-summary-text'),
  
  resFailureProb: document.getElementById('res-failure-prob'),
  resAssetRisk: document.getElementById('res-asset-risk'),
  resRiskScore: document.getElementById('res-risk-score'),
  resRulDays: document.getElementById('res-rul-days'),
  
  resSparePart: document.getElementById('res-spare-part'),
  resCurrentStock: document.getElementById('res-current-stock'),
  resStockoutRisk: document.getElementById('res-stockout-risk'),
  resReorderQty: document.getElementById('res-reorder-qty'),
  
  resSelectedTech: document.getElementById('res-selected-tech'),
  resTechScore: document.getElementById('res-tech-score'),
  resTechEta: document.getElementById('res-tech-eta'),
  resSlaStatus: document.getElementById('res-sla-status'),
  
  resPreventiveCost: document.getElementById('res-preventive-cost'),
  resFailureCost: document.getElementById('res-failure-cost'),
  resNetSavings: document.getElementById('res-net-savings'),
  resLogId: document.getElementById('res-log-id'),
};

// ---------------------------------------------------------
// 1. API Helper Functions
// ---------------------------------------------------------
async function fetchFromBackend(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }

    clearError();
    updateConnectionStatus(true);
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    updateConnectionStatus(false);
    showError(`API Error (${endpoint}): ${err.message}`);
    throw err;
  }
}

function updateConnectionStatus(isOnline) {
  if (isOnline) {
    elements.backendStatusText.textContent = 'Connected (Port 5000)';
    elements.backendStatusPill.querySelector('.status-dot').classList.remove('error');
    elements.aiStatusText.textContent = 'Ready (Port 8000)';
  } else {
    elements.backendStatusText.textContent = 'Offline / Error';
    elements.backendStatusPill.querySelector('.status-dot').classList.add('error');
    elements.aiStatusText.textContent = 'Unreachable';
  }
}

function showError(msg) {
  elements.globalErrorMsg.textContent = msg;
  elements.globalErrorBanner.classList.remove('hidden');
}

function clearError() {
  elements.globalErrorBanner.classList.add('hidden');
}

// ---------------------------------------------------------
// 2. Data Loaders
// ---------------------------------------------------------
async function loadAssets() {
  elements.assetsContainer.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <span>Loading telemetry stream from backend...</span>
    </div>
  `;
  try {
    const assets = await fetchFromBackend('/api/assets');
    state.assets = assets;
    renderAssets(assets);
    updateKPIs();
  } catch (err) {
    elements.assetsContainer.innerHTML = `
      <div class="loading-state">
        <span class="text-critical">⚠️ Failed to load assets. Verify backend server is active at ${API_BASE_URL}</span>
      </div>
    `;
  }
}

async function loadInventory() {
  try {
    const items = await fetchFromBackend('/api/inventory');
    state.inventory = items;
    renderInventory(items);
    updateKPIs();
  } catch (err) {
    elements.inventoryTbody.innerHTML = `<tr><td colspan="8" class="table-empty text-critical">Failed to load inventory.</td></tr>`;
  }
}

async function loadTechnicians() {
  try {
    const techs = await fetchFromBackend('/api/technicians');
    state.technicians = techs;
    renderTechnicians(techs);
    updateKPIs();
  } catch (err) {
    elements.techniciansContainer.innerHTML = `
      <div class="loading-state">
        <span class="text-critical">Failed to load technician roster.</span>
      </div>
    `;
  }
}

async function loadOperationLogs() {
  try {
    const logs = await fetchFromBackend('/api/operations/logs');
    state.logs = logs;
    renderLogs(logs);
  } catch (err) {
    elements.logsTbody.innerHTML = `<tr><td colspan="9" class="table-empty text-critical">Failed to load operation logs.</td></tr>`;
  }
}

function updateKPIs() {
  elements.valTotalAssets.textContent = state.assets.length || '0';
  const criticalCount = state.assets.filter(a => a.criticality === 'CRITICAL' || a.vibration_mm_s > 6.0).length;
  elements.valCriticalAssets.textContent = criticalCount;
  elements.valTotalInventory.textContent = state.inventory.length || '0';
  elements.valActiveTechs.textContent = state.technicians.filter(t => t.availability).length || '0';
}

// ---------------------------------------------------------
// 3. UI Renderers
// ---------------------------------------------------------
function renderAssets(assets) {
  if (!assets.length) {
    elements.assetsContainer.innerHTML = `<div class="loading-state"><span>No assets registered.</span></div>`;
    return;
  }

  elements.assetsContainer.innerHTML = assets.map(asset => {
    const isCrit = asset.criticality === 'CRITICAL' || asset.vibration_mm_s >= 6.5;
    const isWarn = !isCrit && (asset.criticality === 'HIGH' || asset.vibration_mm_s >= 4.0);
    const cardClass = isCrit ? 'critical' : (isWarn ? 'medium' : 'healthy');
    const critClass = asset.criticality.toLowerCase();

    return `
      <article class="asset-card ${cardClass}" id="card-${asset.asset_id}">
        <div>
          <div class="asset-header">
            <div>
              <span class="asset-id-badge">${escapeHtml(asset.asset_id)}</span>
              <h4 class="asset-name">${escapeHtml(asset.name)}</h4>
              <div class="asset-location">📍 ${escapeHtml(asset.location)} • ${escapeHtml(asset.asset_type)}</div>
            </div>
            <span class="crit-badge ${critClass}">${escapeHtml(asset.criticality)}</span>
          </div>

          <div class="telemetry-grid">
            <div class="telemetry-item">
              <span class="telem-label">Vibration</span>
              <span class="telem-val ${asset.vibration_mm_s >= 6.0 ? 'danger' : ''}">${asset.vibration_mm_s.toFixed(1)} mm/s</span>
            </div>
            <div class="telemetry-item">
              <span class="telem-label">Operating Temp</span>
              <span class="telem-val ${asset.operating_temp_c >= 80 ? 'danger' : ''}">${asset.operating_temp_c.toFixed(1)} °C</span>
            </div>
            <div class="telemetry-item">
              <span class="telem-label">Ambient Temp</span>
              <span class="telem-val">${asset.ambient_temp_c.toFixed(1)} °C</span>
            </div>
            <div class="telemetry-item">
              <span class="telem-label">Runtime / Age</span>
              <span class="telem-val">${asset.runtime_hours.toLocaleString()} hrs (${asset.last_maintenance_days}d ago)</span>
            </div>
          </div>

          <div class="asset-part-meta">
            Required Part: <strong>${escapeHtml(asset.required_spare_part_id)}</strong>
          </div>
        </div>

        <button 
          class="btn-trigger-ai" 
          id="btn-trigger-${asset.asset_id}"
          onclick="triggerAutonomousOperation('${asset.asset_id}')"
        >
          <span>⚡ Run Autonomous Operation</span>
        </button>
      </article>
    `;
  }).join('');
}

function renderInventory(items) {
  if (!items.length) {
    elements.inventoryTbody.innerHTML = `<tr><td colspan="8" class="table-empty">No inventory items found.</td></tr>`;
    return;
  }

  elements.inventoryTbody.innerHTML = items.map(item => {
    const isOut = item.current_stock <= 0;
    const isLow = !isOut && item.current_stock < item.min_safety_stock;
    const badge = isOut 
      ? '<span class="status-badge badge-critical">OUT OF STOCK</span>'
      : (isLow ? '<span class="status-badge" style="background:var(--color-warning-bg);color:var(--color-warning);">LOW</span>' : '<span class="status-badge badge-success">OPTIMAL</span>');

    return `
      <tr>
        <td><strong>${escapeHtml(item.part_id)}</strong></td>
        <td>${escapeHtml(item.part_name)}</td>
        <td>${escapeHtml(item.category)}</td>
        <td class="${isOut ? 'text-critical' : ''}"><strong>${item.current_stock}</strong></td>
        <td>${item.min_safety_stock}</td>
        <td>${item.unit_cost_aed.toFixed(2)} AED</td>
        <td>${item.lead_time_days} days</td>
        <td>${badge}</td>
      </tr>
    `;
  }).join('');
}

function renderTechnicians(techs) {
  if (!techs.length) {
    elements.techniciansContainer.innerHTML = `<div class="loading-state"><span>No technicians registered.</span></div>`;
    return;
  }

  elements.techniciansContainer.innerHTML = techs.map(tech => {
    const skillsHtml = (tech.skills || []).map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('');
    return `
      <div class="tech-card">
        <div class="tech-header">
          <span class="tech-name">${escapeHtml(tech.technician_id)}</span>
          <span class="status-badge ${tech.availability ? 'badge-success' : 'badge-critical'}">
            ${tech.availability ? 'AVAILABLE' : 'OFF SHIFT'}
          </span>
        </div>
        <div style="font-size:13px; color:var(--text-muted);">
          📍 Current Corridor: <strong>${escapeHtml(tech.current_location)}</strong> | Active Tasks: <strong>${tech.technician_workload}</strong>
        </div>
        <div class="tech-skills">${skillsHtml}</div>
      </div>
    `;
  }).join('');
}

function renderLogs(logs) {
  if (!logs.length) {
    elements.logsTbody.innerHTML = `<tr><td colspan="9" class="table-empty">No autonomous operations logged yet. Click "Run Autonomous Operation" on any asset above.</td></tr>`;
    return;
  }

  elements.logsTbody.innerHTML = logs.map(log => {
    return `
      <tr>
        <td><span class="log-pill">#${log.id}</span></td>
        <td style="color:var(--text-dim);font-size:12px;">${escapeHtml(log.executed_at || '-')}</td>
        <td><strong>${escapeHtml(log.asset_id)}</strong></td>
        <td class="${log.failure_probability > 0.5 ? 'text-critical' : ''}"><strong>${(log.failure_probability * 100).toFixed(1)}%</strong></td>
        <td>${log.risk_score.toFixed(1)}</td>
        <td><span class="status-badge ${log.unified_action.includes('URGENT') || log.unified_action.includes('ESCALATION') ? 'badge-critical' : 'badge-success'}">${escapeHtml(log.unified_action)}</span></td>
        <td>${escapeHtml(log.selected_technician)}</td>
        <td>${log.technician_eta_minutes.toFixed(1)} min</td>
        <td class="text-success"><strong>+${log.estimated_savings_aed.toFixed(2)} AED</strong></td>
      </tr>
    `;
  }).join('');
}

// ---------------------------------------------------------
// 4. Trigger Autonomous Operation Workflow
// ---------------------------------------------------------
window.triggerAutonomousOperation = async function(assetId) {
  const btn = document.getElementById(`btn-trigger-${assetId}`);
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div><span>Analyzing...</span>`;
  }

  try {
    const data = await fetchFromBackend(`/api/operations/trigger/${assetId}`, {
      method: 'POST',
    });

    displayDecisionModal(data);
    // Refresh background logs & assets
    loadOperationLogs();
  } catch (err) {
    alert(`Autonomous Operation Execution Error: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>⚡ Run Autonomous Operation</span>`;
    }
  }
};

// ---------------------------------------------------------
// 5. Modal Presentation of 13 Intelligence Outputs
// ---------------------------------------------------------
function displayDecisionModal(data) {
  const fail = data.failure_prediction || {};
  const inv = data.inventory_intelligence || {};
  const tech = data.technician_dispatch || {};
  const cost = data.cost_optimization || {};

  // Header & Summary
  elements.modalAssetTitle.textContent = data.asset_id;
  elements.modalActionBadge.textContent = data.unified_action || 'OPERATION_COMPLETE';
  if (data.unified_action === 'MONITOR' || data.unified_action === 'MAINTAIN_STANDARD_SCHEDULE') {
    elements.modalActionBadge.className = 'modal-badge-action success';
  } else {
    elements.modalActionBadge.className = 'modal-badge-action';
  }
  elements.modalSummaryText.textContent = data.operational_summary || 'Autonomous analysis concluded.';

  // 1. Failure Prediction & Health
  elements.resFailureProb.textContent = `${((fail.failure_probability || 0) * 100).toFixed(1)}%`;
  elements.resAssetRisk.textContent = fail.predicted_status || 'UNKNOWN';
  elements.resAssetRisk.className = `status-badge ${fail.predicted_status === 'CRITICAL' ? 'badge-critical' : 'badge-success'}`;
  elements.resRiskScore.textContent = `${(fail.risk_score || 0).toFixed(1)} / 100`;
  elements.resRulDays.textContent = `${(fail.estimated_rul_days || 0).toFixed(1)} Days`;

  // 2. Inventory & Stockout
  elements.resSparePart.textContent = inv.spare_part || 'N/A';
  elements.resCurrentStock.textContent = `${inv.current_stock || 0} Units`;
  elements.resStockoutRisk.textContent = inv.stockout_risk || 'UNKNOWN';
  const ropVal = (inv.reorder_point !== undefined && inv.reorder_point !== null)
    ? (Number(inv.reorder_point) % 1 !== 0 ? Number(inv.reorder_point).toFixed(2) : inv.reorder_point)
    : (data.inventory?.reorder_point || 0);
  elements.resReorderQty.textContent = `${inv.recommended_order_quantity || 0} Units (ROP: ${ropVal})`;

  // 3. Technician Dispatch & SLA
  elements.resSelectedTech.textContent = tech.selected_technician || 'None';
  elements.resTechScore.textContent = `${(tech.technician_score || 0).toFixed(1)} / 100`;
  elements.resTechEta.textContent = `${(tech.estimated_eta_minutes || 0).toFixed(1)} mins (${(tech.distance_km || 0).toFixed(1)} km)`;
  elements.resSlaStatus.textContent = tech.sla_status || 'UNKNOWN';
  elements.resSlaStatus.className = `status-badge ${tech.sla_status === 'WITHIN_SLA' ? 'badge-success' : 'badge-critical'}`;

  // 4. Financial Cost & Savings
  elements.resPreventiveCost.textContent = `${(cost.preventive_total_cost || 0).toFixed(2)} AED`;
  elements.resFailureCost.textContent = `${(cost.failure_total_cost || 0).toFixed(2)} AED`;
  elements.resNetSavings.textContent = `+${(cost.estimated_savings || 0).toFixed(2)} AED`;
  elements.resLogId.textContent = `#${data.log_id || 'N/A'}`;

  // Open Modal
  elements.decisionModal.classList.remove('hidden');
}

function closeModal() {
  elements.decisionModal.classList.add('hidden');
}

// ---------------------------------------------------------
// 6. Event Listeners & Tab Switching
// ---------------------------------------------------------
elements.tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const targetTab = btn.dataset.tab;
    elements.tabBtns.forEach(b => b.classList.remove('active'));
    elements.tabPanes.forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(targetTab)?.classList.add('active');
    state.activeTab = targetTab;

    if (targetTab === 'tab-inventory') loadInventory();
    if (targetTab === 'tab-technicians') loadTechnicians();
    if (targetTab === 'tab-logs') loadOperationLogs();
  });
});

elements.btnCloseModal.addEventListener('click', closeModal);
elements.btnModalDismiss.addEventListener('click', closeModal);
elements.decisionModal.addEventListener('click', (e) => {
  if (e.target === elements.decisionModal) closeModal();
});

elements.btnRefreshAssets.addEventListener('click', loadAssets);
elements.btnRefreshInventory.addEventListener('click', loadInventory);
elements.btnRefreshTechnicians.addEventListener('click', loadTechnicians);
elements.btnRefreshLogs.addEventListener('click', loadOperationLogs);
elements.btnRetryConnection.addEventListener('click', () => {
  clearError();
  loadAssets();
  loadInventory();
  loadTechnicians();
});

function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;',
  }[tag] || tag));
}

// ---------------------------------------------------------
// 7. App Initialization
// ---------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  loadAssets();
  loadInventory();
  loadTechnicians();
  loadOperationLogs();
});
