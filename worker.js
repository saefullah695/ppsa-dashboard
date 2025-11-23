import { GoogleSpreadsheet } from 'google-spreadsheet';

export default {
  async fetch(request, env, ctx) {
    // Handle CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    try {
      const url = new URL(request.url);
      
      if (url.pathname === '/api/data') {
        return await handleDataRequest(env);
      } else if (url.pathname === '/') {
        return await serveStaticFile('index.html');
      } else if (url.pathname === '/styles.css') {
        return await serveStaticFile('styles.css', 'text/css');
      } else if (url.pathname === '/app.js') {
        return await serveStaticFile('app.js', 'application/javascript');
      } else {
        return new Response('Not Found', { status: 404 });
      }
    } catch (error) {
      console.error('Error:', error);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
  },
};

async function serveStaticFile(filename, contentType = 'text/html') {
  let fileContent = '';
  
  if (filename === 'index.html') {
    fileContent = getHTMLTemplate();
  } else if (filename === 'styles.css') {
    fileContent = getCSSTemplate();
  } else if (filename === 'app.js') {
    fileContent = getJSTemplate();
  }
  
  return new Response(fileContent, {
    headers: {
      'Content-Type': contentType,
      'Cache-Control': 'public, max-age=3600',
    },
  });
}

async function handleDataRequest(env) {
  // In a real implementation, you would use proper authentication
  // For demo purposes, we'll return sample data structure
  
  const sampleData = generateSampleData();
  
  return new Response(JSON.stringify(sampleData), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-cache',
    },
  });
}

function generateSampleData() {
  // Generate realistic sample data matching your Streamlit structure
  const cashiers = ['Budi Santoso', 'Siti Rahayu', 'Ahmad Wijaya', 'Maya Sari', 'Rizki Pratama'];
  const shifts = ['Shift 1 (Pagi)', 'Shift 2 (Siang)', 'Shift 3 (Malam)'];
  const days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
  
  const data = [];
  const startDate = new Date('2024-01-01');
  
  for (let i = 0; i < 100; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    data.push({
      TANGGAL: date.toISOString().split('T')[0],
      HARI: days[date.getDay()],
      'NAMA KASIR': cashiers[Math.floor(Math.random() * cashiers.length)],
      SHIFT: shifts[Math.floor(Math.random() * shifts.length)],
      'PSM Target': 100,
      'PSM Actual': 85 + Math.random() * 30,
      'BOBOT PSM': 20,
      'PWP Target': 100,
      'PWP Actual': 80 + Math.random() * 40,
      'BOBOT PWP': 25,
      'SG Target': 100,
      'SG Actual': 90 + Math.random() * 20,
      'BOBOT SG': 30,
      'APC Target': 100,
      'APC Actual': 75 + Math.random() * 50,
      'BOBOT APC': 25,
      'TARGET TEBUS 2500': 100,
      'ACTUAL TEBUS 2500': 70 + Math.random() * 60,
    });
  }
  
  return data;
}

