/**
 * Frontend Smoke Test Script
 * Verifies DOM contracts, required metric IDs, API endpoints, and static integrity.
 */

const fs = require('fs');
const path = require('path');

console.log('=== RUNNING FRONTEND SMOKE TESTS ===');

// 1. Check index.html existence and critical element IDs
const htmlPath = path.join(__dirname, 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf-8');

const requiredIds = [
  'backend-status-pill',
  'ai-status-pill',
  'assets-container',
  'inventory-tbody',
  'technicians-container',
  'logs-tbody',
  'decision-modal',
  // The 13 required AI decision outputs
  'res-failure-prob',
  'res-asset-risk',
  'res-rul-days',
  'res-spare-part',
  'res-current-stock',
  'res-stockout-risk',
  'res-reorder-qty',
  'res-selected-tech',
  'res-tech-score',
  'res-tech-eta',
  'res-sla-status',
  'res-preventive-cost',
  'res-failure-cost',
  'res-net-savings',
  'modal-summary-text',
  'modal-action-badge',
];

for (const id of requiredIds) {
  if (!htmlContent.includes(`id="${id}"`)) {
    console.error(`❌ Missing critical DOM ID: ${id}`);
    process.exit(1);
  }
}
console.log(`✅ All ${requiredIds.length} required DOM IDs and metric containers verified in index.html`);

// 2. Check app.js existence and endpoint calls
const jsPath = path.join(__dirname, 'app.js');
const jsContent = fs.readFileSync(jsPath, 'utf-8');

const requiredEndpoints = [
  '/api/assets',
  '/api/inventory',
  '/api/technicians',
  '/api/operations/trigger/',
  '/api/operations/logs',
];

for (const ep of requiredEndpoints) {
  if (!jsContent.includes(ep)) {
    console.error(`❌ Missing API integration endpoint in app.js: ${ep}`);
    process.exit(1);
  }
}
console.log(`✅ All ${requiredEndpoints.length} backend API endpoint paths verified in app.js`);

// 3. Check CSS existence
const cssPath = path.join(__dirname, 'index.css');
const cssContent = fs.readFileSync(cssPath, 'utf-8');
if (cssContent.length < 500) {
  console.error('❌ index.css seems incomplete');
  process.exit(1);
}
console.log(`✅ index.css verified (${cssContent.length} bytes)`);

console.log('=== ALL FRONTEND SMOKE TESTS PASSED ===');
