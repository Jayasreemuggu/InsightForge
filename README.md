# InsightForge

## Evidence-Driven KPI Investigation

InsightForge is an evidence-driven business intelligence prototype that investigates significant KPI changes and explains them using verified business data, customer feedback, analytical relationships, and Gemini.

### Core Workflow

**Detect → Analyze → Retrieve Evidence → Rank → Reconcile → Explain → Recommend**

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
4. Identifies observed drivers.
5. Calculates historical driver-revenue associations.
6. Evaluates directional alignment and driver contribution.
7. Retrieves relevant customer feedback.
8. Ranks supporting evidence.
9. Calculates heuristic evidence strength.
10. Performs source reconciliation.
11. Handles sparse historical data through abstention.
12. Sends verified analytical results to Gemini.
13. Generates an explanation, uncertainty statement, and recommended action.

The system explicitly distinguishes **association from causation**.

---

# Key Features

## KPI Change Detection

The current prototype investigates revenue changes of at least **5%**.

Example:

```text
North — June 2025
Revenue change: -23.08%
Investigation triggered

South — June 2025
Revenue change: -0.81%
Investigation not triggered

This prevents insignificant KPI movements from unnecessarily entering the investigation pipeline.

Driver Analysis

InsightForge identifies observed business drivers associated with the KPI movement.

For each driver, the system calculates:

Previous value
Current value
Percentage change
Historical correlation with revenue
Directional alignment
Driver score
Contribution weight
Contribution percentage
Historical observations
Correlation reliability
Correlation significance

The driver score is a ranking heuristic based on observed movement and historical association.

It is not a causal score.

Evidence Retrieval

Customer feedback is searched using terms associated with the observed drivers.

For example:

support_resolution_hours

can be represented using related terms such as:

support
resolution
hours

Matching feedback is retrieved for the selected investigation.

Evidence Ranking

Retrieved customer feedback is ranked according to its relevance to the observed drivers.

This allows InsightForge to prioritize evidence that directly supports an observed business signal.

Evidence is grouped according to the driver it supports.

Example:

Product Usage
→ Unresolved product issues

Support Resolution Hours
→ Support delays

Renewal Rate
→ No direct qualitative evidence

This reduces the risk of presenting unrelated feedback as evidence for a particular driver.

Evidence Strength

InsightForge provides a qualitative evidence-strength rating:

Weak
Moderate
Strong

The rating considers available:

KPI movement
Number of observed drivers
Supporting evidence
Historical observations

The resulting rating is a heuristic assessment, not statistical confidence.

Sparse-History Abstention

InsightForge includes a safeguard for insufficient historical data.

When fewer than three historical observations are available, the system abstains from presenting a strong historical interpretation.

The result is:

abstained: True
confidence: Low

This prevents limited historical data from being presented as strong analytical evidence.

Source Reconciliation

InsightForge includes source reconciliation functionality to compare and validate information from available business data sources.

This supports the principle that AI explanations should be based on verified analytical inputs rather than unsupported claims.

Gemini-Powered Explanation

Gemini receives the verified analytical output and supporting evidence.

The AI is instructed to:

Use only supplied evidence
Avoid inventing facts
Avoid unsupported causal claims
Communicate uncertainty
Recommend one practical action
Preserve the distinction between association and causation

The output contains:

Explanation
Uncertainty
Recommended Action
Gemini Failure Handling

If Gemini is unavailable because of API quota limitations, API errors, empty responses, invalid JSON, or missing output fields, the application returns a structured fallback response instead of crashing.

The verified analytical results remain available.

System Architecture
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    │ Region + Period     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Analysis Pipeline   │
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
                    │ Evidence Ranking    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence Strength   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Source Reconciliation│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Gemini AI Service   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └─────────────────────┘
End-to-End Workflow
Select Region + Period
          ↓
Calculate KPI
          ↓
Calculate KPI Change
          ↓
Check 5% Threshold
          ↓
       Significant?
       ↙          ↘
     No            Yes
     ↓              ↓
    Stop      Analyze Drivers
                    ↓
             Rank Drivers
                    ↓
          Retrieve Customer Evidence
                    ↓
             Rank Evidence
                    ↓
        Calculate Evidence Strength
                    ↓
          Reconcile Sources
                    ↓
          Check Historical Sufficiency
                    ↓
          Build Gemini Prompt
                    ↓
          Generate AI Insight
                    ↓
             Display Results
Example Investigation
Negative KPI Movement
North Region — June 2025

Revenue changed from:

May 2025:   ₹130,000
June 2025:  ₹100,000

Revenue change:

-23.08%
Observed Drivers
Driver	Previous	Current	Change
Product Usage	86	70	-18.60%
Support Resolution Hours	12	18	+50.00%
Renewal Rate	93	82	-11.83%

Supporting customer feedback includes observations about:

Unresolved product issues
Longer support ticket resolution
Slower support responses

InsightForge combines these quantitative movements and qualitative evidence into an evidence-grounded investigation.

Positive KPI Investigation
North Region — July 2025

Revenue changed from:

June 2025:  ₹100,000
July 2025:  ₹126,000

Revenue change:

+26.00%

Observed driver movements:

Driver	Previous	Current	Change
Support Resolution Hours	18	12	-33.33%
Product Usage	70	84	+20.00%
Renewal Rate	82	91	+10.98%

The system investigates positive KPI movements using the same evidence-driven workflow.

Dashboard Output

The Streamlit dashboard presents:

KPI overview
Revenue change
Investigation summary
Revenue trend
Top observed drivers
Driver change comparison
Regional comparison
Driver details
Investigation evidence chain
Supporting customer evidence
AI explanation
Uncertainty statement
Recommended action
Analyst/business feedback
Project Structure
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
│   ├── insight_feedback.csv
│   ├── product_usage.csv
│   ├── renewal_data.csv
│   ├── support_tickets.csv
│   ├── sparse_history_test.csv
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
Technology Stack
Component	Technology
Frontend	Streamlit
Backend	Python, FastAPI
Data Analysis	Pandas, NumPy
Analytical Modeling	Scikit-learn
Generative AI	Google Gemini
Gemini SDK	google-genai
Configuration	python-dotenv
Testing	pytest
Version Control	Git, GitHub
Installation
1. Clone the Repository
git clone https://github.com/Jayasreemuggu/InsightForge.git
cd InsightForge
2. Create Virtual Environment
python -m venv venv

Activate:

.\venv\Scripts\Activate.ps1

If PowerShell execution policy prevents activation, use the virtual environment Python executable directly:

.\venv\Scripts\python.exe
3. Install Dependencies
pip install -r requirements.txt
Gemini API Configuration

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

The .env file must never be committed to GitHub.

The repository ignores:

.env
venv/
__pycache__/
Running the Application

From the project root:

.\venv\Scripts\python.exe -m streamlit run frontend\app.py

Open:

http://localhost:8501

Select:

Region
Period

Then run the KPI investigation.

FastAPI Backend

The project also contains a FastAPI backend.

Run:

.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload

Health endpoint:

GET /health
Testing

InsightForge includes automated tests covering important analytical and robustness components.

Run the complete test suite:

.\venv\Scripts\python.exe -m pytest -q

Current validation result:

7 passed

The test suite covers:

Sparse-history abstention
Driver contribution
Data freshness
Source reconciliation
Scalability
Security and entitlements
Robustness

The prototype handles:

Positive KPI changes
Negative KPI changes
Insignificant KPI changes
Invalid periods
Missing customer evidence
Sparse historical observations
Gemini API failures
Empty Gemini responses
Invalid Gemini JSON
Missing Gemini output fields

If Gemini is unavailable, the application returns a structured fallback response instead of crashing.

Analytical Limitations

InsightForge is an analytical investigation prototype.

It is not a causal inference system.

Correlation Is Not Causation

A driver moving alongside revenue does not prove that it caused the revenue movement.

Limited Historical Data

Historical correlations depend on the available observations and should be interpreted cautiously.

Heuristic Evidence Strength

The evidence-strength label is a heuristic and should not be interpreted as statistical confidence.

Missing Qualitative Evidence

Some drivers may not have directly matching customer feedback.

External Factors

Market conditions, competitors, pricing, seasonality, and other unobserved variables may also affect revenue.

Human review is required before making business decisions.

Design Principle

AI should explain verified evidence, not invent the evidence.

Numerical analysis is performed programmatically.

Customer evidence is retrieved from the supplied datasets.

Gemini synthesizes these verified inputs into a business explanation while being instructed to preserve uncertainty and avoid unsupported causal claims.

Future Improvements

Potential improvements include:

Larger real-world datasets
Additional KPIs
Statistical significance testing
Time-series forecasting
Causal inference
Semantic/vector-based evidence retrieval
More advanced evidence scoring
Automated report generation
Real-time business data integration
Monitoring and alerting
Repository

Public GitHub repository:

https://github.com/Jayasreemuggu/InsightForge

Status

Prototype — Round 2

InsightForge demonstrates an end-to-end evidence-driven KPI investigation workflow from KPI change detection through driver analysis, evidence retrieval, evidence ranking, source reconciliation, confidence assessment, sparse-history safeguards, and AI-generated business insight.


### What you should do now

Since you already pushed the code and **7 tests are passing**, don't touch the Python code.

Replace your current `README.md` with the above, then run:

```powershell
git add README.md
git commit -m "Improve GitHub documentation"
git push

Then verify:

git status

You should ideally see:

Your branch is up to date with 'origin/master'.