function getHTMLTemplate() {
  return `<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 PPSA Analytics Dashboard</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="dashboard-header">
            <h1 class="main-title">
                <svg class="header-icon" width="60" height="60" viewBox="0 0 24 24">
                    <path d="M3 13h2v8H3zm4-8h2v16H7zm4-2h2v18h-2zm4 4h2v14h-2zm4-2h2v16h-2z" fill="#667eea"/>
                </svg>
                PPSA Analytics Dashboard
            </h1>
            <div class="store-name">
                <svg class="store-icon" width="24" height="24" viewBox="0 0 24 24">
                    <path d="M12 2L2 7v2c0 1.1.9 2 2 2h2v9h2v-9h4v9h2v-9h2c1.1 0 2-.9 2-2V7l-10-5z" fill="#764ba2"/>
                </svg>
                2GC6 BAROS PANDEGLANG
            </div>
            <p class="subtitle">
                Platform <strong>analytics</strong> komprehensif untuk monitoring real-time 
                performa <strong>PPSA</strong> (PSM, PWP, SG, APC) dan <strong>Tebus Suuegerr</strong> 
                dengan insights AI-powered untuk optimasi performa tim.
            </p>
        </div>

        <!-- Loading Indicator -->
        <div id="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>Memuat data...</p>
        </div>

        <!-- Main Content -->
        <div id="content" class="content-hidden">
            <!-- Tabs Navigation -->
            <div class="tabs-container">
                <button class="tab-button active" data-tab="ppsa">📈 PPSA Analytics</button>
                <button class="tab-button" data-tab="tebus">🛒 Tebus Analytics</button>
                <button class="tab-button" data-tab="insights">🔍 Deep Insights</button>
                <button class="tab-button" data-tab="alerts">🎯 Performance Alerts</button>
                <button class="tab-button" data-tab="shift">🕐 Performance Shift</button>
                <button class="tab-button" data-tab="daily">📅 Performance Per Hari</button>
            </div>

            <!-- Tab Contents -->
            <div class="tab-content active" id="ppsa-tab">
                <!-- PPSA Analytics content will be populated by JavaScript -->
            </div>

            <div class="tab-content" id="tebus-tab">
                <!-- Tebus Analytics content will be populated by JavaScript -->
            </div>

            <div class="tab-content" id="insights-tab">
                <!-- Deep Insights content will be populated by JavaScript -->
            </div>

            <div class="tab-content" id="alerts-tab">
                <!-- Performance Alerts content will be populated by JavaScript -->
            </div>

            <div class="tab-content" id="shift-tab">
                <!-- Performance Shift content will be populated by JavaScript -->
            </div>

            <div class="tab-content" id="daily-tab">
                <!-- Performance Per Hari content will be populated by JavaScript -->
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <strong>🚀 PPSA Analytics Dashboard v2.0</strong> • 
            Powered by Cloudflare Workers & AI • © 2025<br>
            <small>Advanced Analytics • Real-time Monitoring • Performance Optimization</small>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>`;
}

