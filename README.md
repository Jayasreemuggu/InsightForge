\# InsightForge



\## Evidence-Driven KPI Investigation



InsightForge is an evidence-driven business intelligence prototype that helps investigate significant KPI changes.



Instead of simply reporting that a KPI increased or decreased, InsightForge follows an investigation workflow:



\*\*Detect → Analyze Drivers → Retrieve Evidence → Rank Evidence → Explain → Recommend\*\*



The system combines structured business metrics, historical driver relationships, customer feedback, and Gemini-powered natural-language reasoning to produce an evidence-grounded investigation.



\---



\## Problem



Business dashboards can show that revenue or another KPI has changed, but they often do not explain:



\- Why the KPI changed

\- Which business metrics moved alongside it

\- Whether customer feedback supports those observations

\- How strong the available evidence is

\- What should be investigated next



InsightForge addresses this gap by creating an automated investigation pipeline around KPI changes.



\---



\## Solution



For a selected region and period, InsightForge:



1\. Calculates monthly revenue.

2\. Calculates month-over-month revenue change.

3\. Detects significant KPI movements using an investigation threshold.

4\. Identifies the top observed drivers.

5\. Measures historical association between drivers and revenue.

6\. Retrieves relevant customer feedback.

7\. Ranks supporting evidence.

8\. Calculates a heuristic evidence-strength score.

9\. Sends only the verified analytical results and supporting evidence to Gemini.

10\. Generates:

&#x20;  - Evidence-grounded explanation

&#x20;  - Uncertainty and limitations

&#x20;  - One recommended next action



The system explicitly distinguishes \*\*association from causation\*\*.



\---



\## Key Features



\### 1. KPI Change Detection



Revenue is monitored on a monthly basis.



The current prototype investigates changes of at least:



