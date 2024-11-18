const Dashboard = {
    historicalData: [],
    currentPage: 1,
    pageSize: 10,
    
    initialize: function() {
        this.setupEventListeners();
        this.createCharts();
        this.loadInitialData();
        this.setupAutoRefresh();
        
        // Check simulation status
        if (localStorage.getItem('simulationRunning') === 'true') {
            this.startSimulation();
        }
    },

    setupEventListeners: function() {
        // Simulation controls
        $('#simulationControl').click(() => this.toggleSimulation());
        $('#resetSimulation').click(() => this.resetSimulation());

        // Chart controls
        $('#timeRangeSelect').change(() => this.updateRealtimeChart());
        $('#toggleRiskView').click(() => this.toggleRiskChartView());
        $('#refreshAlerts').click(() => this.loadRecentAlerts());

        // Pagination
        $('#prevPage').click(() => this.changePage(-1));
        $('#nextPage').click(() => this.changePage(1));

        // Listen for new transactions
        $(document).on('transactionGenerated', (event, transaction) => {
            this.handleNewTransaction(transaction);
        });
    },

    createCharts: function() {
        // Realtime transaction flow chart
        ChartManager.createChart('realtimeChart', {
            data: [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Transaction Amount'
            }, {
                x: [],
                y: [],
                type: 'scatter',
                mode: 'markers',
                name: 'Flagged Transactions',
                marker: {
                    color: 'red',
                    size: 10
                }
            }],
            layout: {
                title: 'Transaction Flow',
                height: 300,
                margin: { t: 30, r: 30, b: 40, l: 50 },
                showlegend: true,
                xaxis: { title: 'Time' },
                yaxis: { title: 'Amount ($)' }
            }
        });

        // Risk distribution chart
        ChartManager.createChart('riskDistributionChart', {
            data: [{
                values: [],
                labels: [],
                type: 'pie',
                hole: 0.4,
                marker: {
                    colors: ['#4CAF50', '#FFC107', '#F44336']
                }
            }],
            layout: {
                height: 300,
                margin: { t: 30, r: 30, b: 30, l: 30 },
                showlegend: true
            }
        });

        // Amount vs Risk scatter plot
        ChartManager.createChart('amountRiskChart', {
            data: [{
                x: [],
                y: [],
                mode: 'markers',
                type: 'scatter',
                marker: {
                    color: [],
                    colorscale: 'Viridis',
                    showscale: true
                }
            }],
            layout: {
                height: 300,
                margin: { t: 30, r: 30, b: 40, l: 50 },
                xaxis: { title: 'Amount ($)' },
                yaxis: { title: 'Risk Score' }
            }
        });
    },

    loadInitialData: function() {
        Promise.all([
            $.get('/api/transactions/latest'),
            $.get('/api/metrics'),
            $.get('/api/analytics/data')
        ]).then(([transactions, metrics, analytics]) => {
            this.historicalData = transactions.transactions || [];
            this.updateMetrics(metrics);
            this.updateCharts(analytics);
            this.updateTransactionTable();
            this.loadRecentAlerts();
        }).catch(error => {
            console.error('Error loading initial data:', error);
        });
    },

    updateMetrics: function(metrics) {
        // Update metric values with animations
        this.animateValue('totalTransactions', metrics.total_transactions);
        this.animateValue('flaggedTransactions', metrics.flagged_transactions);
        this.animateValue('fraudRate', metrics.fraud_rate, '%');
        this.animateValue('averageAmount', metrics.average_amount, '$');

        // Update trends
        this.updateTrends(metrics);
    },

    animateValue: function(elementId, newValue, suffix = '') {
        const element = $(`#${elementId}`);
        const startValue = parseFloat(element.text().replace(/[^0-9.-]+/g, '')) || 0;
        const duration = 1000;
        const steps = 20;
        const increment = (newValue - startValue) / steps;
        let currentStep = 0;

        const timer = setInterval(() => {
            currentStep++;
            const currentValue = startValue + (increment * currentStep);
            element.text(this.formatValue(currentValue, suffix));

            if (currentStep >= steps) {
                clearInterval(timer);
                element.text(this.formatValue(newValue, suffix));
            }
        }, duration / steps);
    },

    formatValue: function(value, suffix) {
        if (suffix === '$') {
            return `$${value.toFixed(2)}`;
        } else if (suffix === '%') {
            return `${value.toFixed(2)}%`;
        }
        return Math.round(value).toString();
    },

    updateTrends: function(metrics) {
        // Calculate and display trends based on historical data
        // This would compare current values with previous period
        const trends = this.calculateTrends(metrics);
        
        Object.entries(trends).forEach(([metric, trend]) => {
            const element = $(`#${metric}Trend`);
            element.html(this.getTrendHTML(trend));
        });
    },

    calculateTrends: function(currentMetrics) {
        // Compare with historical values to determine trends
        // This is a simplified example
        return {
            transactions: currentMetrics.total_transactions > this.lastMetrics?.total_transactions,
            flagged: currentMetrics.flagged_transactions > this.lastMetrics?.flagged_transactions,
            fraudRate: currentMetrics.fraud_rate > this.lastMetrics?.fraud_rate,
            amount: currentMetrics.average_amount > this.lastMetrics?.average_amount
        };
    },

    getTrendHTML: function(trend) {
        if (trend === true) {
            return '<span class="trend-up">↑</span>';
        } else if (trend === false) {
            return '<span class="trend-down">↓</span>';
        }
        return '<span class="trend-neutral">→</span>';
    },

    updateCharts: function(data) {
        // Update realtime chart
        const timeRange = $('#timeRangeSelect').val();
        const filteredData = this.filterDataByTimeRange(this.historicalData, timeRange);
        
        ChartManager.updateChart('realtimeChart', {
            x: [filteredData.map(t => new Date(t.timestamp))],
            y: [filteredData.map(t => t.Amount)]
        });

        // Update risk distribution
        const riskData = data.risk_distribution;
        ChartManager.updateChart('riskDistributionChart', {
            values: [Object.values(riskData)],
            labels: [Object.keys(riskData)]
        });

        // Update amount vs risk scatter plot
        ChartManager.updateChart('amountRiskChart', {
            x: [data.risk_by_amount.map(d => d[0])],
            y: [data.risk_by_amount.map(d => d[1])],
            'marker.color': [data.risk_by_amount.map(d => d[1])]
        });
    },

    filterDataByTimeRange: function(data, timeRange) {
        const now = new Date();
        const cutoff = new Date();
        
        switch(timeRange) {
            case '1h':
                cutoff.setHours(now.getHours() - 1);
                break;
            case '6h':
                cutoff.setHours(now.getHours() - 6);
                break;
            case '24h':
                cutoff.setHours(now.getHours() - 24);
                break;
        }
        
        return data.filter(t => new Date(t.timestamp) > cutoff);
    },

    updateTransactionTable: function() {
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const pageData = this.historicalData.slice(startIndex, startIndex + this.pageSize);
        
        const tableHTML = `
            <table class="transactions-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Amount</th>
                        <th>Risk Level</th>
                        <th>Location</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${pageData.map(t => `
                        <tr class="${this.getRowClass(t)}">
                            <td>${new Date(t.timestamp).toLocaleString()}</td>
                            <td>$${t.Amount.toFixed(2)}</td>
                            <td>${this.formatRiskLevel(t)}</td>
                            <td>${t.location}</td>
                            <td>${this.getStatusBadge(t)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        $('#transactionsTable').html(tableHTML);
        this.updatePagination();
    },

    getRowClass: function(transaction) {
        if (transaction.final_decision === 'flagged') return 'flagged-row';
        return transaction.risk_level === 'high' ? 'high-risk-row' : '';
    },

    formatRiskLevel: function(transaction) {
        return `
            <div class="risk-indicator ${transaction.risk_level}-risk">
                ${transaction.risk_level.charAt(0).toUpperCase() + transaction.risk_level.slice(1)}
            </div>
        `;
    },

    getStatusBadge: function(transaction) {
        const status = transaction.final_decision || 'pending';
        return `<span class="status-badge ${status}">${status}</span>`;
    },

    updatePagination: function() {
        const totalPages = Math.ceil(this.historicalData.length / this.pageSize);
        $('#pageInfo').text(`Page ${this.currentPage} of ${totalPages}`);
        $('#prevPage').prop('disabled', this.currentPage === 1);
        $('#nextPage').prop('disabled', this.currentPage === totalPages);
    },

    changePage: function(delta) {
        const newPage = this.currentPage + delta;
        const totalPages = Math.ceil(this.historicalData.length / this.pageSize);
        
        if (newPage >= 1 && newPage <= totalPages) {
            this.currentPage = newPage;
            this.updateTransactionTable();
        }
    },

    loadRecentAlerts: function() {
        const alerts = this.historicalData
            .filter(t => t.final_decision === 'flagged')
            .slice(-5);

        const alertsHTML = alerts.map(alert => `
            <div class="alert-item ${alert.risk_level}-risk">
                <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
                <div class="alert-content">
                   <div class="alert-amount">$${alert.Amount.toFixed(2)}</div>
                    <div class="alert-details">
                        <span class="alert-location">${alert.location}</span>
                        <span class="alert-risk">${alert.risk_level} risk</span>
                    </div>
                    <div class="alert-flags">
                        ${this.formatAlertFlags(alert.flags)}
                    </div>
                </div>
            </div>
        `).join('');

        $('#recentAlerts').html(alertsHTML || '<div class="no-alerts">No recent alerts</div>');
    },

    formatAlertFlags: function(flags) {
        if (!flags || !flags.length) return '';
        return flags.map(flag => `
            <span class="alert-flag" title="${flag.description}">
                ${flag.name}
            </span>
        `).join('');
    },

    handleNewTransaction: function(transaction) {
        // Add to historical data
        this.historicalData.push(transaction);
        if (this.historicalData.length > 1000) {
            this.historicalData.shift(); // Keep last 1000 transactions
        }

        // Update UI
        this.updateRealtimeChart(transaction);
        this.updateTransactionTable();
        
        // Update alerts if needed
        if (transaction.final_decision === 'flagged') {
            this.loadRecentAlerts();
        }

        // Fetch and update metrics
        $.get('/api/metrics')
            .done(metrics => this.updateMetrics(metrics))
            .fail(error => console.error('Failed to fetch metrics:', error));
    },

    updateRealtimeChart: function(newTransaction) {
        const timeRange = $('#timeRangeSelect').val();
        const filteredData = this.filterDataByTimeRange(this.historicalData, timeRange);
        
        const times = filteredData.map(t => new Date(t.timestamp));
        const amounts = filteredData.map(t => t.Amount);
        const flagged = filteredData.filter(t => t.final_decision === 'flagged');
        
        ChartManager.updateChart('realtimeChart', {
            x: [times, flagged.map(t => new Date(t.timestamp))],
            y: [amounts, flagged.map(t => t.Amount)]
        });
    },

    toggleSimulation: function() {
        if (SimulationState.isRunning) {
            this.stopSimulation();
        } else {
            this.startSimulation();
        }
    },

    startSimulation: function() {
        SimulationState.startSimulation();
        $('#simulationControl').text('Stop Simulation')
            .removeClass('primary')
            .addClass('danger');
        $('#statusText').text('Running')
            .addClass('status-running');
    },

    stopSimulation: function() {
        SimulationState.stopSimulation();
        $('#simulationControl').text('Start Simulation')
            .removeClass('danger')
            .addClass('primary');
        $('#statusText').text('Stopped')
            .removeClass('status-running');
    },

    resetSimulation: function() {
        this.stopSimulation();
        
        $.post('/api/reset')
            .done(response => {
                if (response.status === 'success') {
                    this.historicalData = [];
                    this.currentPage = 1;
                    this.createCharts();
                    this.loadInitialData();
                    this.showNotification('Simulation reset successful', 'success');
                } else {
                    this.showNotification('Failed to reset simulation', 'error');
                }
            })
            .fail(error => {
                console.error('Reset failed:', error);
                this.showNotification('Failed to reset simulation', 'error');
            });
    },

    showNotification: function(message, type = 'info') {
        const notification = $(`
            <div class="notification ${type}">
                ${message}
                <button class="close-notification">&times;</button>
            </div>
        `);
        
        $('body').append(notification);
        setTimeout(() => notification.remove(), 5000);
        
        notification.find('.close-notification').on('click', () => {
            notification.remove();
        });
    },

    setupAutoRefresh: function() {
        // Refresh data every 30 seconds
        setInterval(() => {
            if (!SimulationState.isRunning) return;
            
            Promise.all([
                $.get('/api/transactions/latest'),
                $.get('/api/metrics'),
                $.get('/api/analytics/data')
            ]).then(([transactions, metrics, analytics]) => {
                this.historicalData = transactions.transactions || [];
                this.updateMetrics(metrics);
                this.updateCharts(analytics);
                this.updateTransactionTable();
            }).catch(error => {
                console.error('Auto-refresh failed:', error);
            });
        }, 30000);
    }
};

// Initialize when document is ready
$(document).ready(function() {
    console.log('Initializing Dashboard...');
    Dashboard.initialize();
});