function getCSSTemplate() {
  return `:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    --card-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    --card-shadow-hover: 0 20px 60px rgba(102, 126, 234, 0.25);
    --border-radius: 20px;
    --border-radius-sm: 12px;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
    min-height: 100vh;
    color: #333;
}

.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

/* DASHBOARD HEADER */
.dashboard-header {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
    backdrop-filter: blur(20px);
    padding: 2rem;
    border-radius: var(--border-radius);
    box-shadow: var(--card-shadow);
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    text-align: center;
    position: relative;
    overflow: hidden;
}

.dashboard-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: var(--primary-gradient);
}

.main-title {
    font-size: 2rem;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.store-name {
    font-size: 1.4rem;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.subtitle {
    color: #64748b;
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
}

/* LOADING */
.loading-container {
    text-align: center;
    padding: 3rem;
    color: white;
}

.loading-spinner {
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top: 4px solid white;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.content-hidden {
    display: none;
}

/* TABS */
.tabs-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 2rem;
    justify-content: center;
}

.tab-button {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.tab-button:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

.tab-button.active {
    background: var(--primary-gradient);
    border-color: transparent;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

/* CONTENT CONTAINERS */
.content-container {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
    backdrop-filter: blur(20px);
    padding: 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--card-shadow);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.section-header {
    font-size: 1.5rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 3px solid transparent;
    background: linear-gradient(90deg, #667eea, #764ba2) bottom / 100% 3px no-repeat;
    position: relative;
}

/* METRIC CARDS */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
    backdrop-filter: blur(20px);
    border-radius: var(--border-radius-sm);
    padding: 1.5rem;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(102, 126, 234, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--primary-gradient);
}

.metric-label {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}

/* SPECIAL CARDS */
.total-ppsa-card {
    background: var(--primary-gradient);
    border-radius: var(--border-radius);
    padding: 2rem;
    box-shadow: 0 25px 70px rgba(102, 126, 234, 0.4);
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    margin: 2rem auto;
    max-width: 500px;
}

.total-ppsa-label {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.95);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.total-ppsa-value {
    font-size: 3rem;
    font-weight: 900;
    color: #ffffff;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 1;
}

/* CHARTS */
.chart-container {
    background: white;
    border-radius: var(--border-radius-sm);
    padding: 1rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--card-shadow);
}

/* INSIGHTS CARDS */
.insight-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: var(--border-radius-sm);
    padding: 1.5rem;
    color: white;
    margin-bottom: 1rem;
    box-shadow: var(--card-shadow);
    transition: all 0.3s ease;
}

.insight-title {
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.insight-text {
    font-size: 0.95rem;
    opacity: 0.9;
    line-height: 1.5;
}

/* ALERT CARDS */
.alert-card {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    border-radius: var(--border-radius-sm);
    padding: 1.5rem;
    color: #1e293b;
    margin-bottom: 1rem;
    box-shadow: var(--card-shadow);
    border-left: 5px solid #ef4444;
}

.alert-title {
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* TOP PERFORMER CARDS */
.top-performers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.top-performer-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
    backdrop-filter: blur(20px);
    border-radius: var(--border-radius-sm);
    padding: 2rem 1.5rem;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(102, 126, 234, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    text-align: center;
}

.top-performer-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.75rem;
}

.top-performer-score {
    font-size: 2.2rem;
    font-weight: 800;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* DATA TABLE */
.data-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: var(--border-radius-sm);
    overflow: hidden;
    box-shadow: var(--card-shadow);
}

.data-table th,
.data-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

.data-table th {
    background: #f8fafc;
    font-weight: 600;
    color: #475569;
}

.data-table tr:hover {
    background: #f1f5f9;
}

/* FILTERS */
.filters-container {
    background: rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    border-radius: var(--border-radius-sm);
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.filter-group {
    margin-bottom: 1rem;
}

.filter-label {
    color: white;
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: block;
}

.filter-select {
    width: 100%;
    padding: 0.75rem;
    border-radius: var(--border-radius-sm);
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
    color: white;
    backdrop-filter: blur(10px);
}

.filter-select option {
    background: #667eea;
    color: white;
}

/* FOOTER */
.footer {
    text-align: center;
    color: rgba(255,255,255,0.8);
    padding: 2rem;
    font-size: 0.9rem;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(248,249,255,0.1) 100%);
    border-radius: 15px;
    margin-top: 2rem;
}

/* RESPONSIVE DESIGN */
@media (max-width: 768px) {
    .dashboard-container {
        padding: 0.5rem;
    }
    
    .dashboard-header {
        padding: 1.5rem;
    }
    
    .main-title {
        font-size: 1.5rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .store-name {
        font-size: 1.1rem;
    }
    
    .subtitle {
        font-size: 0.9rem;
    }
    
    .tabs-container {
        flex-direction: column;
    }
    
    .tab-button {
        text-align: center;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .content-container {
        padding: 1rem;
    }
    
    .section-header {
        font-size: 1.25rem;
    }
    
    .total-ppsa-card {
        padding: 1.5rem;
    }
    
    .total-ppsa-value {
        font-size: 2.5rem;
    }
}

@media (max-width: 480px) {
    .main-title {
        font-size: 1.25rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
    }
    
    .top-performers-grid {
        grid-template-columns: 1fr;
    }
}`;
}

