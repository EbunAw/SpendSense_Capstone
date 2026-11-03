
const API_BASE = "http://localhost:8001";

const currencyFormatter = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP"
});

function formatCurrency(value) {
    return currencyFormatter.format(Number(value) || 0);
}

function formatDate(value) {
    if (!value) return "—";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "—";

    return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

let allTransactions = [];

function renderTransactions(transactions) {
    const tableBody = document.getElementById("transactions-table-body");
    const message = document.getElementById("transaction-message");

    tableBody.replaceChildren();

    if (transactions.length === 0) {
        message.textContent = "No transactions match your search.";
        return;
    }

    message.textContent = `${transactions.length} transaction(s) displayed.`;

    transactions.forEach((transaction) => {
        const row = document.createElement("tr");

        const values = [
            transaction["Transaction Number"] ?? "—",
            formatDate(transaction["Transaction Date"]),
            transaction["Category"] ?? "Unclassified",
            formatCurrency(transaction["Income Amount"]),
            formatCurrency(transaction["Outgoing Amount"]),
            formatCurrency(transaction["Consumption Spending"])
        ];

        values.forEach((value) => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });
}

function updateTransactionCards(transactions) {
    const totalIncome = transactions.reduce(
        (total, transaction) =>
            total + (Number(transaction["Income Amount"]) || 0),
        0
    );

    const totalOutgoing = transactions.reduce(
        (total, transaction) =>
            total + (Number(transaction["Outgoing Amount"]) || 0),
        0
    );

    document.getElementById("records-count").textContent =
        transactions.length.toLocaleString("en-GB");

    document.getElementById("transactions-income").textContent =
        formatCurrency(totalIncome);

    document.getElementById("transactions-outgoing").textContent =
        formatCurrency(totalOutgoing);
}

function filterTransactions() {
    const searchTerm = document
        .getElementById("transaction-search")
        .value
        .trim()
        .toLowerCase();

    const filteredTransactions = allTransactions.filter((transaction) => {
        const transactionNumber = String(
            transaction["Transaction Number"] ?? ""
        ).toLowerCase();

        const category = String(
            transaction["Category"] ?? ""
        ).toLowerCase();

        return (
            transactionNumber.includes(searchTerm) ||
            category.includes(searchTerm)
        );
    });

    renderTransactions(filteredTransactions);
}

async function loadTransactions() {
    const message = document.getElementById("transaction-message");

    try {
        const response = await fetch(`${API_BASE}/api/transactions`);

        if (!response.ok) {
            throw new Error("Unable to retrieve transaction records.");
        }

        allTransactions = await response.json();

        updateTransactionCards(allTransactions);
        renderTransactions(allTransactions);

    } catch (error) {
        console.error("Transaction loading error:", error);
        message.textContent =
            "Could not load transactions. Please check that the SpendSense API is running.";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document
        .getElementById("transaction-search")
        .addEventListener("input", filterTransactions);

    loadTransactions();
});
