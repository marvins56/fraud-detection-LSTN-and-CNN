// static/js/analytics.js
const AnalyticsCharts = {
    initialize: function() {
        this.createAllCharts();
        this.setupAutoRefresh();
    },
    
    createAllCharts: function() {
        // Transaction Volume Timeline
        ChartManager.createChart('volumeTimeline', {
            data: [{
                type: 'scatter',
                mode: 'lines+markers'
            }],
            layout: {
                title: 'Transaction Volume Over Time',
                height: 400
            }
        });
        
        // Risk Distribution Heatmap
        ChartManager.createChart('riskHeatmap', {
            data: [{
                type: 'heatmap',
                colorscale: 'Viridis'
            }],
            layout: {
                title: 'Risk Distribution by Hour and Day',
                height: 400
            }
        });
        
        // Amount Distribution Histogram
        ChartManager.createChart('amountHistogram', {
            data: [{
                type: 'histogram',
                nbinsx: 30
            }],
            layout: {
                title: 'Transaction Amount Distribution',
                height: 400
            }
        });
        
        // Fraud Patterns Parallel Coordinates
        ChartManager.createChart('fraudPatterns', {
            data: [{
                type: 'parcoords',
                line: {
                    color: 'blue'
                }
            }],
            layout: {
                title: 'Fraud Pattern Analysis',
                height: 500
            }
        });
    },
    
    setupAutoRefresh: function() {
        setInterval(() => this.refreshData(), 30000);
    },
    
    refreshData: function() {
        $.get('/api/analytics/data')
            .done(data => this.updateAllCharts(data))
            .fail(error => console.error('Failed to fetch analytics data:', error));
    }
};