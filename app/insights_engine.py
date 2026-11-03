from app.financial_engine import (
    get_financial_summary,
    get_category_breakdown
)
from pathlib import Path
import pandas as pd

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Location of anomaly results
ANOMALY_FILE = BASE_DIR / "data" / "category_anomalies.csv"

# Location of potential recurring payment results
RECURRING_FILE = (
    BASE_DIR / "data" / "potential_recurring_payments.csv"
)

def get_financial_health_insights():
    """
    Generate insights about the overall financial position.
    """
    summary = get_financial_summary()
    categories = get_category_breakdown()

    insights = []

    # Analyse overall cash flow
    if summary["net_cash_flow"] < 0:
        insights.append({
            "type": "warning",
            "title": "Negative cash flow",
            "message": (
                "Your total outgoing is higher than your total income."
            )
        })
    else:
        insights.append({
            "type": "positive",
            "title": "Positive cash flow",
            "message": (
                "Your total income is higher than your total outgoing."
            )
        })

    # Identify the highest consumption spending category
    spending_categories = [
        category for category in categories
        if category["total_spending"] > 0
    ]

    if spending_categories:
        highest_category = spending_categories[0]

        insights.append({
            "type": "information",
            "title": "Highest spending category",
            "message": (
                f'{highest_category["Category"]} is your highest '
                f'spending category, with £'
                f'{highest_category["total_spending"]:,.2f} recorded.'
            )
        })

    return insights

def load_anomalies():
    """
    Load category-aware anomaly results.
    """
    if not ANOMALY_FILE.exists():
        raise FileNotFoundError(
            f"Anomaly file not found: {ANOMALY_FILE}"
        )

    anomalies = pd.read_csv(ANOMALY_FILE)

    return anomalies

def get_anomaly_insights(limit=10):
    """
    Return the highest-value transactions flagged as anomalies.
    """
    anomalies = load_anomalies()

    anomalies = anomalies.sort_values(
        by="Debit Amount",
        ascending=False
    )

    results = anomalies.head(limit)

    return results[
        [
            "Transaction Number",
            "Transaction Date",
            "Category",
            "Debit Amount",
            "Category_Upper_Bound"
        ]
    ].to_dict(orient="records")

def load_recurring_payments():
    """
    Load potential recurring payment patterns.
    """
    if not RECURRING_FILE.exists():
        raise FileNotFoundError(
            f"Recurring payments file not found: {RECURRING_FILE}"
        )

    recurring = pd.read_csv(RECURRING_FILE)

    return recurring

def get_recurring_payment_insights():
    """
    Return potential recurring payment patterns.
    """
    recurring = load_recurring_payments()

    return recurring[
        [
            "Category",
            "Amount",
            "Occurrences",
            "First_Date",
            "Last_Date",
            "Median_Gap_Days",
            "Gap_Std_Dev",
            "Pattern_Indication"
        ]
    ].to_dict(orient="records")