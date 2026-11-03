# SpendSense

**An AI-powered personal finance transaction investigator for students and young professionals.**

SpendSense helps users understand their transaction history, identify spending patterns, review unusual transactions, and access financial-literacy information through an AI assistant.

## Problem Statement

Students and young professionals often find it difficult to understand where their money goes, recognize recurring payments, and identify unusual spending patterns. SpendSense provides a data-driven way to explore transaction activity and gain practical financial insights.

## Key Features

- **Dashboard:** View income, outgoing transactions, net cash flow, and consumption spending.
- **Transaction Explorer:** Search and review transaction records.
- **Spending Insights:** Explore category spending, recurring payment patterns, and anomaly candidates.
- **AI Financial Assistant:** Ask financial-literacy questions and receive answers grounded in a knowledge base with source references.
- **Financial Analysis:** Use Python and Pandas for deterministic calculations rather than relying on an LLM to calculate financial figures.

## Technology Stack

- Python
- FastAPI
- Pandas and NumPy
- ChromaDB
- Sentence Transformers
- Google Gemini API
- HTML, CSS, and JavaScript
- Chart.js
- Docker
- Pytest

## Dataset

SpendSense uses an anonymized bank transaction dataset containing transaction records from a UK account.

The dataset is denominated in GBP (£) and covers multiple years. It is used for transaction analysis, spending summaries, recurring-pattern detection, and anomaly screening.

### Dataset Limitations

- The dataset represents a single account and may not generalize to all users.
- The data is historical and does not represent real-time banking activity.
- Anomaly candidates are not confirmed fraud.
- Repeated transaction patterns are not necessarily subscriptions.
- The dataset becomes sparse after July 2022, so later reductions in transaction activity should not be interpreted as definitive spending trends.

## System Architecture

SpendSense separates deterministic financial analysis from AI-powered financial-literacy assistance.

1. Transaction data is loaded and processed using Python and Pandas.
2. Financial calculations are performed by deterministic functions.
3. Transaction insights are exposed through FastAPI endpoints.
4. Financial-literacy documents are processed and stored in ChromaDB.
5. The AI assistant retrieves relevant knowledge-base content to support grounded responses.
6. The frontend displays financial summaries, charts, transaction records, insights, and assistant responses.

## Project Structure

```text
SpendSense_Capstone/
├── app/
├── data/
├── evaluation/
├── knowledge_base/
├── tests/
├── templates/
├── static/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd SpendSense_Capstone
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add the required API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit `.env` or expose API keys.

### 5. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- Dashboard: http://localhost:8000
- API documentation: http://localhost:8000/docs

## Run with Docker

Build and start the container:

```powershell
docker compose up --build
```

The Docker configuration maps the application to port 8001 on the host:

- Application: http://localhost:8001
- API documentation: http://localhost:8001/docs

Docker deployment is included as part of the capstone implementation.

## Testing

Run the test suite:

```powershell
pytest
```

The current test suite contains 13 passing tests covering financial calculations and API behavior.

## Responsible Use and Limitations

SpendSense is an educational financial-analysis application, not a banking platform or professional financial-advice service.

- Financial totals are calculated using deterministic Python logic.
- The AI assistant is used for financial-literacy explanations.
- Anomaly detection identifies candidates for review, not confirmed fraud.
- Recurring transaction patterns require user interpretation.
- The application does not connect to a user's live bank account.

## Future Improvements

- Support additional datasets and currencies.
- Improve transaction categorization.
- Expand retrieval evaluation.
- Improve deployment reliability and monitoring.
- Add user-specific financial goals and budgeting features.

## Author

Developed as an independent AI/ML capstone project.