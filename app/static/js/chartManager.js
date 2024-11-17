// static/js/utils/chartManager.js
const ChartManager = {
    charts: {},
    
    createChart: function(elementId, config) {
        const container = document.getElementById(elementId);
        
        // Add loading overlay
        $(container).append('<div class="loading-overlay"><div class="loading-spinner"></div></div>');
        
        try {
            this.charts[elementId] = Plotly.newPlot(elementId, 
                config.data, 
                config.layout, 
                config.options
            ).then(() => {
                // Remove loading overlay on success
                $(container).find('.loading-overlay').remove();
            }).catch(error => {
                console.error(`Error creating chart ${elementId}:`, error);
                this.handleChartError(container, error);
            });
        } catch (error) {
            console.error(`Error initializing chart ${elementId}:`, error);
            this.handleChartError(container, error);
        }
    },
    
    updateChart: function(elementId, newData) {
        const container = document.getElementById(elementId);
        $(container).find('.loading-overlay').remove();
        $(container).append('<div class="loading-overlay"><div class="loading-spinner"></div></div>');
        
        try {
            Plotly.update(elementId, newData).then(() => {
                $(container).find('.loading-overlay').remove();
            }).catch(error => {
                console.error(`Error updating chart ${elementId}:`, error);
                this.handleChartError(container, error);
            });
        } catch (error) {
            console.error(`Error in chart update ${elementId}:`, error);
            this.handleChartError(container, error);
        }
    },
    
    handleChartError: function(container, error) {
        $(container).find('.loading-overlay').remove();
        $(container).append(`
            <div class="chart-error">
                <p>Error loading chart</p>
                <button onclick="ChartManager.retryChart('${container.id}')">Retry</button>
            </div>
        `);
    },
    
    retryChart: function(elementId) {
        // Implement retry logic
        location.reload();
    }
};

$(document).ready(function() {
    console.log('ChartManager initialized');
});