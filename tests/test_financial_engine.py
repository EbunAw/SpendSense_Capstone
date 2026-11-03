from app.financial_engine import (
    get_financial_summary,
    get_category_breakdown,
    get_monthly_summary
)

from app.insights_engine import (
    get_anomaly_insights,
    get_recurring_payment_insights
)

def test_financial_summary():
    summary = get_financial_summary()

    assert isinstance(summary, dict)
    assert "total_income" in summary
    assert "total_outgoing" in summary
    assert "net_cash_flow" in summary
    assert "consumption_spending" in summary
    assert "savings" in summary
    assert "investment" in summary


def test_category_breakdown():
    categories = get_category_breakdown()

    assert isinstance(categories, list)
    assert len(categories) > 0

    for category in categories:
        assert "Category" in category
        assert "transaction_count" in category
        assert "total_spending" in category


def test_monthly_summary():
    monthly = get_monthly_summary()

    assert isinstance(monthly, list)
    assert len(monthly) > 0

    for month in monthly:
        assert "Month" in month
        assert "total_income" in month
        assert "total_outgoing" in month
        assert "net_cash_flow" in month

def test_anomaly_insights():
    anomalies = get_anomaly_insights()

    assert isinstance(anomalies, list)
    assert len(anomalies) > 0

    for anomaly in anomalies:
        assert "Category" in anomaly
        assert "Debit Amount" in anomaly
        assert "Category_Upper_Bound" in anomaly


def test_recurring_payment_insights():
    recurring = get_recurring_payment_insights()

    assert isinstance(recurring, list)
    assert len(recurring) > 0

    for payment in recurring:
        assert "Category" in payment
        assert "Amount" in payment
        assert "Occurrences" in payment
        assert "Pattern_Indication" in payment