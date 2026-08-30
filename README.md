# InsightForge

## Evidence-Driven KPI Investigation

InsightForge is an evidence-driven business intelligence prototype that investigates significant KPI changes and explains them using verified business data, customer feedback, analytical relationships, and Gemini.

### Core Workflow

**Detect → Analyze → Retrieve Evidence → Rank → Explain → Recommend**

---

## Problem

Traditional dashboards can show that revenue increased or decreased, but they often do not answer:

- What changed?
- Which business metrics moved with the KPI?
- Does customer feedback support the observed movement?
- How strong is the available evidence?
- What should be investigated next?

InsightForge addresses this gap through an automated KPI investigation pipeline.

---

## Solution

For a selected region and period, InsightForge:

1. Calculates monthly revenue.
2. Calculates month-over-month revenue change.
3. Detects significant KPI movements.
4. Identifies the top observed drivers.
5. Calculates historical driver-revenue associations.
6. Retrieves relevant customer feedback.
7. Ranks supporting evidence.
8. Calculates heuristic evidence strength.
9. Sends verified analytical results to Gemini.
10. Generates an explanation, uncertainty statement, and recommended action.

The system explicitly distinguishes **association from causation**.

---

# Key Features

## 1. KPI Change Detection

The current prototype investigates revenue changes of at least **5%**.

Example:

```text
North — June 2025
Revenue change: -23.08%
Investigation triggered

South — June 2025
Revenue change: -0.81%
Investigation not triggered
```

This prevents insignificant changes from unnecessarily entering the investigation pipeline.

---

## 2. Driver Analysis

InsightForge identifies observed business drivers associated with the KPI movement.

Example drivers:

- Product Usage
- Support Resolution Hours
- Renewal Rate

For each driver, the system calculates:

- Previous value
- Current value
- Percentage change
- Historical correlation with revenue
- Directional alignment
- Driver score
- Contribution weight
- Contribution percentage
- Historical observations
- Correlation reliability
- Correlation significance

The driver score is a ranking heuristic based on observed change and historical association.

**It is not a causal score.**

---

## 3. Evidence Retrieval

Customer feedback is searched using terms associated with the observed drivers.

For example:

```text
support_resolution_hours
```

can be represented using related terms such as:

```text
support
resolution
hours
```

Matching feedback is retrieved for the selected investigation.

---

## 4. Evidence Ranking

Retrieved feedback is ranked according to the relevance of driver-related keywords.

This allows InsightForge to prioritize customer feedback that directly supports an observed driver.

---

## 5. Driver-Specific Evidence

Evidence is grouped according to the driver it supports.

Example:

```text
Product Usage
→ Unresolved product issues

Support Resolution Hours
→ Support delays

Renewal Rate
→ No direct qualitative evidence
```

This prevents unrelated feedback from being presented as evidence for a driver.

---

## 6. Evidence Strength

InsightForge provides a qualitative evidence-strength rating:

- Weak
- Moderate
- Strong

The rating considers:

- KPI change
- Number of observed drivers
- Supporting evidence
- Historical observations

It is a **heuristic assessment**, not statistical confidence.

---

## 7. Sparse-History Abstention

InsightForge avoids presenting strong analytical conclusions when historical evidence is insufficient.

When historical observations are below the required threshold:

```text
Abstained: True
Confidence: Low
```

This allows the system to explicitly communicate uncertainty instead of overstating weak historical relationships.

---

## 8. Gemini-Powered Explanation

Gemini receives the verified analytical output and supporting evidence.

The AI is instructed to:

- Use only supplied evidence
- Avoid inventing facts
- Avoid causal claims
- Communicate uncertainty
- Recommend one practical action
- Preserve the distinction between association and causation

The output contains:

- Explanation
- Uncertainty
- Recommended Action

If Gemini is unavailable or the API quota is exceeded, the system provides a structured fallback response instead of crashing.

---

# System Architecture

```text
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    │  Region + Period    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Analysis Pipeline  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       KPI Calculation   Change Detection   Driver Analysis
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence Retrieval  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Evidence Ranking   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence Strength   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Gemini AI Service │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └─────────────────────┘
```

