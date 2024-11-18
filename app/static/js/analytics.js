const AnalyticsCharts = {
    initialize: function() {
        console.log('Initializing AnalyticsCharts...');
        this.createAllCharts();
        this.setupAutoRefresh();
        this.loadInitialData();
    },
    
    loadInitialData: function() {
        $.get('/api/analytics/data')
            .done(data => {
                console.log('Received analytics data:', data);
                this.updateAllCharts(data);
            })
            .fail(error => {
                console.error('Failed to fetch initial analytics data:', error);
            });
    },
    
    createAllCharts: function() {
        // Transaction Volume Timeline
        const volumeLayout = {
            title: 'Transaction Volume by Hour',
            xaxis: { title: 'Hour of Day' },
            yaxis: { title: 'Number of Transactions' },
            height: 400
        };
        
        ChartManager.createChart('volumeTimeline', {
            data: [{
                x: [],
                y: [],
                type: 'bar'
            }],
            layout: volumeLayout
        });

        // Risk Distribution
        const riskLayout = {
            title: 'Risk Level Distribution',
            height: 400
        };
        
        ChartManager.createChart('riskDistribution', {
            data: [{
                values: [],
                labels: [],
                type: 'pie'
            }],
            layout: riskLayout
        });

        // Amount Distribution
        const amountLayout = {
            title: 'Transaction Amount Distribution',
            xaxis: { title: 'Amount ($)' },
            yaxis: { title: 'Count' },
            height: 400
        };
        
        ChartManager.createChart('amountHistogram', {
            data: [{
                x: [],
                y: [],
                type: 'histogram',
                nbinsx: 30
            }],
            layout: amountLayout
        });

        // Fraud Patterns
        const fraudLayout = {
            title: 'Fraud by Pattern Type',
            height: 400
        };
        
        ChartManager.createChart('fraudPatterns', {
            data: [{
                values: [],
                labels: [],
                type: 'pie'
            }],
            layout: fraudLayout
        });
    },
    
    updateAllCharts: function(data) {
        // Update volume timeline
        const hours = Object.keys(data.hourly_transactions);
        const counts = Object.values(data.hourly_transactions);
        
        ChartManager.updateChart('volumeTimeline', {
            x: [hours],
            y: [counts]
        });

        // Update risk distribution
        const riskLabels = Object.keys(data.risk_distribution);
        const riskValues = Object.values(data.risk_distribution);
        
        ChartManager.updateChart('riskDistribution', {
            values: [riskValues],
            labels: [riskLabels]
        });

        // Update amount distribution
        if (data.risk_by_amount && data.risk_by_amount.length > 0) {
            const amounts = data.risk_by_amount.map(item => item[0]);
            
            ChartManager.updateChart('amountHistogram', {
                x: [amounts]
            });
        }

        // Update fraud patterns
        const fraudLabels = Object.keys(data.fraud_by_type);
        const fraudValues = Object.values(data.fraud_by_type);
        
        ChartManager.updateChart('fraudPatterns', {
            values: [fraudValues],
            labels: [fraudLabels]
        });
    },
    
    setupAutoRefresh: function() {
        // Refresh every 30 seconds
        setInterval(() => {
            $.get('/api/analytics/data')
                .done(data => this.updateAllCharts(data))
                .fail(error => console.error('Failed to fetch analytics data:', error));
        }, 30000);

        // Also update when new transactions come in
        $(document).on('transactionGenerated', (event, transaction) => {
            this.loadInitialData();
        });
    }
};

// Initialize when document is ready
$(document).ready(function() {
    AnalyticsCharts.initialize();
});