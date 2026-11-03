from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel

from app.financial_engine import (
    get_financial_summary,
    get_category_breakdown,
    get_monthly_summary,
    get_transaction_records
)

from app.insights_engine import (
    get_financial_health_insights,
    get_anomaly_insights,
    get_recurring_payment_insights
)
from app.rag_engine import ask_financial_question

class QuestionRequest(BaseModel):
    question: str

# Initialise the FastAPI application
app = FastAPI(
    title="SpendSense API",
    description="An AI-powered personal finance analysis application.",
    version="1.0.0"
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure HTML templates
templates = Jinja2Templates(directory="templates")

@app.get("/api/transactions")
def transaction_records():
    return get_transaction_records()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.get("/transactions")
def transactions_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={}
    )


@app.get("/insights")
def insights_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="insights.html",
        context={}
    )


@app.get("/assistant")
def assistant_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="assistant.html",
        context={}
    )


@app.get("/api/summary")
def financial_summary():
    """
    Return the overall financial summary.
    """
    return get_financial_summary()

@app.get("/api/categories")
def spending_categories():
    """
    Return spending totals grouped by category.
    """
    return get_category_breakdown()

@app.get("/api/monthly")
def monthly_analysis():
    """
    Return monthly income, expenditure and cash flow.
    """
    return get_monthly_summary()

@app.get("/api/insights")
def financial_insights():
    """
    Return automatically generated financial insights.
    """
    return get_financial_health_insights()

@app.get("/api/anomalies")
def transaction_anomalies():
    """
    Return unusual transactions flagged for review.
    """
    return get_anomaly_insights()

@app.get("/api/recurring-payments")
def recurring_payments():
    """
    Return potential recurring payment patterns.
    """
    return get_recurring_payment_insights()

@app.post("/api/ask")
def ask_question(request: QuestionRequest):
    """
    Answer a financial question using the RAG knowledge base.
    """

    return ask_financial_question(request.question)