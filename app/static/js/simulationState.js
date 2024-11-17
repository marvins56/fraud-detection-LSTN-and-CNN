// static/js/simulationState.js
const SimulationState = {
    isRunning: false,
    interval: null,
    
    startSimulation: function() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        localStorage.setItem('simulationRunning', 'true');
        this.interval = setInterval(() => this.generateTransaction(), 1000);
        
        // Update UI across all pages
        $('.simulation-status').text('Simulation Running');
        $('.simulation-toggle').text('Stop Simulation');
    },
    
    stopSimulation: function() {
        this.isRunning = false;
        localStorage.setItem('simulationRunning', 'false');
        if (this.interval) {
            clearInterval(this.interval);
        }
        
        // Update UI across all pages
        $('.simulation-status').text('Simulation Stopped');
        $('.simulation-toggle').text('Start Simulation');
    },
    
    generateTransaction: function() {
        $.post('/api/simulate', function(response) {
            if (response.status === 'success') {
                // Emit custom event for updates
                $(document).trigger('transactionGenerated', [response.transaction]);
            }
        });
    },
    
    initialize: function() {
        // Check if simulation was running before page change
        if (localStorage.getItem('simulationRunning') === 'true') {
            this.startSimulation();
        }
    }
};

// Initialize on all pages
$(document).ready(function() {
    console.log('SimulationState initialized');
    SimulationState.initialize();
});