---

# End-to-End Workflow

```text
Select Region + Period
          ↓
Calculate KPI
          ↓
Calculate KPI Change
          ↓
Check 5% Threshold
          ↓
      Significant?
       ↙        ↘
     No          Yes
     ↓            ↓
   Stop     Analyze Drivers
                  ↓
        Rank Observed Drivers
                  ↓
        Retrieve Customer Evidence
                  ↓
             Rank Evidence
                  ↓
        Calculate Evidence Strength
                  ↓
          Check Historical Support
                  ↓
            Build Gemini Prompt
                  ↓
            Generate AI Insight
                  ↓
             Display Results
```

---

# Example Investigation

## North Region — June 2025

Revenue changed from:

```text
May 2025:  ₹130,000
June 2025: ₹100,000
```

Revenue change:

```text
-23.08%
```

### Top Observed Drivers

#### Product Usage

```text
86 → 70
-18.60%
```

#### Support Resolution Hours

```text
12 → 18
+50.00%
```

#### Renewal Rate

```text
93 → 82
-11.83%
```

### Supporting Customer Evidence

Examples include:

- Unresolved product issues
- Longer support ticket resolution
- Slower support responses

InsightForge combines these quantitative movements and qualitative evidence into an evidence-grounded investigation.

---

# Positive KPI Investigation

InsightForge also investigates positive KPI movements using the same evidence-driven workflow.

## North Region — July 2025

Revenue changed from:

```text
June 2025: ₹100,000
July 2025: ₹126,000
```

Revenue change:

```text
+26.00%
```

### Observed Driver Movements

#### Support Resolution Hours

```text
18 → 12
-33.33%
```

#### Product Usage

```text
70 → 84
+20.00%
```

#### Renewal Rate

```text
82 → 91
+10.98%
```

The system applies the same investigation framework to both positive and negative KPI movements.

---

# Evidence Chain

InsightForge exposes the investigation chain from the KPI movement to supporting evidence:

```text
1. KPI Change
       ↓
2. Observed Drivers
       ↓
3. Supporting Evidence
       ↓
4. Evidence Strength
       ↓
5. AI Explanation
       ↓
6. Recommended Action
```

This makes the reasoning process traceable instead of treating the LLM as the source of the analysis.

---

# Analyst / Business Feedback

InsightForge supports analyst/business feedback after an investigation.

Feedback can include:

- Insight rating
- Correction
- Comment

Stored feedback can be retrieved for future investigations involving the same KPI, region, period, and persona.

---

# Security and Entitlements

The backend includes security and entitlement checks to control access to analytical functionality.

The system is designed to ensure that analysis requests are validated before processing.

---

# Reconciliation

InsightForge includes source reconciliation functionality to compare analytical sources and identify inconsistencies before presenting the final investigation.

This supports the principle that AI should explain verified analytical information rather than independently determine the underlying numbers.

---

# Robustness

The prototype handles:

- Positive KPI changes
- Negative KPI changes
- Insignificant KPI changes
- Invalid periods
- Missing customer evidence
- Sparse historical observations
- Gemini API failures
- Gemini quota failures
- Empty Gemini responses
- Invalid Gemini JSON
- Missing Gemini output fields

If Gemini is unavailable, the application returns a structured fallback response instead of crashing.

---

# Testing

The project includes automated tests covering:

- Sparse-history abstention
- Driver contribution
- Data freshness
- Source reconciliation
- Scalability
- Security and entitlements

Run the complete test suite with:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Current validation result:

```text
7 passed
```

---

# Project Structure

