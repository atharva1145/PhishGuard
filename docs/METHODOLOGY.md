# PhishGuard Scientific Methodology & Machine Learning Architecture

## 1. Objective & Scope

PhishGuard is an explainable AI phishing detection platform designed to detect malicious URLs and deceptive emails through local feature engineering, supervised scikit-learn models, and deterministic heuristic synthesis.

### What PhishGuard Does
- **URL Lexical & Structural Profiling:** Parses string representations without making external HTTP requests or DNS resolutions.
- **Natural Language Email Classification:** Vectorizes subject and body text to detect social engineering themes (urgency, credential harvesting, wire fraud).
- **Exact Linear Explainability (XAI):** Calculates log-odds feature contributions ($w_i \cdot x_i$) for linear models and identifies influential vocabulary tokens.
- **Empirical Metric Reporting:** Evaluates precision, recall, F1, false-positive rate (FPR), and false-negative rate (FNR) on held-out test splits.

### What PhishGuard Cannot Determine
- **Sender Identity Authentication:** Text-only email analysis cannot verify SPF, DKIM, or DMARC cryptographic signatures without raw MIME transport headers.
- **Dynamic Web Content:** PhishGuard does not execute JavaScript, inspect DOM elements, or download remote payloads.
- **Absolute Ground Truth:** Predictions are probabilistic estimates; benign messages may contain urgent phrasing and advanced phishing messages can appear legitimate.

---

## 2. URL Feature Engineering Taxonomy

URLs are parsed locally via Python's standard library `urllib.parse` and regex. Twenty-four numerical features are computed:

| Feature Name | Type | Cybersecurity Significance |
|---|---|---|
| `url_length` | Float | Long URLs frequently obscure attack payloads or forward parameters |
| `hostname_length` | Float | Disproportionately long hostnames correlate with subdomain spoofing |
| `path_length` | Float | Deeply nested paths disguise attack landing scripts |
| `query_length` | Float | Extensive query strings often pack stolen session parameters |
| `num_dots` | Float | Excessive dot count indicates obfuscated domain nesting |
| `num_dots_hostname` | Float | Reflects subdomain hierarchy |
| `num_subdomains` | Float | Subdomain stacking prepends trusted brands (e.g. `paypal.com.auth.attacker.com`) |
| `num_hyphens` | Float | High frequency of hyphens in impersonated brand names |
| `num_hyphens_hostname` | Float | Brand keyword hyphenation (e.g. `microsoft-security-update`) |
| `num_digits` | Float | Randomized numeric IDs in attack landing pages |
| `num_digits_hostname` | Float | Hostnames with high numeric counts indicate disposable infrastructure |
| `digit_ratio` | Float | Fraction of digits across the entire URL string |
| `num_special_chars` | Float | Counts of `@`, `?`, `=`, `&`, `_`, `%`, `+`, `~`, `#` |
| `has_ip_address` | Binary | Direct IPv4/IPv6 hostname bypassing registrar reputation lists |
| `has_punycode` | Binary | Internationalized domain names (`xn--`) used for homograph attacks |
| `is_https` | Binary | Transport layer encryption (Note: Many modern phishing sites also obtain free TLS) |
| `has_at_symbol` | Binary | `@` symbol directs browsers to treat leading text as userinfo, obscuring the true host |
| `has_suspicious_port` | Binary | Web services hosted on non-standard ports (e.g., :8080, :8888) |
| `num_percent_encoded` | Float | Excessive percent-encoding (%xx) designed to evade regex filters |
| `has_shortener` | Binary | Shorteners (bit.ly, tinyurl.com) concealing the destination domain |
| `has_suspicious_tld` | Binary | Top-level domains with statistically high abuse rates (.xyz, .top, .buzz, etc.) |
| `num_sensitive_keywords` | Float | Presence of target words (login, verify, secure, banking, credentials, etc.) |
| `has_prefix_suffix_in_host`| Binary | Domain contains hyphens separating brand tokens |
| `is_valid_url` | Binary | Conforms to RFC URL structure standards |

---

## 3. Email NLP Preprocessing Pipeline

1. **Sanitization:** Strips raw HTML tags safely without rendering or executing scripts.
2. **Entity Normalization:** Converts raw URLs to `__URL__`, email addresses to `__EMAIL__`, currency values to `__MONEY__`, and phone numbers to `__PHONE__`.
3. **TF-IDF Vectorization:**
   - Sublinear term-frequency scaling ($1 + \log(\text{tf})$)
   - $N$-gram range: $(1, 2)$ (capturing bigrams such as "account suspended", "click here", "wire transfer")
   - Vocabulary bound: Max 5,000 features
   - English stop-word removal
4. **Classification:** L2-regularized Logistic Regression with balanced class weights.

---

## 4. Train/Test Separation & Leakage Prevention

To avoid overly optimistic performance estimates:
1. **Deduplication:** URLs and email bodies are normalized and deduplicated prior to partitioning.
2. **Stratified Split:** 80% training / 20% test partition with fixed seed (42).
3. **Strict Parameter Fitting:** Scalers (`StandardScaler`) and TF-IDF vectorizers are fitted **strictly on training partitions**; test sets are transformed without fitting.
4. **Leakage Assertion:** Automated unit tests confirm $X_{\text{train}} \cap X_{\text{test}} = \emptyset$.
5. **Cross-Validation:** 5-fold stratified cross-validation on the training set is used for model comparison; the held-out test split is evaluated only once on the selected final model.

---

## 5. Mathematical Metrics & Definitions

For positive class = 1 (Phishing):
- **Accuracy:** $(TP + TN) / (TP + TN + FP + FN)$
- **Precision:** $TP / (TP + FP)$
- **Recall (TPR):** $TP / (TP + FN)$
- **F1-Score:** $2 \times (\text{Precision} \times \text{Recall}) / (\text{Precision} + \text{Recall})$
- **False-Positive Rate (FPR):** $FP / (FP + TN)$
- **False-Negative Rate (FNR):** $FN / (FN + TP)$

*Zero-Division Protection:* When a denominator is zero, PhishGuard reports the metric as unavailable (`null`) rather than failing or outputting inaccurate numbers.