```text

5%



Examples:



North, June 2025

Revenue change: -23.08%

→ Investigation triggered



North, July 2025

Revenue change: +26.00%

→ Investigation triggered



South, June 2025

Revenue change: -0.81%

→ No investigation triggered

2\. Driver Analysis



The system analyzes business metrics that move alongside revenue.



Current drivers include:



Product Usage

Support Resolution Hours

Renewal Rate



For each driver, InsightForge calculates:



Previous value

Current value

Percentage change

Historical correlation with revenue

Directional alignment

Driver score



The driver score is a heuristic based on observed change magnitude and historical association.



driver\_score =

&#x20;   abs(percentage\_change) × abs(correlation)



This is used for ranking observed drivers and is not a causal measure.



3\. Evidence Retrieval



Customer feedback is searched using terms associated with the observed drivers.



For example:



support\_resolution\_hours



is converted into searchable terms such as:



support

resolution

hours



Matching feedback is retrieved for the selected region and period.



4\. Evidence Ranking



Retrieved feedback is ranked based on keyword matching.



Evidence containing more relevant driver terms receives a higher evidence score.



This allows InsightForge to distinguish between:



Relevant supporting feedback



and:



Unrelated feedback

5\. Driver-Specific Evidence



Evidence is grouped according to the driver it supports.



Example:



Product Usage

→ Unresolved product issues



Support Resolution Hours

→ Support delays



Renewal Rate

→ No direct qualitative evidence



This prevents the system from treating all customer feedback as evidence for every driver.



6\. Evidence Strength



InsightForge produces a qualitative evidence-strength label:



Weak

Moderate

Strong



The score considers:



Magnitude of KPI change

Number of observed drivers

Amount of supporting evidence

Drivers with qualitative evidence



This is a heuristic assessment, not statistical confidence.



7\. Gemini-Powered Explanation



Gemini receives the verified analytical output rather than performing the numerical analysis itself.



The AI receives:



KPI change

Driver changes

Historical associations

Directional alignment

Driver scores

Supporting customer evidence

Evidence strength



The AI is instructed to:



Avoid causal claims

Use only supplied evidence

Communicate uncertainty

Avoid inventing facts

Recommend one practical action



The generated output contains:



Explanation

Uncertainty

Recommended Action

System Architecture

&#x20;                   ┌─────────────────────┐

&#x20;                   │    Streamlit UI     │

&#x20;                   │ Region + Period     │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Analysis Pipeline   │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;             ┌────────────────┼────────────────┐

&#x20;             │                │                │

&#x20;             ▼                ▼                ▼

&#x20;      KPI Calculation   Change Detection   Driver Analysis

&#x20;             │                │                │

&#x20;             └────────────────┼────────────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Evidence Retrieval  │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Evidence Ranking    │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Confidence /        │

&#x20;                   │ Evidence Strength   │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Gemini AI Service   │

&#x20;                   │ Explanation         │

&#x20;                   │ Uncertainty         │

&#x20;                   │ Recommendation      │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Streamlit Dashboard │

&#x20;                   └─────────────────────┘

End-to-End Workflow

User selects Region + Period

&#x20;            ↓

Calculate monthly revenue

&#x20;            ↓

Calculate percentage change

&#x20;            ↓

Check investigation threshold

&#x20;            ↓

If insignificant → Stop

&#x20;            ↓

Analyze observed drivers

&#x20;            ↓

Calculate historical associations

&#x20;            ↓

Rank top drivers

&#x20;            ↓

Retrieve customer feedback

&#x20;            ↓

Rank supporting evidence

&#x20;            ↓

Calculate evidence strength

&#x20;            ↓

Build evidence-grounded AI prompt

&#x20;            ↓

Gemini generates structured insight

&#x20;            ↓

Display results

Example Investigation

North Region — June 2025



The prototype detects:



Revenue:

100,000



Previous month:

130,000



Change:

\-23.08%



Top observed drivers:



Product Usage

86 → 70

\-18.60%



Support Resolution Hours

12 → 18

+50.00%



Renewal Rate

93 → 82

\-11.83%



Supporting evidence includes customer feedback about:



Unresolved product issues

Longer support ticket resolution

Slower support responses



The system therefore produces an evidence-grounded explanation while explicitly stating that these relationships represent associations rather than proven causal effects.



Positive KPI Investigation

North Region — July 2025



The prototype also handles positive KPI changes.



Revenue:

126,000



Previous month:

100,000



Change:

+26.00%



Observed driver movements include:



Support Resolution Hours

18 → 12

\-33.33%



Product Usage

70 → 84

+20.00%



Renewal Rate

82 → 91

+10.98%



The system identifies these movements as directionally associated with the revenue increase and incorporates the available customer feedback.



Handling Insignificant Changes



Not every KPI movement triggers an AI investigation.



Example:



South Region — June 2025



Revenue change:

\-0.81%



Because the change is below the 5% investigation threshold, InsightForge returns:



No significant KPI change detected.



This prevents unnecessary downstream analysis and AI calls.



Project Structure

InsightForge/

│

├── backend/

│   ├── analysis\_pipeline.py

│   ├── main.py

│   │

│   ├── analytics/

│   │   ├── anomaly\_detection.py

│   │   ├── change\_detection.py

│   │   ├── confidence.py

│   │   ├── driver\_analysis.py

│   │   └── kpi.py

│   │

│   ├── evidence/

│   │   ├── ranking.py

│   │   └── retrieval.py

│   │

│   └── llm/

│       ├── gemini\_service.py

│       └── insight\_generator.py

│

├── data/

│   ├── sales.csv

│   └── customer\_feedback.csv

│

├── frontend/

│   └── app.py

│

├── requirements.txt

├── .gitignore

├── InsightForge\_IITIndore.pdf

└── InsightForge\_IITIndore.pptx

Technology Stack

Frontend

Streamlit

Backend

Python

FastAPI

Data Analysis

Pandas

NumPy

Scikit-learn

AI

Google Gemini

google-genai

Configuration

python-dotenv

Installation

1\. Clone the repository

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd InsightForge

2\. Create a virtual environment



Windows:



python -m venv venv



Activate it:



.\\venv\\Scripts\\Activate.ps1



If PowerShell blocks script execution, the application can also be run directly through:



.\\venv\\Scripts\\python.exe

3\. Install dependencies

pip install -r requirements.txt

Gemini API Configuration



Create a .env file in the project root:



GEMINI\_API\_KEY=your\_api\_key\_here



Do not commit .env to GitHub.



The repository already ignores:



.env

venv/

\_\_pycache\_\_/

InsightForge\_IITIndore.mp4

Running the Application



From the project root:



.\\venv\\Scripts\\python.exe -m streamlit run frontend\\app.py



The application will be available at:



http://localhost:8501



Select:



Region

Period



and click:



Analyze KPI

API



A minimal FastAPI backend is also included.



Run:



.\\venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload



Health endpoint:



GET /health



Expected response:



{

&#x20; "status": "healthy"

}

Robustness



The prototype has been tested for:



Positive KPI changes

Negative KPI changes

Insignificant KPI changes

Invalid periods

Missing customer evidence

Gemini API failures

Invalid Gemini responses

Empty Gemini responses

Missing fields in Gemini JSON output



When Gemini is unavailable, InsightForge returns a structured fallback response instead of crashing the application.



Important Analytical Limitations



InsightForge is an analytical investigation prototype, not a causal inference system.



Correlation is not causation



A driver moving alongside revenue does not prove that it caused the revenue change.



Small historical dataset



Historical correlations are calculated using the available pre-period observations. With a small number of observations, correlation estimates should be interpreted cautiously.



Heuristic evidence strength



The evidence-strength label is a heuristic based on available KPI movement, drivers, and supporting evidence. It is not statistical confidence.



Incomplete qualitative evidence



Some drivers may not have directly matching customer feedback.



External factors



Market conditions, competitors, pricing changes, seasonality, operational changes, and other variables not represented in the dataset may affect revenue.



Human review is therefore required before making business decisions.



Design Principle



InsightForge follows a simple principle:



AI should explain verified evidence, not invent the evidence.



The numerical analysis is performed programmatically.



The evidence is retrieved from the supplied dataset.



Gemini is used to synthesize these verified inputs into an understandable business explanation.



Future Improvements



Potential future improvements include:



Larger real-world datasets

More KPI types

Statistical significance testing

Time-series forecasting

Causal inference methods

Semantic/vector-based evidence retrieval

More sophisticated evidence scoring

Automated report generation

Role-based dashboards

Real-time business data integration

Monitoring and alerting

Status



Prototype — Round 2



The current prototype demonstrates the complete investigation workflow from KPI detection to evidence-backed AI explanation.





Save and close Notepad.



Then run:



```powershell