```text
InsightForge/
│
├── backend/
│   ├── analysis_pipeline.py
│   ├── main.py
│   ├── feedback.py
│   ├── freshness.py
│   ├── reconciliation.py
│   ├── security.py
│   │
│   ├── analytics/
│   │   ├── anomaly_detection.py
│   │   ├── change_detection.py
│   │   ├── confidence.py
│   │   ├── contribution.py
│   │   ├── driver_analysis.py
│   │   ├── kpi.py
│   │   ├── llm_breakdown.py
│   │   └── llm_telemetry.py
│   │
│   ├── evidence/
│   │   ├── ranking.py
│   │   └── retrieval.py
│   │
│   └── llm/
│       ├── gemini_service.py
│       └── insight_generator.py
│
├── config/
│   └── kpi_contracts.yaml
│
├── data/
│   ├── sales.csv
│   ├── customer_feedback.csv
│   ├── product_usage.csv
│   ├── renewal_data.csv
│   ├── support_tickets.csv
│   ├── insight_feedback.csv
│   └── sparse_history_abstention.csv
│
├── frontend/
│   └── app.py
│
├── tests/
│   ├── test_abstention.py
│   ├── test_contribution.py
│   ├── test_freshness.py
│   ├── test_reconciliation.py
│   ├── test_scalability.py
│   └── test_security_entitlements.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python, FastAPI |
| Data Analysis | Pandas, NumPy |
| Analytical Modeling | Scikit-learn |
| Generative AI | Google Gemini |
| Gemini SDK | google-genai |
| Configuration | python-dotenv |
| Testing | pytest |

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Jayasreemuggu/InsightForge.git
cd InsightForge
```

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell execution policy prevents activation, the environment can still be used directly:

```powershell
.\venv\Scripts\python.exe
```

## 3. Install Dependencies

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

# Gemini API Configuration

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

The `.env` file must **never** be committed to GitHub.

The repository ignores:

```text
.env
venv/
__pycache__/
```

---

# Running the Application

From the project root:

```powershell
.\venv\Scripts\python.exe -m streamlit run frontend\app.py
```

Open:

```text
http://localhost:8501
```

Then select:

```text
Region
Period
```

and click:

```text
Analyze KPI
```

---

# FastAPI Backend

The project also contains a FastAPI backend.

Run:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Health endpoint:

```text
GET /health
```

---

# Analytical Limitations

InsightForge is an analytical investigation prototype.

It is **not a causal inference system**.

### Correlation Is Not Causation

A driver moving alongside revenue does not prove that it caused the revenue movement.

### Limited Historical Data

Historical correlations depend on the available observations and should be interpreted cautiously.

### Heuristic Evidence Strength

The evidence-strength label is a heuristic and should not be interpreted as statistical confidence.

### Missing Qualitative Evidence

Some drivers may not have directly matching customer feedback.

### External Factors

Market conditions, competitors, pricing, seasonality, and other unobserved variables may also affect revenue.

### Human Review

Human review is required before making business decisions.

---

# Design Principle

> **AI should explain verified evidence, not invent the evidence.**

Numerical analysis is performed programmatically.

Customer evidence is retrieved from the supplied datasets.

Gemini synthesizes these verified inputs into a business explanation.

This architecture keeps the analytical computation separate from the generative explanation layer.

---

# Future Improvements

Potential improvements include:

- Larger real-world datasets
- Additional KPIs
- Statistical significance testing
- Time-series forecasting
- Causal inference
- Semantic/vector-based evidence retrieval
- More advanced evidence scoring
- Automated report generation
- Real-time business data integration
- Monitoring and alerting
- More advanced analyst feedback learning

---

# Prototype Status

**Status: Prototype — Round 2**

InsightForge demonstrates an end-to-end evidence-driven KPI investigation workflow:

```text
KPI Change Detection
        ↓
Driver Analysis
        ↓
Evidence Retrieval
        ↓
Evidence Ranking
        ↓
Evidence Strength
        ↓
Historical Reliability
        ↓
AI Explanation
        ↓
Recommended Action
```

The prototype has been validated with an automated test suite.

```text
7 tests passed
```

---

# Repository

GitHub:

https://github.com/Jayasreemuggu/InsightForge

---

# Key Takeaway

InsightForge is designed around a simple principle:

**Detect the change → identify observed drivers → retrieve supporting evidence → assess evidence strength → explain with AI → communicate uncertainty → recommend an action.**

The system does not ask the LLM to discover or invent the underlying business facts. The analytical pipeline produces the verified inputs first, and Gemini is used primarily for evidence-grounded explanation.
