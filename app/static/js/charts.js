// static/js/charts.js
const Charts = {
    transactionChart: null,
    riskChart: null,

    initializeCharts: function() {
        console.log('Initializing charts...');
        this.initTransactionChart();
        this.initRiskChart();
    },

    initTransactionChart: function() {
        const layout = {
            title: 'Transactions Over Time',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Amount ($)' },
            height: 400
        };

        Plotly.newPlot('transactionChart', [{
            x: [],
            y: [],
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 10,
                color: [],
                colorscale: 'Viridis',
                showscale: true
            }
        }], layout);
    },

    initRiskChart: function() {
        const layout = {
            title: 'Risk Distribution',
            height: 400
        };

        Plotly.newPlot('riskDistribution', [{
            values: [0, 0, 0],
            labels: ['Low', 'Medium', 'High'],
            type: 'pie'
        }], layout);
    },

    updateCharts: function(transactions) {
        if (!transactions || transactions.length === 0) return;

        // Update transaction chart
        const times = transactions.map(t => new Date(t.timestamp));
        const amounts = transactions.map(t => t.Amount);
        const risks = transactions.map(t => t.fraud_probability);

        Plotly.update('transactionChart', {
            x: [times],
            y: [amounts],
            'marker.color': [risks]
        });

        // Update risk distribution
        const riskCounts = {
            low: 0,
            medium: 0,
            high: 0
        };

        transactions.forEach(t => {
            if (t.fraud_probability < 0.3) riskCounts.low++;
            else if (t.fraud_probability < 0.7) riskCounts.medium++;
            else riskCounts.high++;
        });

        Plotly.update('riskDistribution', {
            values: [[riskCounts.low, riskCounts.medium, riskCounts.high]]
        });
    }
};