git add README.md

git commit -m "Add project documentation"



Finally:



git status



We want:



nothing to commit, working tree clean

One important correction before submission



I deliberately did not claim this is a causal/ML prediction system. Your current implementation doesn't justify that claim. It is stronger and more defensible to present it as an evidence-driven KPI investigation system using analytical heuristics and LLM reasoning.



After the README commit, our next job is GitHub preparation + repository presentation. That includes the repository name/description, README screenshots, demo-video strategy, and checking whether the current code has anything that would look weak to the judges.



wait i ran readme opened it now what to paste in it



Yes. You are in the README.md file opened in Notepad.



Delete anything currently inside it, then paste this entire content:



\# InsightForge



\## Evidence-Driven KPI Investigation



InsightForge is an evidence-driven business intelligence prototype that helps investigate significant KPI changes.



Instead of simply reporting that a KPI increased or decreased, InsightForge follows an investigation workflow:



\*\*Detect → Analyze Drivers → Retrieve Evidence → Rank Evidence → Explain → Recommend\*\*



The system combines structured business metrics, historical driver relationships, customer feedback, and Gemini-powered reasoning to produce an evidence-grounded investigation.



\---



\## Problem



Business dashboards can show that a KPI has changed, but they often do not explain:



\- Why the KPI changed

\- Which business metrics moved alongside it

\- Whether customer feedback supports those observations

\- How strong the available evidence is

\- What should be investigated next



InsightForge addresses this gap by creating an automated investigation pipeline around KPI changes.



\---



\## Solution



For a selected region and period, InsightForge:



1\. Calculates monthly revenue.

2\. Calculates month-over-month revenue change.

3\. Detects significant KPI movements using an investigation threshold.

4\. Identifies the top observed drivers.

5\. Measures historical association between drivers and revenue.

6\. Retrieves relevant customer feedback.

7\. Ranks supporting evidence.

8\. Calculates a heuristic evidence-strength score.

9\. Sends the verified analytical results and supporting evidence to Gemini.

10\. Generates:

&#x20;  - Evidence-grounded explanation

&#x20;  - Uncertainty and limitations

&#x20;  - Recommended next action



The system explicitly distinguishes \*\*association from causation\*\*.



\---



\## Key Features



\### 1. KPI Change Detection



Revenue is monitored on a monthly basis.



The current prototype investigates changes of at least:



