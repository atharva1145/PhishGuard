# PhishGuard System Architecture

## Component Overview

```
+--------------------------------------------------------------------------+
|                       React + TypeScript Frontend                        |
|                                                                          |
|  [Overview]    [URL Scanner]    [Email Scanner]   [Evaluation]  [History]|
|                                                                          |
|       Recharts Analytics  *  Tailwind CSS Dark Theme  *  Lucide Icons     |
+------------------------------------+-------------------------------------+
                                     |  REST API (JSON over HTTP)
                                     v
+------------------------------------+-------------------------------------+
|                          FastAPI Backend                                 |
|                                                                          |
|  /api/health      /api/scan/url    /api/scan/email                       |
|  /api/models      /api/metrics     /api/history                          |
|                                                                          |
|      Pydantic Request Validation  *  CORS Security  *  SQLite Audit      |
+-----------------+-----------------------------------+--------------------+
                  |                                   |
                  v                                   v
+-----------------+---------------+   +---------------+--------------------+
|     URL Analysis Service        |   |     Email Analysis Service         |
|                                 |   |                                    |
| * Local Lexical Parser          |   | * Text Normalizer & HTML Strip     |
| * 24-Feature Vector Extractor   |   | * TF-IDF N-Gram Vectorizer         |
| * StandardScaler Pipeline       |   | * Logistic Regression Classifier   |
| * Log-Odds XAI Attribution      |   | * Influential Vocabulary Terms     |
| * Heuristic Indicator Engine    |   | * Psychological Cue Detector       |
+-----------------+---------------+   +---------------+--------------------+
                  |                                   |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |   Joblib Serialized Model Store   |
                  |                                   |
                  | * url_detector.joblib             |
                  | * email_detector.joblib           |
                  | * metadata.json                   |
                  | * Evaluation JSON Reports         |
                  +-----------------------------------+
```

## Security & Privacy Guardrails

1. **Local Analysis Only:** No URL fetching, socket connections to scanned hosts, or remote DNS queries.
2. **Zero Raw Body Logging:** SQLite database logs only store sanitized preview snippets and model verdicts; full email bodies are never persisted.
3. **Restricted CORS Policy:** Development frontend origins (`http://localhost:5173`) are explicitly whitelisted.
4. **Deterministic Heuristics:** Explanations combine exact linear log-odds mathematics ($w_i \cdot x_i$) with deterministic rule engines; no hallucinations or fabricated predictions.
