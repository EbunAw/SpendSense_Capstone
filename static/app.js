
const API_BASE = "http://localhost:8001";

let monthlyChart = null;
let categoryChart = null;

// Format financial values in GBP
function formatCurrency(value) {
    return new Intl.NumberFormat("en-GB", {
        style: "currency",
        currency: "GBP"
    }).format(value || 0);
}

// Load financial summary
async function loadSummary() {
    try {
        const response = await fetch(`${API_BASE}/api/summary`);

        if (!response.ok) {
            throw new Error("Unable to load financial summary");
        }

        const data = await response.json();

        document.getElementById("total-income").textContent =
            formatCurrency(data.total_income);

        document.getElementById("total-outgoing").textContent =
            formatCurrency(data.total_outgoing);

        document.getElementById("net-cash-flow").textContent =
            formatCurrency(data.net_cash_flow);

        document.getElementById("consumption-spending").textContent =
            formatCurrency(data.consumption_spending);

        document.getElementById("net-cash-flow").style.color =
            data.net_cash_flow < 0 ? "#D94A4A" : "#16845B";

    } catch (error) {
        console.error("Summary error:", error);
        document.getElementById("total-income").textContent = "Unavailable";
    }
}

// Load monthly financial chart
async function loadMonthlyChart() {
    try {
        const response = await fetch(`${API_BASE}/api/monthly`);

        if (!response.ok) {
            throw new Error("Unable to load monthly data");
        }

        const data = await response.json();

        const labels = data.map(item => item.Month);
        const income = data.map(item => item.total_income);
        const outgoing = data.map(item => item.total_outgoing);

        const context = document
            .getElementById("monthly-chart")
            .getContext("2d");

        if (monthlyChart) {
            monthlyChart.destroy();
        }

        monthlyChart = new Chart(context, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Income",
                        data: income,
                        borderColor: "#087F5B",
                        backgroundColor: "rgba(8, 127, 91, 0.08)",
                        tension: 0.35
                    },
                    {
                        label: "Outgoing",
                        data: outgoing,
                        borderColor: "#D99A43",
                        backgroundColor: "rgba(217, 154, 67, 0.08)",
                        tension: 0.35
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });

    } catch (error) {
        console.error("Monthly chart error:", error);
    }
}

// Load spending categories
async function loadCategoryChart() {
    try {
        const response = await fetch(`${API_BASE}/api/categories`);

        if (!response.ok) {
            throw new Error("Unable to load category data");
        }

        const data = await response.json();

        const filteredData = data.filter(
            item => item.total_spending > 0
        ).slice(0, 8);

        const labels = filteredData.map(item => item.Category);
        const amounts = filteredData.map(item => item.total_spending);

        const context = document
            .getElementById("category-chart")
            .getContext("2d");

        if (categoryChart) {
            categoryChart.destroy();
        }

        categoryChart = new Chart(context, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: amounts,
                    backgroundColor: [
                        "#087F5B",
                        "#39A982",
                        "#A7DCC5",
                        "#E5B96D",
                        "#83B5A0",
                        "#527E70",
                        "#C7D9D0",
                        "#B8A68C"
                    ],
                    borderWidth: 2,
                    borderColor: "#FFFFFF"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });

    } catch (error) {
        console.error("Category chart error:", error);
    }
}

// Load financial health insights
async function loadInsights() {
    try {
        const response = await fetch(`${API_BASE}/api/insights`);

        if (!response.ok) {
            throw new Error("Unable to load insights");
        }

        const insights = await response.json();

        const container = document.getElementById("financial-insights");

        container.innerHTML = "";

        insights.forEach(insight => {
            const card = document.createElement("div");
            card.className = "insight-item";

            const heading = document.createElement("h4");
            heading.textContent = insight.title;

            const message = document.createElement("p");
            message.textContent = insight.message;

            card.appendChild(heading);
            card.appendChild(message);
            container.appendChild(card);
        });

    } catch (error) {
        console.error("Insights error:", error);

        document.getElementById("financial-insights").textContent =
            "Financial insights are currently unavailable.";
    }
}

// Initialise dashboard
async function initialiseDashboard() {
    await Promise.all([
        loadSummary(),
        loadMonthlyChart(),
        loadCategoryChart(),
        loadInsights()
    ]);
}

document.addEventListener("DOMContentLoaded", initialiseDashboard);