function getJSTemplate() {
  return `// PPSA Dashboard JavaScript
class PPSADashboard {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.currentTab = 'ppsa';
        this.filters = {
            cashiers: [],
            dateRange: [],
            shifts: []
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadData();
        this.render();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Filter handlers would be added here in a real implementation
    }

    async loadData() {
        try {
            const response = await fetch('/api/data');
            this.data = await response.json();
            this.filteredData = [...this.data];
            this.processData();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Gagal memuat data. Silakan refresh halaman.');
        }
    }

    processData() {
        // Calculate derived metrics similar to Streamlit version
        this.calculateScores();
        this.calculateAggregates();
    }

    calculateScores() {
        this.data.forEach(row => {
            // Calculate ACV percentages
            row['(%) PSM ACV'] = this.calculateACV(row['PSM Actual'], row['PSM Target']);
            row['(%) PWP ACV'] = this.calculateACV(row['PWP Actual'], row['PWP Target']);
            row['(%) SG ACV'] = this.calculateACV(row['SG Actual'], row['SG Target']);
            row['(%) APC ACV'] = this.calculateACV(row['APC Actual'], row['APC Target']);
            row['(%) ACV TEBUS 2500'] = this.calculateACV(row['ACTUAL TEBUS 2500'], row['TARGET TEBUS 2500']);

            // Calculate weighted scores
            row['SCORE PSM'] = (row['(%) PSM ACV'] * row['BOBOT PSM']) / 100;
            row['SCORE PWP'] = (row['(%) PWP ACV'] * row['BOBOT PWP']) / 100;
            row['SCORE SG'] = (row['(%) SG ACV'] * row['BOBOT SG']) / 100;
            row['SCORE APC'] = (row['(%) APC ACV'] * row['BOBOT APC']) / 100;

            // Calculate total PPSA score
            row['TOTAL SCORE PPSA'] = row['SCORE PSM'] + row['SCORE PWP'] + row['SCORE SG'] + row['SCORE APC'];
        });
    }

    calculateACV(actual, target) {
        return target !== 0 ? (actual / target) * 100 : 0;
    }

    calculateAggregates() {
        // Calculate overall performance metrics
        this.overallScores = this.calculateOverallPPSABreakdown();
        this.cashierPerformance = this.calculateCashierPerformance();
        this.shiftPerformance = this.calculateShiftPerformance();
        this.dailyPerformance = this.calculateDailyPerformance();
    }

    calculateOverallPPSABreakdown() {
        const weights = { PSM: 20, PWP: 25, SG: 30, APC: 25 };
        const scores = { psm: 0, pwp: 0, sg: 0, apc: 0 };

        // PSM, PWP, SG - SUM aggregation
        ['PSM', 'PWP', 'SG'].forEach(comp => {
            const totalTarget = this.data.reduce((sum, row) => sum + row[\`\${comp} Target\`], 0);
            const totalActual = this.data.reduce((sum, row) => sum + row[\`\${comp} Actual\`], 0);
            if (totalTarget > 0) {
                const acv = (totalActual / totalTarget) * 100;
                scores[comp.toLowerCase()] = (acv * weights[comp]) / 100;
            }
        });

        // APC - AVERAGE aggregation
        const avgTargetAPC = this.data.reduce((sum, row) => sum + row['APC Target'], 0) / this.data.length;
        const avgActualAPC = this.data.reduce((sum, row) => sum + row['APC Actual'], 0) / this.data.length;
        if (avgTargetAPC > 0) {
            const acvAPC = (avgActualAPC / avgTargetAPC) * 100;
            scores.apc = (acvAPC * weights.APC) / 100;
        }

        scores.total = Object.values(scores).reduce((sum, score) => sum + score, 0);
        return scores;
    }

    calculateCashierPerformance() {
        const cashiers = [...new Set(this.data.map(row => row['NAMA KASIR']))];
        return cashiers.map(cashier => {
            const cashierData = this.data.filter(row => row['NAMA KASIR'] === cashier);
            const performance = {
                'NAMA KASIR': cashier,
                'TOTAL SCORE PPSA': cashierData.reduce((sum, row) => sum + row['TOTAL SCORE PPSA'], 0) / cashierData.length,
                'SCORE PSM': cashierData.reduce((sum, row) => sum + row['SCORE PSM'], 0) / cashierData.length,
                'SCORE PWP': cashierData.reduce((sum, row) => sum + row['SCORE PWP'], 0) / cashierData.length,
                'SCORE SG': cashierData.reduce((sum, row) => sum + row['SCORE SG'], 0) / cashierData.length,
                'SCORE APC': cashierData.reduce((sum, row) => sum + row['SCORE APC'], 0) / cashierData.length,
                'RECORD_COUNT': cashierData.length
            };
            return performance;
        }).sort((a, b) => b['TOTAL SCORE PPSA'] - a['TOTAL SCORE PPSA']);
    }

    calculateShiftPerformance() {
        const shifts = [...new Set(this.data.map(row => row.SHIFT))];
        return shifts.map(shift => {
            const shiftData = this.data.filter(row => row.SHIFT === shift);
            return {
                SHIFT: shift,
                'TOTAL SCORE PPSA': shiftData.reduce((sum, row) => sum + row['TOTAL SCORE PPSA'], 0) / shiftData.length,
                'RECORD_COUNT': shiftData.length
            };
        });
    }

    calculateDailyPerformance() {
        const days = [...new Set(this.data.map(row => row.HARI))];
        return days.map(day => {
            const dayData = this.data.filter(row => row.HARI === day);
            return {
                Day: day,
                'Avg Score': dayData.reduce((sum, row) => sum + row['TOTAL SCORE PPSA'], 0) / dayData.length,
                'Record Count': dayData.length
            };
        });
    }

    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.toggle('active', button.dataset.tab === tabName);
        });
        
        // Update tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === \`\${tabName}-tab\`);
        });
        
        this.renderCurrentTab();
    }

    render() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').classList.remove('content-hidden');
        this.renderCurrentTab();
    }

    renderCurrentTab() {
        switch (this.currentTab) {
            case 'ppsa':
                this.renderPPSATab();
                break;
            case 'tebus':
                this.renderTebusTab();
                break;
            case 'insights':
                this.renderInsightsTab();
                break;
            case 'alerts':
                this.renderAlertsTab();
                break;
            case 'shift':
                this.renderShiftTab();
                break;
            case 'daily':
                this.renderDailyTab();
                break;
        }
    }

    renderPPSATab() {
        const container = document.getElementById('ppsa-tab');
        container.innerHTML = \`
            <div class="content-container">
                <h2 class="section-header">📊 Performance Overview</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">PSM Score</div>
                        <div class="metric-value">\${this.overallScores.psm.toFixed(1)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">PWP Score</div>
                        <div class="metric-value">\${this.overallScores.pwp.toFixed(1)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">SG Score</div>
                        <div class="metric-value">\${this.overallScores.sg.toFixed(1)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">APC Score</div>
                        <div class="metric-value">\${this.overallScores.apc.toFixed(1)}</div>
                    </div>
                </div>

                <div class="total-ppsa-card">
                    <div class="total-ppsa-label">TOTAL PPSA SCORE</div>
                    <div class="total-ppsa-value">\${this.overallScores.total.toFixed(1)}</div>
                    <div style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;">
                        Gap: <span style="color: \${this.overallScores.total >= 100 ? '#90EE90' : '#FFB6C1'};">\${(this.overallScores.total - 100).toFixed(1)}</span>
                    </div>
                </div>
            </div>

            <div class="content-container">
                <h2 class="section-header">🏅 Top Performers</h2>
                <div class="top-performers-grid">
                    \${this.cashierPerformance.slice(0, 3).map((cashier, index) => \`
                        <div class="top-performer-card" style="border-top: 4px solid \${['#FFD700', '#C0C0C0', '#CD7F32'][index]}">
                            <div class="top-performer-name">\${cashier['NAMA KASIR']}</div>
                            <div class="top-performer-score">\${cashier['TOTAL SCORE PPSA'].toFixed(1)}</div>
                            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                                Records: \${cashier.RECORD_COUNT}
                            </div>
                        </div>
                    \`).join('')}
                </div>
            </div>

            <div class="content-container">
                <h2 class="section-header">📈 Performance Analytics</h2>
                <div class="chart-container">
                    <div id="component-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="distribution-chart"></div>
                </div>
            </div>

            <div class="content-container">
                <h2 class="section-header">🤖 AI-Powered Insights</h2>
                \${this.generateInsights().map(insight => \`
                    <div class="\${insight.type === 'alert' ? 'alert-card' : 'insight-card'}">
                        <div class="\${insight.type === 'alert' ? 'alert-title' : 'insight-title'}">
                            \${insight.title}
                        </div>
                        <div class="insight-text">
                            \${insight.text}
                        </div>
                    </div>
                \`).join('')}
            </div>
        \`;

        // Render charts
        this.renderComponentChart();
        this.renderDistributionChart();
    }

    renderTebusTab() {
        const container = document.getElementById('tebus-tab');
        const tebusData = this.calculateTebusPerformance();
        
        container.innerHTML = \`
            <div class="content-container">
                <h2 class="section-header">🛒 Tebus Performance Analytics</h2>
                
                <div class="total-ppsa-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="total-ppsa-label">TOTAL ACV TEBUS</div>
                    <div class="total-ppsa-value">\${tebusData.overallACV.toFixed(1)}%</div>
                    <div style="font-size: 1rem; margin-top: 1rem; opacity: 0.9;">
                        \${tebusData.totalActual.toLocaleString()} / \${tebusData.totalTarget.toLocaleString()}
                    </div>
                </div>

                <div class="top-performers-grid">
                    \${tebusData.topPerformers.slice(0, 3).map((performer, index) => \`
                        <div class="top-performer-card" style="border-top: 4px solid \${['#FFD700', '#C0C0C0', '#CD7F32'][index]}">
                            <div class="top-performer-name">\${performer.cashier}</div>
                            <div class="top-performer-score">\${performer.acv.toFixed(1)}%</div>
                            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                                Target: \${performer.target.toLocaleString()}
                            </div>
                        </div>
                    \`).join('')}
                </div>
            </div>

            <div class="content-container">
                <h2 class="section-header">📊 Tebus Performance Charts</h2>
                <div class="chart-container">
                    <div id="tebus-shift-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="tebus-daily-chart"></div>
                </div>
            </div>
        \`;

        this.renderTebusCharts(tebusData);
    }

    renderInsightsTab() {
        const container = document.getElementById('insights-tab');
        container.innerHTML = \`
            <div class="content-container">
                <h2 class="section-header">🔍 Advanced Analytics & Deep Insights</h2>
                <div class="chart-container">
                    <div id="correlation-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="trend-chart"></div>
                </div>
            </div>
        \`;

        this.renderInsightsCharts();
    }

    renderAlertsTab() {
        const container = document.getElementById('alerts-tab');
        const alerts = this.generateAlerts();
        
        container.innerHTML = \`
            <div class="content-container">
                <h2 class="section-header">🚨 Performance Alerts & Action Items</h2>
                \${alerts.map(alert => \`
                    <div class="\${alert.level === 'critical' ? 'alert-card' : 'insight-card'}">
                        <div class="\${alert.level === 'critical' ? 'alert-title' : 'insight-title'}">
                            \${alert.title}
                        </div>
                        <div class="insight-text">
                            \${alert.message}
                        </div>
                        <div style="margin-top: 0.5rem; font-weight: 600;">
                            💡 \${alert.action}
                        </div>
                    </div>
                \`).join('')}
            </div>
        \`;
    }

    renderShiftTab() {
        const container = document.getElementById('shift-tab');
        container.innerHTML = \`
            <div class="content-container">
                <h2 class="section-header">🕐 Performance Shift Analysis</h2>
                <div class="metrics-grid">
                    \${this.shiftPerformance.map(shift => \`
                        <div class="metric-card">
                            <div class="metric-label">\${shift.SHIFT}</div>
                            <div class="metric-value">\${shift['TOTAL SCORE PPSA'].toFixed(1)}</div>
                            <div style="font-size: 0.8rem; color: #64748b;">
                                Records: \${shift.RECORD_COUNT}
                            </div>
                        </div>
                    \`).join('')}
                </div>
                <div class="chart-container">
                    <div id="shift-comparison-chart"></div>
                </div>
            </div>
        \`;

        this.renderShiftChart();
    }

    renderDailyTab() {
        const container = document.getElementById('daily-tab');
        container.innerHTML = \`
            <div class="content-container">
                <h2 class="section-header">📅 Performance Per Hari Analysis</h2>
                <div class="chart-container">
                    <div id="daily-performance-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="day-of-week-chart"></div>
                </div>
            </div>
        \`;

        this.renderDailyCharts();
    }

    // Chart rendering methods
    renderComponentChart() {
        const data = [
            {
                x: ['PSM', 'PWP', 'SG', 'APC'],
                y: [this.overallScores.psm, this.overallScores.pwp, this.overallScores.sg, this.overallScores.apc],
                type: 'bar',
                name: 'Actual Score',
                marker: { color: ['#667eea', '#764ba2', '#f093fb', '#4facfe'] }
            },
            {
                x: ['PSM', 'PWP', 'SG', 'APC'],
                y: [20, 25, 30, 25],
                type: 'scatter',
                mode: 'markers+lines',
                name: 'Target',
                line: { dash: 'dash', color: 'red' },
                marker: { size: 10, symbol: 'diamond' }
            }
        ];

        const layout = {
            title: 'Component vs Target Analysis',
            yaxis: { title: 'Score' },
            showlegend: true,
            height: 350
        };

        Plotly.newPlot('component-chart', data, layout, { responsive: true });
    }

    renderDistributionChart() {
        const scores = this.cashierPerformance.map(c => c['TOTAL SCORE PPSA']);
        
        const data = [{
            x: scores,
            type: 'histogram',
            marker: { color: 'rgba(102, 126, 234, 0.7)' }
        }];

        const layout = {
            title: 'Performance Distribution',
            xaxis: { title: 'Total PPSA Score' },
            yaxis: { title: 'Frequency' },
            height: 350,
            shapes: [{
                type: 'line',
                x0: 100,
                x1: 100,
                y0: 0,
                y1: 1,
                yref: 'paper',
                line: { dash: 'dash', color: 'red' }
            }]
        };

        Plotly.newPlot('distribution-chart', data, layout, { responsive: true });
    }

    calculateTebusPerformance() {
        const totalTarget = this.data.reduce((sum, row) => sum + row['TARGET TEBUS 2500'], 0);
        const totalActual = this.data.reduce((sum, row) => sum + row['ACTUAL TEBUS 2500'], 0);
        const overallACV = totalTarget > 0 ? (totalActual / totalTarget) * 100 : 0;

        // Group by cashier
        const cashiers = [...new Set(this.data.map(row => row['NAMA KASIR']))];
        const topPerformers = cashiers.map(cashier => {
            const cashierData = this.data.filter(row => row['NAMA KASIR'] === cashier);
            const target = cashierData.reduce((sum, row) => sum + row['TARGET TEBUS 2500'], 0);
            const actual = cashierData.reduce((sum, row) => sum + row['ACTUAL TEBUS 2500'], 0);
            const acv = target > 0 ? (actual / target) * 100 : 0;
            
            return { cashier, target, actual, acv };
        }).sort((a, b) => b.acv - a.acv);

        return { overallACV, totalTarget, totalActual, topPerformers };
    }

    renderTebusCharts(tebusData) {
        // Tebus by Shift
        const shifts = [...new Set(this.data.map(row => row.SHIFT))];
        const shiftData = shifts.map(shift => {
            const shiftData = this.data.filter(row => row.SHIFT === shift);
            const target = shiftData.reduce((sum, row) => sum + row['TARGET TEBUS 2500'], 0);
            const actual = shiftData.reduce((sum, row) => sum + row['ACTUAL TEBUS 2500'], 0);
            return { shift, acv: target > 0 ? (actual / target) * 100 : 0 };
        });

        const shiftChartData = [{
            x: shiftData.map(d => d.shift),
            y: shiftData.map(d => d.acv),
            type: 'bar',
            marker: {
                color: shiftData.map(d => d.acv >= 100 ? '#10b981' : d.acv >= 80 ? '#f59e0b' : '#ef4444')
            }
        }];

        const shiftChartLayout = {
            title: 'Tebus Achievement by Shift',
            yaxis: { title: 'ACV Tebus (%)' },
            height: 350,
            shapes: [{
                type: 'line',
                y0: 100,
                y1: 100,
                x0: -0.5,
                x1: shifts.length - 0.5,
                line: { dash: 'dash', color: 'red' }
            }]
        };

        Plotly.newPlot('tebus-shift-chart', shiftChartData, shiftChartLayout, { responsive: true });
    }

    renderInsightsCharts() {
        // Correlation chart placeholder
        const correlationData = [{
            z: [[1, 0.8, 0.6, 0.7], [0.8, 1, 0.5, 0.6], [0.6, 0.5, 1, 0.8], [0.7, 0.6, 0.8, 1]],
            x: ['PSM', 'PWP', 'SG', 'APC'],
            y: ['PSM', 'PWP', 'SG', 'APC'],
            type: 'heatmap',
            colorscale: 'RdYlBu'
        }];

        const correlationLayout = {
            title: 'Component Correlation Matrix',
            height: 400
        };

        Plotly.newPlot('correlation-chart', correlationData, correlationLayout, { responsive: true });
    }

    renderShiftChart() {
        const data = [{
            x: this.shiftPerformance.map(s => s.SHIFT),
            y: this.shiftPerformance.map(s => s['TOTAL SCORE PPSA']),
            type: 'bar',
            marker: { color: ['#667eea', '#764ba2', '#f093fb'] }
        }];

        const layout = {
            title: 'Shift Performance Comparison',
            yaxis: { title: 'Average Score' },
            height: 350,
            shapes: [{
                type: 'line',
                y0: 100,
                y1: 100,
                x0: -0.5,
                x1: this.shiftPerformance.length - 0.5,
                line: { dash: 'dash', color: 'red' }
            }]
        };

        Plotly.newPlot('shift-comparison-chart', data, layout, { responsive: true });
    }

    renderDailyCharts() {
        // Daily performance trend
        const dailyData = this.data.reduce((acc, row) => {
            const date = row.TANGGAL;
            if (!acc[date]) {
                acc[date] = { total: 0, count: 0 };
            }
            acc[date].total += row['TOTAL SCORE PPSA'];
            acc[date].count++;
            return acc;
        }, {});

        const dates = Object.keys(dailyData).sort();
        const avgScores = dates.map(date => dailyData[date].total / dailyData[date].count);

        const trendData = [{
            x: dates,
            y: avgScores,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Daily Average',
            line: { color: '#667eea', width: 3 }
        }];

        const trendLayout = {
            title: 'Daily Performance Trend',
            yaxis: { title: 'Average Score' },
            height: 350,
            shapes: [{
                type: 'line',
                y0: 100,
                y1: 100,
                x0: dates[0],
                x1: dates[dates.length - 1],
                line: { dash: 'dash', color: 'red' }
            }]
        };

        Plotly.newPlot('daily-performance-chart', trendData, trendLayout, { responsive: true });

        // Day of week chart
        const dayData = [{
            x: this.dailyPerformance.map(d => d.Day),
            y: this.dailyPerformance.map(d => d['Avg Score']),
            type: 'bar',
            marker: { color: '#764ba2' }
        }];

        const dayLayout = {
            title: 'Performance by Day of Week',
            yaxis: { title: 'Average Score' },
            height: 350
        };

        Plotly.newPlot('day-of-week-chart', dayData, dayLayout, { responsive: true });
    }

    generateInsights() {
        const insights = [];
        const totalScore = this.overallScores.total;

        if (totalScore >= 100) {
            insights.push({
                type: 'success',
                title: '🎉 Target Tercapai!',
                text: \`Total PPSA Score \${totalScore.toFixed(1)} telah melampaui target 100.\`
            });
        } else {
            insights.push({
                type: 'warning',
                title: '⚠️ Gap Performa',
                text: \`Masih kurang \${(100 - totalScore).toFixed(1)} poin untuk mencapai target.\`
            });
        }

        // Component analysis
        const components = [
            { name: 'PSM', score: this.overallScores.psm, target: 20 },
            { name: 'PWP', score: this.overallScores.pwp, target: 25 },
            { name: 'SG', score: this.overallScores.sg, target: 30 },
            { name: 'APC', score: this.overallScores.apc, target: 25 }
        ];

        const bestComponent = components.reduce((best, current) => 
            (current.score / current.target) > (best.score / best.target) ? current : best
        );

        insights.push({
            type: 'info',
            title: \`🏆 Komponen Terbaik: \${bestComponent.name}\`,
            text: \`Achievement \${((bestComponent.score / bestComponent.target) * 100).toFixed(1)}% dari target.\`
        });

        return insights;
    }

    generateAlerts() {
        const alerts = [];
        const lowPerformers = this.cashierPerformance.filter(c => c['TOTAL SCORE PPSA'] < 80);

        if (lowPerformers.length > 0) {
            alerts.push({
                level: 'critical',
                title: '🚨 Critical Performance Alert',
                message: \`\${lowPerformers.length} kasir dengan performa < 80 poin\`,
                action: 'Immediate coaching dan performance improvement plan diperlukan'
            });
        }

        if (this.overallScores.total < 100) {
            alerts.push({
                level: 'warning',
                title: '⚠️ Overall Performance Alert',
                message: \`Total score \${this.overallScores.total.toFixed(1)} di bawah target 100\`,
                action: 'Focus pada komponen dengan gap terbesar'
            });
        }

        if (alerts.length === 0) {
            alerts.push({
                level: 'info',
                title: '✅ No Critical Alerts',
                message: 'Semua sistem beroperasi dalam parameter normal',
                action: 'Pertahankan performa yang baik'
            });
        }

        return alerts;
    }

    showError(message) {
        const container = document.getElementById('content');
        container.innerHTML = \`
            <div class="content-container" style="text-align: center; color: #ef4444;">
                <h2>❌ Error</h2>
                <p>\${message}</p>
                <button onclick="location.reload()" style="
                    background: var(--primary-gradient);
                    color: white;
                    border: none;
                    padding: 0.75rem 2rem;
                    border-radius: var(--border-radius-sm);
                    font-weight: 600;
                    cursor: pointer;
                    margin-top: 1rem;
                ">Refresh Halaman</button>
            </div>
        \`;
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PPSADashboard();
});`;
}
