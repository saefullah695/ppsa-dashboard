class PPSADashboard {
    constructor() {
        this.data = null;
        this.processedData = null;
        this.apiBaseUrl = 'https://your-worker.your-subdomain.workers.dev/api';
        
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderDashboard();
        this.hideLoading();
    }

    async loadData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/data`);
            const result = await response.json();
            
            if (result.success) {
                this.data = result.data;
                this.processedData = this.processData(this.data);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Error loading data:', error);
            // Fallback to mock data
            this.data = this.generateMockData();
            this.processedData = this.processData(this.data);
        }
    }

    processData(rawData) {
        // Process data similar to Python version
        const processed = rawData.map(row => {
            const psmAcv = (row['PSM Actual'] / row['PSM Target']) * 100;
            const pwpAcv = (row['PWP Actual'] / row['PWP Target']) * 100;
            const sgAcv = (row['SG Actual'] / row['SG Target']) * 100;
            const apcAcv = (row['APC Actual'] / row['APC Target']) * 100;
            const tebusAcv = (row['ACTUAL TEBUS 2500'] / row['TARGET TEBUS 2500']) * 100;

            return {
                ...row,
                'PSM ACV': psmAcv,
                'PWP ACV': pwpAcv,
                'SG ACV': sgAcv,
                'APC ACV': apcAcv,
                'TEBUS ACV': tebusAcv,
                'SCORE PSM': (psmAcv * row['BOBOT PSM']) / 100,
                'SCORE PWP': (pwpAcv * row['BOBOT PWP']) / 100,
                'SCORE SG': (sgAcv * row['BOBOT SG']) / 100,
                'SCORE APC': (apcAcv * row['BOBOT APC']) / 100
            };
        });

        // Calculate total scores
        processed.forEach(row => {
            row['TOTAL SCORE PPSA'] = 
                row['SCORE PSM'] + row['SCORE PWP'] + 
                row['SCORE SG'] + row['SCORE APC'];
        });

        return processed;
    }

    calculateOverallMetrics() {
        if (!this.processedData) return null;

        const scores = {
            psm: 0, pwp: 0, sg: 0, apc: 0, total: 0
        };

        // Calculate average scores
        scores.psm = this.processedData.reduce((sum, row) => sum + row['SCORE PSM'], 0) / this.processedData.length;
        scores.pwp = this.processedData.reduce((sum, row) => sum + row['SCORE PWP'], 0) / this.processedData.length;
        scores.sg = this.processedData.reduce((sum, row) => sum + row['SCORE SG'], 0) / this.processedData.length;
        scores.apc = this.processedData.reduce((sum, row) => sum + row['SCORE APC'], 0) / this.processedData.length;
        scores.total = scores.psm + scores.pwp + scores.sg + scores.apc;

        return scores;
    }

    getTopPerformers() {
        if (!this.processedData) return [];

        const cashierScores = {};
        
        this.processedData.forEach(row => {
            const cashier = row['NAMA KASIR'];
            if (!cashierScores[cashier]) {
                cashierScores[cashier] = {
                    name: cashier,
                    totalScore: 0,
                    count: 0
                };
            }
            cashierScores[cashier].totalScore += row['TOTAL SCORE PPSA'];
            cashierScores[cashier].count++;
        });

        // Calculate averages and sort
        return Object.values(cashierScores)
            .map(cashier => ({
                ...cashier,
                averageScore: cashier.totalScore / cashier.count
            }))
            .sort((a, b) => b.averageScore - a.averageScore)
            .slice(0, 3);
    }

    renderDashboard() {
        this.renderKPIMetrics();
        this.renderCharts();
        this.renderTopPerformers();
    }

    renderKPIMetrics() {
        const metrics = this.calculateOverallMetrics();
        if (!metrics) return;

        document.getElementById('psm-score').textContent = metrics.psm.toFixed(1);
        document.getElementById('pwp-score').textContent = metrics.pwp.toFixed(1);
        document.getElementById('sg-score').textContent = metrics.sg.toFixed(1);
        document.getElementById('apc-score').textContent = metrics.apc.toFixed(1);
        document.getElementById('total-ppsa-score').textContent = metrics.total.toFixed(1);

        const gap = metrics.total - 100;
        const gapElement = document.getElementById('total-ppsa-gap');
        gapElement.textContent = `${gap >= 0 ? '+' : ''}${gap.toFixed(1)}`;
        gapElement.style.color = gap >= 0 ? '#90EE90' : '#FFB6C1';
    }

    renderCharts() {
        this.renderComponentChart();
        this.renderPerformanceChart();
    }

    renderComponentChart() {
        const metrics = this.calculateOverallMetrics();
        if (!metrics) return;

        const trace1 = {
            x: ['PSM', 'PWP', 'SG', 'APC'],
            y: [metrics.psm, metrics.pwp, metrics.sg, metrics.apc],
            name: 'Actual Score',
            type: 'bar',
            marker: {
                color: ['#667eea', '#764ba2', '#f093fb', '#4facfe']
            }
        };

        const trace2 = {
            x: ['PSM', 'PWP', 'SG', 'APC'],
            y: [20, 25, 30, 25],
            name: 'Target',
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: 'red',
                dash: 'dash',
                width: 3
            },
            marker: {
                size: 8,
                color: 'red'
            }
        };

        const layout = {
            title: 'Component vs Target Analysis',
            showlegend: true,
            height: 280,
            margin: { t: 40, r: 30, l: 40, b: 40 },
            font: { family: 'Inter' }
        };

        Plotly.newPlot('component-chart', [trace1, trace2], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    renderPerformanceChart() {
        if (!this.processedData) return;

        const scores = this.processedData.map(row => row['TOTAL SCORE PPSA']);
        
        const trace = {
            x: scores,
            type: 'histogram',
            marker: {
                color: 'rgba(102, 126, 234, 0.7)'
            },
            nbinsx: 15
        };

        const layout = {
            title: 'Performance Distribution',
            xaxis: { title: 'Total PPSA Score' },
            yaxis: { title: 'Frequency' },
            height: 280,
            margin: { t: 40, r: 30, l: 40, b: 40 },
            shapes: [{
                type: 'line',
                x0: 100,
                x1: 100,
                y0: 0,
                y1: 1,
                yref: 'paper',
                line: {
                    color: 'red',
                    width: 2,
                    dash: 'dash'
                }
            }],
            annotations: [{
                x: 100,
                y: 1,
                yref: 'paper',
                text: 'Target (100)',
                showarrow: false,
                bgcolor: 'red',
                bordercolor: 'red',
                font: { color: 'white' }
            }],
            font: { family: 'Inter' }
        };

        Plotly.newPlot('performance-chart', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    renderTopPerformers() {
        const topPerformers = this.getTopPerformers();
        const container = document.getElementById('top-performers');
        
        const medals = ['gold', 'silver', 'bronze'];
        const medalIcons = ['🥇', '🥈', '🥉'];
        
        container.innerHTML = topPerformers.map((performer, index) => `
            <div class="top-performer-card ${medals[index]}">
                <div class="top-performer-icon">${medalIcons[index]}</div>
                <div class="top-performer-name">${performer.name}</div>
                <div class="top-performer-score">${performer.averageScore.toFixed(1)}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">
                    Records: ${performer.count}
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Mobile navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });
    }

    switchTab(tabName) {
        // Update active nav button
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden');
    }

    generateMockData() {
        // Same as worker mock data for fallback
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
                SHIFT: shifts[Math.floor(Math.random() * shifts.length)],
                'NAMA KASIR': cashiers[Math.floor(Math.random() * cashiers.length)],
                'PSM Target': 100,
                'PSM Actual': 80 + Math.random() * 40,
                'BOBOT PSM': 20,
                'PWP Target': 100,
                'PWP Actual': 75 + Math.random() * 50,
                'BOBOT PWP': 25,
                'SG Target': 100,
                'SG Actual': 85 + Math.random() * 30,
                'BOBOT SG': 30,
                'APC Target': 100,
                'APC Actual': 90 + Math.random() * 20,
                'BOBOT APC': 25,
                'TARGET TEBUS 2500': 100,
                'ACTUAL TEBUS 2500': 70 + Math.random() * 60
            });
        }
        
        return data;
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PPSADashboard();
});

// Service Worker for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
