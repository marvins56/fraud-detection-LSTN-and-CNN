// static/js/utils/debug.js
const DebugTools = {
    isDebugMode: false,
    
    initialize: function() {
        // Add debug panel
        $('body').append(`
            <div id="debugPanel" style="display:none">
                <h3>Debug Panel</h3>
                <div class="debug-controls">
                    <button onclick="DebugTools.toggleSimulationSpeed()">Toggle Speed</button>
                    <button onclick="DebugTools.logState()">Log State</button>
                </div>
                <div class="debug-log"></div>
            </div>
        `);
        
        // Add keyboard shortcut (Ctrl+D)
        $(document).keydown(function(e) {
            if (e.ctrlKey && e.key === 'd') {
                DebugTools.toggleDebugMode();
            }
        });
    },
    
    toggleDebugMode: function() {
        this.isDebugMode = !this.isDebugMode;
        $('#debugPanel').toggle();
    },
    
    log: function(message) {
        if (this.isDebugMode) {
            console.log('[DEBUG]', message);
            $('.debug-log').prepend(`<div>${new Date().toISOString()}: ${message}</div>`);
        }
    }
};

// Initialize debug tools
$(document).ready(function() {
    DebugTools.initialize();
});