const FlaggedTransactions = {
    currentData: [],
    filters: {
        riskLevel: 'all',
        timeFrame: '24h'
    },
    
    initialize: function() {
        console.log('Initializing FlaggedTransactions...');
        this.setupEventListeners();
        this.loadFlaggedTransactions();
        this.setupAutoRefresh();
        
        // Listen for new transactions from simulation
        $(document).on('transactionGenerated', (event, transaction) => {
            if (transaction.risk_score >= 70 || transaction.final_decision === 'flagged') {
                this.loadFlaggedTransactions();
            }
        });
    },

    setupEventListeners: function() {
        // Filter controls
        $('#riskLevelFilter').on('change', (e) => {
            this.filters.riskLevel = e.target.value;
            this.applyFilters();
        });

        $('#timeFrameFilter').on('change', (e) => {
            this.filters.timeFrame = e.target.value;
            this.loadFlaggedTransactions();
        });

        // Batch action buttons
        $('#selectAll').on('click', () => this.toggleSelectAll());
        $('#batchAction').on('click', () => this.executeBatchAction());
    },

    loadFlaggedTransactions: function() {
        const loadingOverlay = $('<div class="loading-overlay"><span>Loading...</span></div>');
        $('#flaggedTransactionsTable').prepend(loadingOverlay);

        $.get('/api/flagged/data', { timeFrame: this.filters.timeFrame })
            .done(data => {
                console.log('Received flagged transactions:', data);
                this.currentData = data.transactions || [];
                this.renderTransactions();
            })
            .fail(error => {
                console.error('Failed to load flagged transactions:', error);
                $('#flaggedTransactionsTable').html(
                    '<div class="error-message">Failed to load transactions. Please try again.</div>'
                );
            })
            .always(() => {
                loadingOverlay.remove();
            });
    },

    renderTransactions: function() {
        const container = $('#flaggedTransactionsTable');
        container.empty();

        // Add filter controls
        container.append(`
            <div class="filters-container">
                <select id="riskLevelFilter">
                    <option value="all">All Risk Levels</option>
                    <option value="high">High Risk</option>
                    <option value="medium">Medium Risk</option>
                    <option value="low">Low Risk</option>
                </select>
                <select id="timeFrameFilter">
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="30d">Last 30 Days</option>
                </select>
                <button id="selectAll">Select All</button>
                <button id="batchAction">Batch Action</button>
            </div>
        `);

        // Add transactions table
        const table = $('<table>').addClass('flagged-table');
        table.append(`
            <thead>
                <tr>
                    <th><input type="checkbox" id="selectAllCheckbox"></th>
                    <th>Time</th>
                    <th>Amount</th>
                    <th>Risk Score</th>
                    <th>ML Probability</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Flags</th>
                    <th>Actions</th>
                </tr>
            </thead>
        `);

        const tbody = $('<tbody>');
        this.currentData.forEach(transaction => {
            tbody.append(this.createTransactionRow(transaction));
        });

        table.append(tbody);
        container.append(table);

        // Reattach event listeners
        this.setupEventListeners();
    },

    createTransactionRow: function(transaction) {
        // Ensure transaction has all required properties with default values
        const safeTransaction = {
            transaction_id: transaction.transaction_id || 'unknown',
            timestamp: transaction.timestamp || new Date().toISOString(),
            Amount: transaction.Amount || 0,
            risk_score: transaction.risk_score || 0,
            ml_probability: transaction.ml_probability || 0,
            final_decision: transaction.final_decision || 'pending',
            pattern_type: transaction.pattern_type || 'unknown',
            location: transaction.location || 'unknown',
            flags: transaction.flags || []
        };

        const row = $('<tr>').addClass(this.getRiskClass(safeTransaction.risk_score));

        row.html(`
            <td><input type="checkbox" class="transaction-checkbox" data-id="${safeTransaction.transaction_id}"></td>
            <td>${new Date(safeTransaction.timestamp).toLocaleString()}</td>
            <td>$${Number(safeTransaction.Amount).toFixed(2)}</td>
            <td>${this.formatRiskScore(safeTransaction.risk_score)}%</td>
            <td>${(safeTransaction.ml_probability * 100).toFixed(2)}%</td>
            <td>${safeTransaction.location}</td>
            <td>${this.formatStatus(safeTransaction.final_decision)}</td>
            <td>${this.formatFlags(safeTransaction.flags)}</td>
            <td class="action-buttons">
                <div class="dropdown">
                    <button class="dropdown-toggle">Actions</button>
                    <div class="dropdown-content">
                        <button onclick="FlaggedTransactions.reviewTransaction('${safeTransaction.transaction_id}', 'confirm')">
                            Confirm Fraud
                        </button>
                        <button onclick="FlaggedTransactions.reviewTransaction('${safeTransaction.transaction_id}', 'false_positive')">
                            False Positive
                        </button>
                        <button onclick="FlaggedTransactions.reviewTransaction('${safeTransaction.transaction_id}', 'investigate')">
                            Need Investigation
                        </button>
                    </div>
                </div>
            </td>
        `);

        return row;
    },

    formatStatus: function(status) {
        if (!status) return 'Pending';
        return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
    },

    formatFlags: function(flags) {
        if (!flags || !flags.length) return 'None';
        return flags.map(flag => `<div class="flag-item">${flag.name}</div>`).join('');
    },

    getRiskClass: function(riskScore) {
        if (riskScore >= 70) return 'high-risk';
        if (riskScore >= 30) return 'medium-risk';
        return 'low-risk';
    },

    formatRiskScore: function(score) {
        return Math.round(score);
    },

    reviewTransaction: function(transactionId, status) {
        const loadingOverlay = $('<div class="loading-overlay"><span>Updating...</span></div>');
        $(`tr[data-id="${transactionId}"]`).append(loadingOverlay);

        $.post('/api/flagged/review', {
            transaction_id: transactionId,
            status: status
        })
        .done(response => {
            if (response.status === 'success') {
                this.loadFlaggedTransactions();
                this.showNotification('Transaction updated successfully', 'success');
            } else {
                this.showNotification('Failed to update transaction', 'error');
            }
        })
        .fail(error => {
            console.error('Review failed:', error);
            this.showNotification('Failed to update transaction', 'error');
        })
        .always(() => {
            loadingOverlay.remove();
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

    toggleSelectAll: function() {
        const checkboxes = $('.transaction-checkbox');
        const selectAllCheckbox = $('#selectAllCheckbox');
        checkboxes.prop('checked', selectAllCheckbox.prop('checked'));
    },

    executeBatchAction: function() {
        const selectedIds = $('.transaction-checkbox:checked')
            .map(function() {
                return $(this).data('id');
            })
            .get();

        if (selectedIds.length === 0) {
            this.showNotification('Please select transactions first', 'warning');
            return;
        }

        // Show batch action modal
        const modal = $(`
            <div class="modal">
                <div class="modal-content">
                    <h3>Batch Action</h3>
                    <p>Select action for ${selectedIds.length} transactions:</p>
                    <select id="batchActionType">
                        <option value="confirm">Confirm Fraud</option>
                        <option value="false_positive">Mark as False Positive</option>
                        <option value="investigate">Need Investigation</option>
                    </select>
                    <div class="modal-actions">
                        <button onclick="FlaggedTransactions.executeBatchUpdate()">Apply</button>
                        <button onclick="FlaggedTransactions.closeModal()">Cancel</button>
                    </div>
                </div>
            </div>
        `);

        $('body').append(modal);
    },

    executeBatchUpdate: function() {
        const selectedIds = $('.transaction-checkbox:checked')
            .map(function() {
                return $(this).data('id');
            })
            .get();
        const action = $('#batchActionType').val();

        $.post('/api/flagged/batch-review', {
            transaction_ids: selectedIds,
            status: action
        })
        .done(response => {
            if (response.status === 'success') {
                this.loadFlaggedTransactions();
                this.showNotification('Transactions updated successfully', 'success');
            }
        })
        .fail(error => {
            console.error('Batch update failed:', error);
            this.showNotification('Failed to update transactions', 'error');
        })
        .always(() => {
            this.closeModal();
        });
    },

    closeModal: function() {
        $('.modal').remove();
    },

    setupAutoRefresh: function() {
        setInterval(() => this.loadFlaggedTransactions(), 30000);
    },

    applyFilters: function() {
        const filteredData = this.currentData.filter(transaction => {
            if (this.filters.riskLevel === 'all') return true;
            
            const riskLevel = this.getRiskLevelFromScore(transaction.risk_score);
            return riskLevel === this.filters.riskLevel;
        });

        const container = $('#flaggedTransactionsTable tbody');
        container.empty();
        filteredData.forEach(transaction => {
            container.append(this.createTransactionRow(transaction));
        });
    },

    getRiskLevelFromScore: function(score) {
        if (score >= 70) return 'high';
        if (score >= 30) return 'medium';
        return 'low';
    }
};

// Initialize when document is ready
$(document).ready(function() {
    console.log('Initializing Flagged Transactions...');
    FlaggedTransactions.initialize();
});