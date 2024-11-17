// static/js/dashboard.js
const Dashboard = {
    simulationInterval: null,
    isSimulating: false,

    initialize: function() {
        this.setupEventListeners();
        this.updateDashboard(); // Initial update
        Charts.initializeCharts();
    },

    setupEventListeners: function() {
        // Simulation control button
        $('#simulationControl').click(() => this.toggleSimulation());
        
        // Reset button
        $('#resetSimulation').click(() => this.resetSimulation());
    },

    toggleSimulation: function() {
        if (this.isSimulating) {
            this.stopSimulation();
        } else {
            this.startSimulation();
        }
    },

    startSimulation: function() {
        console.log('Starting simulation...');
        this.isSimulating = true;
        $('#simulationControl').text('Stop Simulation');
        $('#statusText').text('Running').addClass('status-running');
        
        // Start periodic simulation
        this.simulationInterval = setInterval(() => {
            this.generateTransaction();
        }, 1000); // Generate a transaction every second
    },

    stopSimulation: function() {
        console.log('Stopping simulation...');
        this.isSimulating = false;
        $('#simulationControl').text('Start Simulation');
        $('#statusText').text('Stopped').removeClass('status-running');
        
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.simulationInterval = null;
        }
    },

    resetSimulation: function() {
        console.log('Resetting simulation...');
        this.stopSimulation();
        
        $.ajax({
            url: '/api/reset',
            method: 'POST',
            success: (response) => {
                if (response.status === 'success') {
                    console.log('Reset successful');
                    this.updateDashboard();
                    Charts.initializeCharts();
                } else {
                    console.error('Reset failed:', response.message);
                }
            },
            error: (xhr, status, error) => {
                console.error('Reset error:', error);
            }
        });
    },

    generateTransaction: function() {
        $.ajax({
            url: '/api/simulate',
            method: 'POST',
            success: (response) => {
                if (response.status === 'success') {
                    console.log('Transaction generated:', response.transaction);
                    this.updateDashboard();
                } else {
                    console.error('Transaction generation failed:', response.message);
                }
            },
            error: (xhr, status, error) => {
                console.error('Transaction generation error:', error);
            }
        });
    },

    updateDashboard: function() {
        // Update metrics
        $.ajax({
            url: '/api/metrics',
            method: 'GET',
            success: (metrics) => {
                $('#totalTransactions').text(metrics.total_transactions);
                $('#flaggedTransactions').text(metrics.flagged_transactions);
                $('#fraudRate').text(metrics.fraud_rate.toFixed(2) + '%');
                $('#averageAmount').text('$' + metrics.average_amount.toFixed(2));
            },
            error: (xhr, status, error) => {
                console.error('Metrics update error:', error);
            }
        });

        // Update transactions and charts
        $.ajax({
            url: '/api/transactions/latest',
            method: 'GET',
            success: (data) => {
                if (data.transactions) {
                    TransactionTable.updateTable(data.transactions);
                    Charts.updateCharts(data.transactions);
                }
            },
            error: (xhr, status, error) => {
                console.error('Transaction update error:', error);
            }
        });
    }
};

// Initialize when document is ready
$(document).ready(function() {
    console.log('Initializing Dashboard...');
    Dashboard.initialize();
});