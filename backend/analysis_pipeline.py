import pandas as pd

from backend.analytics.kpi import calculate_monthly_revenue
from backend.analytics.change_detection import calculate_percentage_change
from backend.analytics.anomaly_detection import detect_significant_changes
from backend.analytics.driver_analysis import analyze_driver_changes
from backend.analytics.confidence import calculate_confidence
from backend.evidence.retrieval import retrieve_feedback
from backend.evidence.ranking import rank_evidence
from backend.llm.gemini_service import generate_insight


def run_analysis(
    sales_file: str,
    feedback_file: str,
    region: str,
    date: str
):
    # ==================================================
    # 1. Calculate KPI
    # ==================================================

    df = calculate_monthly_revenue(
        sales_file
    )


    # ==================================================
    # 2. Calculate KPI percentage change
    # ==================================================

    df = calculate_percentage_change(
        df
    )


    # ==================================================
    # 3. Detect significant changes
    # ==================================================

    df = detect_significant_changes(
        df
    )


    # ==================================================
    # 4. Find requested region and period
    # ==================================================

    anomaly = df[
        (df["region"] == region) &
        (df["date"] == pd.to_datetime(date))
    ]


    if anomaly.empty:

        return {
            "error": "Requested period was not found."
        }


    # ==================================================
    # 5. Get KPI change
    # ==================================================

    kpi_change = float(
        anomaly.iloc[0]["percentage_change"]
    )


    # ==================================================
    # 6. Check significance
    # ==================================================

    is_significant = bool(
        anomaly.iloc[0]["is_significant"]
    )


    if not is_significant:

        return {
            "error": (
                f"No significant KPI change detected for "
                f"{region} during {date}. "
                f"The change was {kpi_change:.2f}%, "
                f"below the 5% investigation threshold."
            )
        }


    # ==================================================
    # 7. Analyze driver changes
    # ==================================================

    sales_df = pd.read_csv(
        sales_file
    )

    drivers = analyze_driver_changes(
        sales_df,
        region,
        date
    )


    # ==================================================
    # 8. Select top three observed drivers
    # ==================================================

    top_drivers = drivers.head(3).copy()


    # ==================================================
    # 9. Retrieve customer feedback
    # ==================================================

    feedback_df = pd.read_csv(
        feedback_file
    )

    feedback_df["date"] = pd.to_datetime(
        feedback_df["date"]
    )

    period_feedback = feedback_df[
        (feedback_df["region"] == region) &
        (feedback_df["date"] == pd.to_datetime(date))
    ].copy()


    # ==================================================
    # 10. Match evidence to each driver
    # ==================================================

    driver_evidence = {}

    all_evidence = []


    for driver in top_drivers["driver"]:

        # Convert driver name into useful keywords
        driver_keywords = [
            word.lower()
            for word in driver.split("_")
        ]

        # Find feedback containing at least one
        # driver-related keyword
        if period_feedback.empty:

            matched = period_feedback.copy()

        else:

            pattern = "|".join(
                driver_keywords
            )

            matched = period_feedback[
                period_feedback["feedback"]
                .str.contains(
                    pattern,
                    case=False,
                    na=False
                )
            ].copy()


        # Rank matched evidence
        if not matched.empty:

            matched = rank_evidence(
                matched,
                driver_keywords
            )

            evidence_list = (
                matched["feedback"]
                .tolist()
            )

        else:

            evidence_list = []


        driver_evidence[driver] = (
            evidence_list
        )

        all_evidence.extend(
            evidence_list
        )


    # ==================================================
    # 11. Remove duplicate evidence
    # ==================================================

    all_evidence = list(
        dict.fromkeys(all_evidence)
    )


    # ==================================================
    # 12. Add evidence to each driver
    # ==================================================

    driver_records = []


    for _, driver_row in top_drivers.iterrows():

        driver_name = driver_row["driver"]

        driver_record = {
            "driver": driver_name,
            "previous_value": driver_row[
                "previous_value"
            ],
            "current_value": driver_row[
                "current_value"
            ],
            "percentage_change": driver_row[
                "percentage_change"
            ],
            "correlation": driver_row[
                "correlation"
            ],
            "direction_alignment": driver_row[
                "direction_alignment"
            ],
            "driver_score": driver_row[
                "driver_score"
            ],
            "supporting_evidence": driver_evidence.get(
                driver_name,
                []
            )
        }

        driver_records.append(
            driver_record
        )


    # ==================================================
    # 13. Calculate evidence strength
    # ==================================================
    
    qualitative_evidence_count = sum(
        1
        for driver in driver_records
        if driver["supporting_evidence"]
    )
    confidence = calculate_confidence(
        kpi_change,
        len(driver_records),
        len(all_evidence),
        len(all_evidence)
    )


    # ==================================================
    # 14. Build LLM prompt
    # ==================================================

    prompt = f"""
You are InsightForge, an evidence-driven
business intelligence assistant.

Analyze the following verified business data.

KPI: Revenue
Region: {region}
Period: {date}
Revenue change: {kpi_change:.2f}%

Observed driver analysis:

{driver_records}

Each driver contains:

- previous_value
- current_value
- percentage_change
- correlation
- direction_alignment
- driver_score
- historical_observations
- supporting_evidence

Interpretation rules:

- percentage_change is the observed
  month-over-month driver change.

- correlation represents historical
  association with revenue using the
  available pre-period observations.

- direction_alignment indicates whether
  the current driver movement is
  directionally consistent with its
  historical relationship with revenue.

- driver_score ranks observed driver
  strength using change magnitude and
  historical association.

- supporting_evidence contains customer
  feedback specifically matched to that
  driver.

- A driver without supporting_evidence
  does NOT have direct qualitative
  customer evidence.

- Correlation and driver scores indicate
  association, not causation.

- historical_observations is the number of pre-period observations used to calculate the historical correlation.
- Correlations based on a small number of observations should be treated cautiously.

Evidence strength:

{confidence}

Rules:

- Do not claim causation.
- Describe drivers as observed
  associations.
- Use only the supplied evidence.
- Do not invent facts.
- Do not claim qualitative evidence
  exists when supporting_evidence is empty.
- Clearly communicate uncertainty.
- Treat evidence strength as a heuristic,
  not statistical confidence.
- Recommend one practical business action.
- Human review remains necessary.

Return ONLY valid JSON using exactly
this structure:

{{
    "explanation":
        "Brief evidence-grounded explanation",

    "uncertainty":
        "Explain limitations and alternative explanations",

    "recommended_action":
        "One practical next-best action"
}}
"""


    # ==================================================
    # 15. Generate structured AI insight
    # ==================================================

    insight = generate_insight(
        prompt
    )


    # ==================================================
    # 16. Return complete analysis
    # ==================================================

    return {
        "region": region,
        "date": date,
        "kpi": "Revenue",
        "kpi_change": kpi_change,
        "drivers": driver_records,
        "evidence": all_evidence,
        "confidence": confidence,
        "explanation": insight["explanation"],
        "uncertainty": insight["uncertainty"],
        "recommended_action": insight[
            "recommended_action"
        ]
    }