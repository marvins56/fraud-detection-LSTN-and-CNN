const TransactionTable = {
    updateTable: function(transactions) {
        const table = $('#transactionsTable');
        let html = `
            <table class="transaction-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Amount</th>
                        <th>Risk Level</th>
                        <th>Probability</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        transactions.slice(-10).forEach(t => {
            const riskClass = this.getRiskClass(t.fraud_probability);
            html += `
                <tr class="${riskClass}">
                    <td>${new Date(t.timestamp).toLocaleString()}</td>
                    <td>$${t.Amount.toFixed(2)}</td>
                    <td>${t.risk_level}</td>
                    <td>${(t.fraud_probability * 100).toFixed(2)}%</td>
                    <td>${this.getStatusBadge(t)}</td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        table.html(html);
    },

    getRiskClass: function(probability) {
        if (probability >= 0.7) return 'high-risk';
        if (probability >= 0.3) return 'medium-risk';
        return 'low-risk';
    },

    getStatusBadge: function(transaction) {
        if (transaction.fraud_probability >= 0.7) {
            return '<span class="badge danger">High Risk</span>';
        } else if (transaction.fraud_probability >= 0.3) {
            return '<span class="badge warning">Medium Risk</span>';
        }
        return '<span class="badge success">Low Risk</span>';
    }
};