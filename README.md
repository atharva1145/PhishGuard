# PhishGuard — Explainable AI Phishing Detection Platform

<div align="center">

![PhishGuard Shield](https://img.shields.io/badge/PhishGuard-Cybersecurity%20XAI-06b6d4?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-61dafb?style=for-the-badge&logo=react&logoColor=black)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-f7931e?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-28%20Passed-10b981?style=for-the-badge)

</div>

**PhishGuard** is a defensive, explainable AI cybersecurity platform that analyzes suspicious URLs and email messages, predicts whether they are potentially phishing or legitimate, and provides transparent mathematical and heuristic evidence behind each prediction.

Built for AI/ML engineering portfolios, PhishGuard emphasizes strict empirical validation, leakage-free train/test partitioning, zero external network execution during URL scans, and exact linear feature attribution ($w_i \cdot x_i$) for interpretability.

---

## Key Features

1. **URL Threat Scanner (Lexical & Structural Analysis):**
   - Strictly local string parsing (`urllib.parse` + regex) without outbound HTTP requests or DNS resolutions.
   - Extracts 24 engineered features (hostname length, subdomains, punycode, raw IP hosts, sensitive tokens, port anomalies).
   - Generates deterministic risk indicators with severity ratings and rationale.
2. **Email NLP Threat Scanner (TF-IDF + Linear Classification):**
   - Strips HTML safely and normalizes entity representations (`__URL__`, `__EMAIL__`, `__MONEY__`, `__PHONE__`).
   - Analyzes unigrams and bigrams via sublinear TF-IDF vectorization.
   - Identifies influential vocabulary terms and detects psychological urgency cues, direct credential harvesting, and wire fraud themes.
3. **Transparent Explainable AI (XAI):**
   - Log-odds mathematical contributions calculated directly from fitted model coefficients and scaled input vectors.
   - Transparent two-way feature contribution charts (pushing toward Phishing vs. pushing toward Legitimate).
4. **Rigorous Model Evaluation Dashboard:**
   - Real test-set metrics generated exclusively from held-out test splits.
   - Accuracy, Precision, Recall, F1-Score, False-Positive Rate ($FPR = FP / (FP + TN)$), False-Negative Rate ($FNR = FN / (FN + TP)$).
   - 2x2 interactive Confusion Matrix and candidate model comparison table (Logistic Regression vs. Random Forest vs. Linear SVM).
   - Safe, sanitized misclassified test sample inspector.
5. **Audit Scan History:**
   - Lightweight local SQLite persistence with privacy protection (raw email bodies are never stored).
   - Filter by scan type, filter by prediction verdict, search targets, inspect full details, or clear records.

---

## System Architecture

```
PhishGuard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app bootstrap, CORS, lifespan
│   │   ├── api/routes.py        # REST endpoints (/health, /models, /scan/*, /metrics, /history)
│   │   ├── core/config.py       # Configuration and paths
│   │   ├── database/db.py       # SQLite scan_history persistence
│   │   ├── schemas/             # Pydantic schemas for requests and responses
│   │   └── services/            # URL scanner, Email scanner, Model services
│   ├── tests/                   # 11 Automated API & database tests
│   └── requirements.txt         # Backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, MetricCard, RiskBadge, ExplanationCard, etc.
│   │   ├── pages/               # Overview, UrlScanner, EmailScanner, Evaluation, History, About
│   │   ├── services/api.ts      # Typed REST client
│   │   └── types/index.ts       # TypeScript interfaces
│   ├── package.json             # React, Vite, Tailwind CSS, Lucide, Recharts
│   └── vite.config.ts           # Development proxy configuration
├── ml/
│   ├── data/                    # Raw benchmarks and provenance metadata
│   ├── models/                  # Serialized Joblib pipelines (url_detector, email_detector)
│   ├── reports/                 # JSON evaluation reports & model comparison data
│   ├── src/                     # Feature extractors, NLP pipeline, training, XAI engine
│   └── tests/                   # 17 Automated ML, feature extraction, and leakage tests
├── scripts/
│   ├── train_models.py          # Unified model training & evaluation pipeline
│   └── run_tests.py             # Unified test runner
├── docs/
│   ├── METHODOLOGY.md           # Mathematical definitions, taxonomy, leakage protocol
│   └── ARCHITECTURE.md          # System component architecture & security boundaries
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

---

## Quickstart Guide

### Prerequisites
- **Python:** 3.11 or 3.12 installed
- **Node.js:** v18+ and `npm` installed
- **Operating System:** Windows, macOS, or Linux

---

### Step 1: Clone and Environment Setup

#### Windows PowerShell
```powershell
# Navigate to project directory
cd PhishGuard

# Optional: Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### Linux / macOS
```bash
cd PhishGuard

python3 -m venv venv
source venv/bin/activate

pip install -r backend/requirements.txt
```

---

### Step 2: Train the Machine Learning Models

Run the training pipeline to generate the engineered datasets, train both classifiers, perform 5-fold cross-validation comparisons, evaluate on held-out test splits, and export serialized model artifacts:

```bash
python scripts/train_models.py
```

*Output artifacts generated:*
- `ml/models/url_detector.joblib`
- `ml/models/email_detector.joblib`
- `ml/models/metadata.json`
- `ml/reports/url_evaluation.json`
- `ml/reports/email_evaluation.json`
- `ml/reports/model_comparison.json`

---

### Step 3: Run the Automated Test Suite

PhishGuard includes 28 automated tests covering feature extraction, malformed input safety, email NLP normalization, zero-division metric safety, leakage assertion ($X_{\text{train}} \cap X_{\text{test}} = \emptyset$), and all REST API endpoints.

```bash
# Run via unified script:
python scripts/run_tests.py

# Or directly via pytest:
python -m pytest
```

---

### Step 4: Start the FastAPI Backend Server

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- **Backend API:** `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation (Swagger):** `http://127.0.0.1:8000/docs`
- **Alternative Documentation (ReDoc):** `http://127.0.0.1:8000/redoc`

---

### Step 5: Start the React Frontend

Open a second terminal window:

#### Windows (cmd / PowerShell)
```cmd
cd frontend
npm install
npm run dev
```

#### Linux / macOS
```bash
cd frontend
npm install
npm run dev
```

- **Frontend Dashboard:** `http://localhost:5173`

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health status and model readiness |
| `GET` | `/api/models` | Registry of trained model algorithms and versions |
| `POST` | `/api/scan/url` | Analyzes URL string locally; returns verdict & XAI |
| `POST` | `/api/scan/email` | Analyzes email text; returns verdict & influential words |
| `GET` | `/api/metrics` | Returns held-out evaluation reports & confusion matrices |
| `GET` | `/api/history` | Paginated scan history with filtering & search |
| `DELETE` | `/api/history/{scan_id}` | Deletes an individual scan record |
| `DELETE` | `/api/history` | Clears all local history records |

---

## Dataset Provenance & Licenses

- **URL Phishing Dataset:** Sourced and benchmarked against verified PhishTank community feeds (phishing class) and Tranco/Alexa Top 1M domains (legitimate class). License: Open Data Commons / CC0.
- **Email NLP Dataset:** Sourced and benchmarked against Apache SpamAssassin Public Corpus (authentic communication) and Nazario Phishing Archives (phishing class). License: Apache 2.0 / Public Domain.
- **Provenance Documentation:** Full provenance files are recorded at `ml/data/raw/urls_provenance.json` and `ml/data/raw/emails_provenance.json`.

---

## Security & Privacy Guardrails

1. **Safe URL Parsing:** PhishGuard never opens an HTTP/HTTPS socket to a scanned URL, executes remote scripts, or performs live DNS resolutions. Analysis is entirely static.
2. **Zero Email Body Persistence:** In compliance with privacy standards, submitted email bodies are discarded after inference. The SQLite audit log records only a sanitized preview snippet and model verdicts.
3. **Restricted CORS Policy:** The FastAPI backend restricts cross-origin access exclusively to development frontend origins (`http://localhost:5173`).
4. **Probabilistic Disclaimer:** Predictions are statistical indicators. Organizations should maintain defense-in-depth controls including multi-factor authentication (MFA) and DNS filtering.

---

## Troubleshooting

- **"Model artifacts are not loaded" (HTTP 503):** Execute `python scripts/train_models.py` to train and serialize the models.
- **PowerShell Execution Policy Error on npm:** Run using `cmd /c npm run dev` or run PowerShell as Administrator and execute `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **Port Conflict on 8000:** Specify an alternative port: `uvicorn backend.app.main:app --port 8080` and adjust the Vite proxy in `frontend/vite.config.ts`.
