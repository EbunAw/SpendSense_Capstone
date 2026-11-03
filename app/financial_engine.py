from pathlib import Path
import pandas as pd


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Location of cleaned transaction data
DATA_FILE = BASE_DIR / "data" / "transactions_cleaned.csv"


def load_transactions():
    """
    Load the cleaned transaction dataset.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_FILE}"
        )

    transactions = pd.read_csv(DATA_FILE)

    transactions["Transaction Date"] = pd.to_datetime(
        transactions["Transaction Date"],
        errors="coerce"
    )

    return transactions

def get_financial_summary():
    """
    Calculate the overall financial position.
    """
    df = load_transactions()

    total_income = df["Income Amount"].sum()
    total_outgoing = df["Outgoing Amount"].sum()
    net_cash_flow = total_income - total_outgoing

    total_consumption = df["Consumption Spending"].sum()
    total_savings = df["Savings Amount"].sum()
    total_investment = df["Investment Amount"].sum()

    return {
        "total_income": round(float(total_income), 2),
        "total_outgoing": round(float(total_outgoing), 2),
        "net_cash_flow": round(float(net_cash_flow), 2),
        "consumption_spending": round(float(total_consumption), 2),
        "savings": round(float(total_savings), 2),
        "investment": round(float(total_investment), 2)
    }


def get_category_breakdown():
    """
    Calculate spending totals for each category.
    """
    df = load_transactions()

    category_summary = (
        df.groupby("Category", as_index=False)
        .agg(
            transaction_count=("Transaction Number", "count"),
            total_spending=("Consumption Spending", "sum")
        )
        .sort_values(
            by="total_spending",
            ascending=False
        )
    )

    return category_summary.to_dict(orient="records")

def get_monthly_summary():
    """
    Calculate monthly income, expenditure and cash flow.
    """
    df = load_transactions()

    df["Month"] = df["Transaction Date"].dt.to_period("M")

    monthly = (
        df.groupby("Month")
        .agg(
            total_income=("Income Amount", "sum"),
            total_outgoing=("Outgoing Amount", "sum"),
            consumption_spending=("Consumption Spending", "sum"),
            savings=("Savings Amount", "sum"),
            investment=("Investment Amount", "sum")
        )
        .reset_index()
    )

    monthly["net_cash_flow"] = (
        monthly["total_income"] - monthly["total_outgoing"]
    )

    monthly["Month"] = monthly["Month"].astype(str)

    return monthly.round(2).to_dict(orient="records")

def get_transaction_records(limit=100):
    df = load_transactions()

    transactions = df.sort_values(
        by="Transaction Date",
        ascending=False
    ).head(limit)

    return transactions[
        [
            "Transaction Number",
            "Transaction Date",
            "Category",
            "Income Amount",
            "Outgoing Amount",
            "Consumption Spending"
        ]
    ].fillna(0).to_dict(orient="records")