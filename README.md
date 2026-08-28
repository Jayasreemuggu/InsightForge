# InsightForge

## Evidence-Driven KPI Investigation

InsightForge is an evidence-driven business intelligence prototype that investigates significant KPI changes and explains them using verified business data, customer feedback, analytical relationships, and Gemini.

The core workflow is:

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

## Key Features

### KPI Change Detection

The current prototype investigates revenue changes of at least **5%**.

Example:

```text
North — June 2025
Revenue change: -23.08%
Investigation triggered
South — June 2025
Revenue change: -0.81%
Investigation not triggered

This prevents insignificant changes from unnecessarily entering the investigation pipeline.

Driver Analysis

Current business drivers:

Product Usage
Support Resolution Hours
Renewal Rate

For each driver, the system calculates:

Previous value
Current value
Percentage change
Historical correlation with revenue
Directional alignment
Driver score

The driver score is a ranking heuristic based on change magnitude and historical association.

It is not a causal score.

Evidence Retrieval

Customer feedback is searched using terms associated with the observed drivers.

For example:

support_resolution_hours

can be represented using related terms such as:

support
resolution
hours

Matching feedback is retrieved for the selected region and period.

Evidence Ranking

Retrieved feedback is ranked according to the relevance of driver-related keywords.

This allows InsightForge to prioritize customer feedback that directly supports an observed driver.

Driver-Specific Evidence

Evidence is grouped according to the driver it supports.

Example:

Product Usage
→ Unresolved product issues

Support Resolution Hours
→ Support delays

Renewal Rate
→ No direct qualitative evidence

This prevents unrelated feedback from being presented as evidence for a driver.

Evidence Strength

InsightForge provides a qualitative evidence-strength rating:

Weak
Moderate
Strong

The rating considers the available:

KPI change
Number of observed drivers
Supporting evidence

It is a heuristic assessment, not statistical confidence.

Gemini-Powered Explanation

Gemini receives the verified analytical output and supporting evidence.

The AI is instructed to:

Use only supplied evidence
Avoid inventing facts
Avoid causal claims
Communicate uncertainty
Recommend one practical action
Preserve the distinction between association and causation

The output contains:

Explanation
Uncertainty
Recommended Action
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
Stop        Analyze Drivers
                  ↓
          Rank Observed Drivers
                  ↓
          Retrieve Customer Evidence
                  ↓
             Rank Evidence
                  ↓
        Calculate Evidence Strength
                  ↓
          Build Gemini Prompt
                  ↓
          Generate AI Insight
                  ↓
             Display Results
Example Investigation
North Region — June 2025

Revenue changed from:

May 2025:  ₹130,000
June 2025: ₹100,000

Revenue change:

-23.08%

Top observed drivers:

Product Usage
86 → 70
-18.60%

Support Resolution Hours
12 → 18
+50.00%

Renewal Rate
93 → 82
-11.83%

Supporting customer feedback includes observations about:

Unresolved product issues
Longer support ticket resolution
Slower support responses

InsightForge combines these quantitative movements and qualitative evidence into an evidence-grounded AI explanation.

Positive KPI Investigation
North Region — July 2025

Revenue changed from:

June 2025: ₹100,000
July 2025: ₹126,000

Revenue change:

+26.00%

Observed driver movements:

Support Resolution Hours
18 → 12
-33.33%

Product Usage
70 → 84
+20.00%

Renewal Rate
82 → 91
+10.98%

The system investigates positive KPI movements using the same evidence-driven workflow.

Project Structure
InsightForge/
│
├── backend/
│   ├── analysis_pipeline.py
│   ├── main.py
│   │
│   ├── analytics/
│   │   ├── anomaly_detection.py
│   │   ├── change_detection.py
│   │   ├── confidence.py
│   │   ├── driver_analysis.py
│   │   └── kpi.py
│   │
│   ├── evidence/
│   │   ├── ranking.py
│   │   └── retrieval.py
│   │
│   └── llm/
│       ├── gemini_service.py
│       └── insight_generator.py
│
├── data/
│   ├── sales.csv
│   └── customer_feedback.csv
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── .gitignore
├── README.md
├── InsightForge_IITIndore.pdf
└── InsightForge_IITIndore.pptx
Technology Stack
Component	Technology
Frontend	Streamlit
Backend	Python, FastAPI
Data Analysis	Pandas, NumPy
Analytical Modeling	Scikit-learn
Generative AI	Google Gemini
Gemini SDK	google-genai
Configuration	python-dotenv
Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd InsightForge
2. Create virtual environment

Windows:

python -m venv venv

Activate:

.\venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
Gemini API Configuration

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

The .env file must never be committed to GitHub.

The repository ignores:

.env
venv/
__pycache__/
InsightForge_IITIndore.mp4
Running the Application

From the project root:

.\venv\Scripts\python.exe -m streamlit run frontend\app.py

Open:

http://localhost:8501

Select:

Region
Period

and click:

Analyze KPI
FastAPI Backend

The project also contains a FastAPI backend.

Run:

.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload

Health endpoint:

GET /health
Robustness

The prototype handles:

Positive KPI changes
Negative KPI changes
Insignificant KPI changes
Invalid periods
Missing customer evidence
Gemini API failures
Empty Gemini responses
Invalid Gemini JSON
Missing Gemini output fields

If Gemini is unavailable, the application returns a structured fallback response instead of crashing.

Analytical Limitations

InsightForge is an analytical investigation prototype.

It is not a causal inference system.

Correlation is not causation

A driver moving alongside revenue does not prove that it caused the revenue movement.

Limited historical data

Historical correlations depend on the available observations and should be interpreted cautiously.

Heuristic evidence strength

The evidence-strength label is a heuristic and should not be interpreted as statistical confidence.

Missing qualitative evidence

Some drivers may not have directly matching customer feedback.

External factors

Market conditions, competitors, pricing, seasonality, and other unobserved variables may also affect revenue.

Human review is required before making business decisions.

Design Principle

AI should explain verified evidence, not invent the evidence.

Numerical analysis is performed programmatically.

Customer evidence is retrieved from the supplied dataset.

Gemini synthesizes these verified inputs into a business explanation.

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
Status

Prototype — Round 2

InsightForge demonstrates an end-to-end evidence-driven KPI investigation workflow from KPI change detection through driver analysis, evidence retrieval, and AI-generated business insight.


### Then save

Press:

**Ctrl + S**

Close Notepad.

Then run:

```powershell
git add README.md
git commit -m "Improve project documentation"
git status