```text

5%



Examples:



North, June 2025

Revenue change: -23.08%

→ Investigation triggered



North, July 2025

Revenue change: +26.00%

→ Investigation triggered



South, June 2025

Revenue change: -0.81%

→ No investigation triggered

2\. Driver Analysis



The system analyzes business metrics that move alongside revenue.



Current drivers include:



Product Usage

Support Resolution Hours

Renewal Rate



For each driver, InsightForge calculates:



Previous value

Current value

Percentage change

Historical correlation with revenue

Directional alignment

Driver score



The driver score is a heuristic based on observed change magnitude and historical association:



driver\_score =

&#x20;   abs(percentage\_change) × abs(correlation)



This is used for ranking observed drivers and is not a causal measure.



3\. Evidence Retrieval



Customer feedback is searched using terms associated with the observed drivers.



For example:



support\_resolution\_hours



is converted into searchable terms such as:



support

resolution

hours



Matching feedback is retrieved for the selected region and period.



4\. Evidence Ranking



Retrieved feedback is ranked based on keyword matching.



Evidence containing more relevant driver terms receives a higher evidence score.



This allows InsightForge to prioritize relevant supporting feedback.



5\. Driver-Specific Evidence



Evidence is grouped according to the driver it supports.



Example:



Product Usage

→ Unresolved product issues



Support Resolution Hours

→ Support delays



Renewal Rate

→ No direct qualitative evidence



This prevents the system from treating all customer feedback as evidence for every driver.



6\. Evidence Strength



InsightForge produces a qualitative evidence-strength label:



Weak

Moderate

Strong



The score considers:



Magnitude of KPI change

Number of observed drivers

Amount of supporting evidence

Drivers with qualitative evidence



This is a heuristic assessment, not statistical confidence.



7\. Gemini-Powered Explanation



Gemini receives the verified analytical output rather than performing the numerical analysis itself.



The AI receives:



KPI change

Driver changes

Historical associations

Directional alignment

Driver scores

Supporting customer evidence

Evidence strength



The AI is instructed to:



Avoid causal claims

Use only supplied evidence

Communicate uncertainty

Avoid inventing facts

Recommend one practical action



The generated output contains:



Explanation

Uncertainty

Recommended Action

System Architecture

&#x20;                   ┌─────────────────────┐

&#x20;                   │    Streamlit UI     │

&#x20;                   │ Region + Period     │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Analysis Pipeline   │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;             ┌────────────────┼────────────────┐

&#x20;             │                │                │

&#x20;             ▼                ▼                ▼

&#x20;      KPI Calculation   Change Detection   Driver Analysis

&#x20;             │                │                │

&#x20;             └────────────────┼────────────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Evidence Retrieval  │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Evidence Ranking    │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Evidence Strength   │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Gemini AI Service   │

&#x20;                   │ Explanation         │

&#x20;                   │ Uncertainty         │

&#x20;                   │ Recommendation      │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Streamlit Dashboard │

&#x20;                   └─────────────────────┘

End-to-End Workflow

User selects Region + Period

&#x20;            ↓

Calculate monthly revenue

&#x20;            ↓

Calculate percentage change

&#x20;            ↓

Check investigation threshold

&#x20;            ↓

If insignificant → Stop

&#x20;            ↓

Analyze observed drivers

&#x20;            ↓

Calculate historical associations

&#x20;            ↓

Rank top drivers

&#x20;            ↓

Retrieve customer feedback

&#x20;            ↓

Rank supporting evidence

&#x20;            ↓

Calculate evidence strength

&#x20;            ↓

Build evidence-grounded AI prompt

&#x20;            ↓

Gemini generates structured insight

&#x20;            ↓

Display results

Example Investigation

North Region — June 2025



The prototype detects:



Revenue:

100,000



Previous month:

130,000



Change:

\-23.08%



Top observed drivers:



Product Usage

86 → 70

\-18.60%



Support Resolution Hours

12 → 18

+50.00%



Renewal Rate

93 → 82

\-11.83%



Supporting customer evidence includes:



Unresolved product issues

Longer support ticket resolution

Slower support responses



The system produces an evidence-grounded explanation while explicitly stating that these relationships represent associations rather than proven causal effects.



Positive KPI Investigation

North Region — July 2025



The prototype also handles positive KPI changes.



Revenue:

126,000



Previous month:

100,000



Change:

+26.00%



Observed driver movements include:



Support Resolution Hours

18 → 12

\-33.33%



Product Usage

70 → 84

+20.00%



Renewal Rate

82 → 91

+10.98%



The system identifies these movements as directionally associated with the revenue increase and incorporates the available customer evidence.



Handling Insignificant Changes



Not every KPI movement triggers an AI investigation.



Example:



South Region — June 2025



Revenue change:

\-0.81%



Because the change is below the 5% investigation threshold, InsightForge returns:



No significant KPI change detected.



This prevents unnecessary downstream analysis and AI calls.



Project Structure

InsightForge/

│

├── backend/

│   ├── analysis\_pipeline.py

│   ├── main.py

│   │

│   ├── analytics/

│   │   ├── anomaly\_detection.py

│   │   ├── change\_detection.py

│   │   ├── confidence.py

│   │   ├── driver\_analysis.py

│   │   └── kpi.py

│   │

│   ├── evidence/

│   │   ├── ranking.py

│   │   └── retrieval.py

│   │

│   └── llm/

│       ├── gemini\_service.py

│       └── insight\_generator.py

│

├── data/

│   ├── sales.csv

│   └── customer\_feedback.csv

│

├── frontend/

│   └── app.py

│

├── requirements.txt

├── .gitignore

├── README.md

├── InsightForge\_IITIndore.pdf

└── InsightForge\_IITIndore.pptx

Technology Stack

Frontend

Streamlit

Backend

Python

FastAPI

Data Analysis

Pandas

NumPy

Scikit-learn

AI

Google Gemini

google-genai

Configuration

python-dotenv

Installation

1\. Clone the repository

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd InsightForge

2\. Create a virtual environment



Windows:



python -m venv venv



Activate it:



.\\venv\\Scripts\\Activate.ps1



If PowerShell blocks script execution, the application can also be run directly through:



.\\venv\\Scripts\\python.exe

3\. Install dependencies

pip install -r requirements.txt

Gemini API Configuration



Create a .env file in the project root:



GEMINI\_API\_KEY=your\_api\_key\_here



Do not commit .env to GitHub.



The repository ignores:



.env

venv/

\_\_pycache\_\_/

InsightForge\_IITIndore.mp4

Running the Application



From the project root:



.\\venv\\Scripts\\python.exe -m streamlit run frontend\\app.py



The application will be available at:



http://localhost:8501



Select a region and period, then click:



Analyze KPI

API



A minimal FastAPI backend is also included.



Run:



.\\venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload



Health endpoint:



GET /health



Expected response:



{

&#x20; "status": "healthy"

}

Robustness



The prototype has been tested for:



Positive KPI changes

Negative KPI changes

Insignificant KPI changes

Invalid periods

Missing customer evidence

Gemini API failures

Invalid Gemini responses

Empty Gemini responses

Missing fields in Gemini JSON output



When Gemini is unavailable, InsightForge returns a structured fallback response instead of crashing the application.



Analytical Limitations



InsightForge is an analytical investigation prototype, not a causal inference system.



Correlation is not causation



A driver moving alongside revenue does not prove that it caused the revenue change.



Small historical dataset



Historical correlations are calculated using the available pre-period observations. With a small number of observations, correlation estimates should be interpreted cautiously.



Heuristic evidence strength



The evidence-strength label is a heuristic based on available KPI movement, drivers, and supporting evidence. It is not statistical confidence.



Incomplete qualitative evidence



Some drivers may not have directly matching customer feedback.



External factors



Market conditions, competitors, pricing changes, seasonality, operational changes, and other variables not represented in the dataset may affect revenue.



Human review is therefore required before making business decisions.



Design Principle



AI should explain verified evidence, not invent the evidence.



The numerical analysis is performed programmatically.



The evidence is retrieved from the supplied dataset.



Gemini is used to synthesize these verified inputs into an understandable business explanation.



Future Improvements



Potential future improvements include:



Larger real-world datasets

More KPI types

Statistical significance testing

Time-series forecasting

Causal inference methods

Semantic/vector-based evidence retrieval

More sophisticated evidence scoring

Automated report generation

Real-time business data integration

Monitoring and alerting



Status



Prototype — Round 2



The current prototype demonstrates the complete investigation workflow from KPI detection to evidence-backed AI explanation.





\### After pasting



1\. Press \*\*Ctrl + S\*\*

2\. Close Notepad.

3\. Back in PowerShell run:



```powershell

git add README.md

git commit -m "Add project documentation"

