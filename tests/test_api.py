from fastapi.testclient import TestClient
from app.main import app
from app import main

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "SpendSense" in response.text


def test_financial_summary_endpoint():
    response = client.get("/api/summary")

    assert response.status_code == 200
    assert "total_income" in response.json()


def test_categories_endpoint():
    response = client.get("/api/categories")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_monthly_endpoint():
    response = client.get("/api/monthly")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_insights_endpoint():
    response = client.get("/api/insights")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_anomalies_endpoint():
    response = client.get("/api/anomalies")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_recurring_payments_endpoint():
    response = client.get("/api/recurring-payments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_ask_endpoint(monkeypatch):
    def mock_ask_financial_question(question):
        return {
            "question": question,
            "answer": "Build an emergency fund gradually.",
            "sources": [
                {
                    "document": "financial_guide.md",
                    "section": "3. Building an Emergency Fund",
                    "chunk_number": 3,
                    "reference_urls": "https://example.com"
                }
            ]
        }

    monkeypatch.setattr(
        main,
        "ask_financial_question",
        mock_ask_financial_question
    )

    response = client.post(
        "/api/ask",
        json={
            "question": "How do I build an emergency fund?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "How do I build an emergency fund?"
    assert data["answer"] == "Build an emergency fund gradually."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["section"] == "3. Building an Emergency Fund"