# SpendSense

**An AI-powered personal finance transaction investigator for students and young professionals.**

SpendSense helps users understand where their money goes, identify spending patterns, review unusual transactions, and access financial-literacy information through a retrieval-augmented generation (RAG) assistant.

## Problem Statement

Students and young professionals often find it difficult to understand their transaction history, recognize recurring payments, and identify unusual spending patterns.

SpendSense provides a data-driven way to explore transaction activity and gain practical financial insights. It combines deterministic financial analysis with an AI-powered financial-literacy assistant to help users make better-informed decisions.

## Key Features

- **Dashboard:** View income, outgoing transactions, net cash flow, and consumption spending.
- **Transaction Explorer:** Search and review transaction records.
- **Spending Insights:** Explore category spending, recurring payment patterns, and anomaly candidates.
- **AI Financial Assistant:** Ask financial-literacy questions and receive answers grounded in a knowledge base, with source references.
- **Deterministic Financial Analysis:** Use Python and Pandas for financial calculations instead of relying on an LLM to calculate financial figures.
- **Responsible AI Behavior:** The assistant can acknowledge when the retrieved context does not contain enough information to answer a question.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Data Analysis | Pandas, NumPy |
| RAG and Retrieval | ChromaDB, Sentence Transformers |
| LLM | Google Gemini API |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Containerization | Docker, Docker Compose |
| Testing | Pytest |
| CI | GitHub Actions |

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
4. Financial-literacy documents are processed, embedded, and stored in ChromaDB.
5. When a user asks a question, the RAG pipeline retrieves relevant knowledge-base content.
6. The retrieved context is passed to the LLM to generate a grounded response.
7. The frontend displays financial summaries, charts, transaction records, insights, and assistant responses.

The application is designed so that financial calculations remain deterministic, while the LLM is used for explanations based on retrieved financial-literacy content.

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
├── .github/
│   └── workflows/
│       └── tests.yml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/EbunAw/SpendSense_Capstone.git
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

Create a `.env` file in the project root and add your Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit `.env` or expose API keys.

### 5. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- Dashboard: [http://localhost:8000](http://localhost:8000)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## Run with Docker

Build and start the application:

```powershell
docker compose up -d --build
```

The Docker configuration maps the application to port 8001 on the host:

- Application: [http://localhost:8001](http://localhost:8001)
- API documentation: [http://localhost:8001/docs](http://localhost:8001/docs)

The Docker Compose configuration mounts the local ChromaDB directory into the container so the financial-literacy collection is available to the RAG assistant.

To stop the application:

```powershell
docker compose down
```

## Testing

Run the test suite:

```powershell
python -m pytest -q
```

**Current test result: 13 passed.**

The test suite covers financial calculations and API behavior. The local test run reports one ChromaDB dependency deprecation warning, which does not cause the tests to fail.

## Continuous Integration

SpendSense uses GitHub Actions to run the test suite automatically when changes are pushed to the `main` branch or when a pull request targets `main`.

The CI workflow:

1. Checks out the repository.
2. Sets up Python.
3. Installs project dependencies.
4. Runs the Pytest suite.

The workflow has been configured and successfully completed with a green check.

## Responsible Use and Limitations

SpendSense is an educational financial-analysis application, not a banking platform or professional financial-advice service.

- Financial totals are calculated using deterministic Python logic.
- The AI assistant provides financial-literacy explanations grounded in retrieved content.
- Anomaly detection identifies candidates for review, not confirmed fraud.
- Recurring transaction patterns require user interpretation.
- The application does not connect to a user's live bank account.
- The quality of AI responses depends on the coverage and relevance of the financial knowledge base.

## Future Improvements

- Support additional datasets and currencies.
- Improve transaction categorization.
- Expand retrieval evaluation.
- Improve deployment reliability and monitoring.
- Add user-specific financial goals and budgeting features.

## Author

Developed as an independent AI/ML capstone project.

[GitHub Repository](https://github.com/EbunAw/SpendSense_Capstone)
