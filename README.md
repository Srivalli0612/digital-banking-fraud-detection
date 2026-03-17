# Digital Banking Fraud Detection & Simulation Engine

A full-stack **fraud detection and simulation platform** for digital banking. Simulate normal and fraudulent transactions, run rule-based and ML-based anomaly detection, view real-time dashboards, and use REST APIs for ingestion and reporting.

---

## Table of Contents

- [Project Statement](#project-statement)
- [What This Project Does](#what-this-project-does)
- [Outcomes](#outcomes)
- [Modules](#modules)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running on Another PC](#running-on-another-pc)
- [How to Run](#how-to-run)
- [Using the Application](#using-the-application)
- [REST API](#rest-api)
- [Milestones & Evaluation](#milestones--evaluation)
- [Further Details](#further-details)

---

## Project Statement

This project aims to develop a **fraud detection and simulation engine** for digital banking platforms. The system:

- **Simulates** normal and fraudulent transactions to test anomaly detection rules.
- **Monitors** transaction flows and identifies risks using rule-based and ML-based techniques.
- **Integrates** with transaction APIs for ingestion and reporting.
- **Provides** dashboards for visualization and supports an ML plug-in for advanced fraud detection.

The platform helps banks evaluate resilience, improve fraud-prevention strategies, and ensure customer security.

---

## What This Project Does

| Feature | Description |
|--------|-------------|
| **Simulate transactions** | Web form or API to create single/bulk synthetic transactions (valid and fraudulent). |
| **Detect fraud** | Each transaction is scored by a **Java rule engine** (if running), or **ML model** (XGBoost), or **Python rule fallback**. |
| **Dashboard** | View total/suspicious/safe counts, fraud vs normal chart, 7-day trend, and recent transactions. |
| **History & filters** | Full transaction history with filters: All / Fraud / Safe. |
| **Alert notifications** | Real‑time bell icon with unread fraudulent transaction count; click to jump to fraud history and mark alerts reviewed. |
| **REST API** | Ingest transactions, list with filters, get flagged report, run batch simulation, export ML data, get model metrics. |
| **ML plug-in** | Train on synthetic data (XGBoost + SMOTE), export training CSV, evaluate model (accuracy, precision, recall, F1, ROC AUC). |

---

## Outcomes

- **Simulation** of both normal and fraudulent transactions (web UI, batch API, optional Java CLI).
- **Anomaly detection** using rule-based (Java/Python) and ML-based (XGBoost) techniques.
- **Real-time dashboards** for fraud monitoring (stats, trend, recent transactions; History with filters).
- **API-driven** transaction ingestion and reporting via REST API Gateway.
- **Enhanced banking security** through end-to-end simulation and detection (simulate → detect → flag → report).

---

## Modules

| # | Module | What it does | Where it lives |
|---|--------|--------------|----------------|
| 1 | **Transaction Simulation Engine** | Generates synthetic transactions (valid + fraudulent); customizable scenarios. | Web: `templates/simulate.html`, `app.py` (Simulate route, `POST /api/v1/simulate/batch`). Java: `Tranjaction/src/Amount.java` (CLI generator). |
| 2 | **Anomaly Detection Core** | Applies business rules and ML to flag suspicious activity. | Java rules: `Tranjaction/src/Amount.java`, `FraudAnalysisServer.java`. Python: `model/predict.py`, `model/java_fraud_client.py`. ML: `ML model/ml_pipeline.py`. |
| 3 | **Dashboard & Monitoring Hub** | Shows risk scores, trends, recent transactions; History with filters (All / Fraud / Safe). | `templates/dashboard.html`, `templates/history.html`, `app.py` (dashboard, history routes). |
| 4 | **Transaction API Gateway** | Ingests external transaction data; REST APIs for reporting and simulation. | `app.py` under `/api/v1/`: transactions (POST/GET), reports/flagged, simulate/batch. |
| 5 | **ML Plug-in & Analytics** | Trains ML model; export training data; model evaluation metrics. | `ML model/ml_pipeline.py`, `model/predict.py`, `model/ml_eval.py`, `/api/v1/ml/export-training-data`, `/api/v1/ml/evaluate`. |

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Python 3, Flask |
| Database | MySQL (users, transactions) |
| ML | scikit-learn, XGBoost, imbalanced-learn (SMOTE), pandas, joblib |
| Rule engine | Java (optional HTTP service on port 8080) |
| Frontend | Jinja2 templates, CSS (static/style.css) |

---

## Project Structure

```
├── app.py                      # Flask app: auth, dashboard, simulate, history, API Gateway, ML endpoints
├── requirements.txt           # Python dependencies
├── README.md                   # This file
├── PROJECT.md                  # Full project statement, outcomes, modules, milestones
├── run_app.bat                 # Start Flask app (Windows)
├── run_java_fraud_service.bat  # Start Java fraud service on port 8080 (Windows)
├── train_model.bat             # Train ML model and save to model/ (Windows)
├── run_tests.py                # Tests for predict and Flask routes
│
├── model/                      # Detection & ML runtime
│   ├── __init__.py
│   ├── predict.py              # Fraud prediction: Java → ML → rule-based fallback
│   ├── java_fraud_client.py    # HTTP client to Java fraud service
│   ├── ml_eval.py              # Load and return ML evaluation metrics
│   ├── fraud_detector_pipeline.joblib   # (after training) ML pipeline
│   ├── threshold.json          # (after training) decision threshold
│   └── evaluation_metrics.json # (after training) accuracy, F1, etc.
│
├── templates/                  # HTML pages
│   ├── base.html               # Layout, nav (Dashboard, Simulate, History)
│   ├── login.html, register.html
│   ├── dashboard.html          # Stats, Fraud vs Normal, trend, recent transactions
│   ├── simulate.html           # Single transaction simulation form
│   ├── result.html             # Result of a simulation (risk, status)
│   └── history.html            # Transaction history with All / Fraud / Safe filter
│
├── static/
│   └── style.css               # App styles (dark theme, cards, tables)
│
├── ML model/                   # ML training
│   ├── ml_pipeline.py          # Train XGBoost + SMOTE; save pipeline & metrics to model/
│   └── synthetic_transactions_15000.csv   # Synthetic dataset for training
│
└── Tranjaction/                # Java rule-based fraud engine (optional)
    └── src/
        ├── Amount.java         # Fraud rules (amount, time, location, etc.)
        └── FraudAnalysisServer.java   # HTTP server POST /analyze on port 8080
```

---

## Prerequisites

- **Python 3.8+** (for Flask app and ML)
- **Java** (optional; only if you want the Java rule-based fraud service)
- **pip** (to install `requirements.txt`)
- **MySQL 8+** (for the main application database)

---

## Installation

1. **Clone or download** the project and open a terminal in the project root.

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   # source venv/bin/activate   # Linux/macOS
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration (`.env`)**

Create a file named **`.env`** in the project root (same folder as `app.py`) with at least:

```env
SECRET_KEY=fraud-detection-dev-secret-change-in-production

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Akshay
DB_NAME=fraud_app

# Admin registration secret used on /admin/register
ADMIN_REGISTRATION_KEY=ADMIN-KEY-1234
```

These values are read automatically by `app.py` using `python-dotenv`. Adjust them for your own MySQL user/password and change the secrets for production.

4. **Optional – Train the ML model** (so detection uses ML when Java is not running):
   ```cmd
   train_model.bat
   ```
   Or manually:
   ```bash
   cd "ML model"
   set FRAUD_MODEL_OUTPUT=..\model    # Windows
   python ml_pipeline.py
   ```
   This creates `model/fraud_detector_pipeline.joblib`, `model/threshold.json`, and `model/evaluation_metrics.json`.

5. **Optional – Start the Java fraud service** (for rule-based detection on port 8080):
   ```cmd
   run_java_fraud_service.bat
   ```
   Keep it running if you want the app to use the Java engine first.

---

## How to Run

1. **Start the web application**:
   ```cmd
   run_app.bat
   ```
   Or:
   ```bash
   python app.py
   ```
   The app runs at **http://127.0.0.1:5000** (and listens on all interfaces, e.g. http://0.0.0.0:5000).

2. **Open the app** in a browser: register a user, log in, then use:
   - **Dashboard** – overview, trend, recent transactions
   - **Simulate** – run a single transaction and see fraud result
   - **History** – view all transactions with All / Fraud / Safe filter

3. **Detection order** (for each transaction):
   - If Java fraud service is running → **Java engine**
   - Else if ML pipeline exists in `model/` → **ML model**
   - Else → **Python rule-based fallback**

---

## Using the Application

| Page | What you do |
|------|-------------|
| **Register / Login** | Create an account or sign in. Required for Dashboard, Simulate, History, and APIs. |
| **Dashboard** | See total transactions, suspicious/safe counts, Fraud vs Normal bar, 7-day trend, and recent transactions table. |
| **Simulate** | Enter amount, type (credit/debit), mode (UPI, NEFT, etc.), optional location and time. Submit to get risk score and Fraud / Not fraud result. |
| **History** | View all your transactions. Use the **Filter** dropdown: All, Fraud, or Safe. |
| **APIs** | Use the REST endpoints below (e.g. from Postman or scripts); maintain a logged-in session (cookies) for auth. |

---

## REST API

Base URL: **http://localhost:5000/api/v1/**  
Authentication: **Session cookie** (log in via browser or send session cookie with requests).

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/transactions` | Ingest one or more transactions (JSON object or array). Runs fraud detection and stores. |
| **GET** | `/transactions` | List transactions. Query params: `risk_level`, `is_fraud`, `from_date`, `to_date`, `limit` (max 500). |
| **GET** | `/reports/flagged` | Get flagged (suspicious) transactions only. |
| **POST** | `/simulate/batch` | Generate bulk synthetic transactions. Body: `count` (default 10, max 100), `fraud_ratio` (0–1). |
| **GET** | `/ml/export-training-data` | Download training dataset as CSV. |
| **GET** | `/ml/evaluate` | Get ML model metrics (accuracy, precision, recall, F1, ROC AUC). Returns 404 if model not trained. |

**Example – Ingest a transaction (POST /api/v1/transactions):**
```json
{
  "amount": 25000,
  "type": "debit",
  "mode": "UPI",
  "current_balance": 100000,
  "transaction_time": "2026-03-07T10:30:00",
  "location": "India"
}
```

---

## Summary

This project delivers a **Digital Banking Fraud Detection & Simulation Engine** with:

- Transaction simulation (web + API + optional Java),
- Anomaly detection (Java rules → ML → Python rules),
- Dashboard and History with filters,
- REST API Gateway for ingestion and reporting,
- ML plug-in with training, export, and evaluation.

