
const API_BASE = "http://127.0.0.1:8000";

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

function createCell(value) {
    const cell = document.createElement("td");
    cell.textContent = value;
    return cell;
}

async function loadFinancialInsights() {
    const container = document.getElementById("financial-insights");

    try {
        const response = await fetch(`${API_BASE}/api/insights`);

        if (!response.ok) {
            throw new Error("Could not load financial insights.");
        }

        const insights = await response.json();
        container.replaceChildren();

        if (!Array.isArray(insights) || insights.length === 0) {
            container.textContent = "No financial insights available.";
            return;
        }

        insights.forEach((insight) => {
            const item = document.createElement("div");
            item.className = "insight-item";

            const heading = document.createElement("h4");
            heading.textContent = insight.title ?? "Financial observation";

            const description = document.createElement("p");
            description.textContent =
                insight.description ?? insight.message ?? "";

            item.append(heading, description);
            container.appendChild(item);
        });

    } catch (error) {
        console.error(error);
        container.textContent = "Unable to load financial insights.";
    }
}

async function loadAnomalies() {
    const tableBody = document.getElementById("anomalies-table-body");
    const message = document.getElementById("anomaly-message");

    try {
        const response = await fetch(`${API_BASE}/api/anomalies`);

        if (!response.ok) {
            throw new Error("Could not load anomaly candidates.");
        }

        const anomalies = await response.json();
        tableBody.replaceChildren();

        if (!Array.isArray(anomalies) || anomalies.length === 0) {
            message.textContent = "No anomaly candidates found.";
            return;
        }

        message.textContent =
            `${anomalies.length} candidate(s) identified for review.`;

        anomalies.forEach((anomaly) => {
            const row = document.createElement("tr");

            row.append(
                createCell(formatDate(anomaly["Transaction Date"])),
                createCell(anomaly["Category"] ?? "Unclassified"),
                createCell(formatCurrency(anomaly["Debit Amount"])),
                createCell(
                    formatCurrency(anomaly["Category_Upper_Bound"])
                )
            );

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error(error);
        message.textContent = "Unable to load anomaly candidates.";
    }
}

async function loadRecurringPayments() {
    const tableBody = document.getElementById("recurring-table-body");
    const message = document.getElementById("recurring-message");

    try {
        const response = await fetch(
            `${API_BASE}/api/recurring-payments`
        );

        if (!response.ok) {
            throw new Error("Could not load recurring payment patterns.");
        }

        const payments = await response.json();
        tableBody.replaceChildren();

        if (!Array.isArray(payments) || payments.length === 0) {
            message.textContent =
                "No potential recurring payment patterns found.";
            return;
        }

        message.textContent =
            `${payments.length} potential pattern(s) identified.`;

        payments.forEach((payment) => {
            const row = document.createElement("tr");

            row.append(
                createCell(payment["Category"] ?? "Unclassified"),
                createCell(formatCurrency(payment["Amount"])),
                createCell(
                    String(payment["Occurrences"] ?? "—")
                ),
                createCell(
                    payment["Pattern"] ??
                    payment["Recurring Pattern"] ??
                    "Potential recurring"
                )
            );

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error(error);
        message.textContent =
            "Unable to load recurring payment patterns.";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadFinancialInsights();
    loadAnomalies();
    loadRecurringPayments();
});

