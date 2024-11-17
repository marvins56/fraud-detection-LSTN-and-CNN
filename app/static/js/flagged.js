// static/js/flagged.js
function loadFlaggedTransactions() {
    $.get('/api/flagged/data', function(data) {
        const container = $('#flaggedTransactions');
        container.empty();

        data.transactions.forEach(transaction => {
            const card = createTransactionCard(transaction);
            container.append(card);
        });
    });
}

function createTransactionCard(transaction) {
    const card = $('<div>').addClass('transaction-card');
    if (transaction.prediction === 'fraud') {
        card.addClass('fraud');
    }

    card.html(`
        <div class="transaction-header">
            <span class="time">${new Date(transaction.timestamp).toLocaleString()}</span>
            <span class="amount">$${transaction.Amount.toFixed(2)}</span>
        </div>
        <div class="transaction-details">
            <p>Risk Level: ${transaction.risk_level}</p>
            <p>Fraud Probability: ${(transaction.fraud_probability * 100).toFixed(2)}%</p>
            <p>Pattern Type: ${transaction.pattern_type}</p>
        </div>
        <div class="transaction-actions">
            <button onclick="reviewTransaction('${transaction.transaction_id}', 'confirm')">Confirm Fraud</button>
            <button onclick="reviewTransaction('${transaction.transaction_id}', 'false_positive')">False Positive</button>
            <button onclick="reviewTransaction('${transaction.transaction_id}', 'investigate')">Need Investigation</button>
        </div>
    `);

    return card;
}

function reviewTransaction(transactionId, status) {
    $.post('/api/flagged/review', {
        transaction_id: transactionId,
        status: status
    }, function(response) {
        if (response.status === 'success') {
            loadFlaggedTransactions();
        }
    });
}

$(document).ready(function() {
    loadFlaggedTransactions();
    // Refresh every 30 seconds
    setInterval(loadFlaggedTransactions, 30000);
});