import pandas as pd

from backend.config_loader import get_kpi_definition
from backend.data_reconciliation import reconcile_sources
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
    date: str,
    product_usage_file: str = "data/product_usage.csv",
    renewal_file: str = "data/renewal_data.csv",
    support_file: str = "data/support_tickets.csv"
):
    
    # ==================================================
    # 0. Load governed KPI semantic contract
    # ==================================================

    kpi_definition = get_kpi_definition("revenue")
    
    revenue_column = kpi_definition["calculation"]["column"]

    if revenue_column != "revenue":
        raise ValueError(
            f"Expected revenue column, got '{revenue_column}'."
        )
        
    # ==================================================
    # 1. Reconcile heterogeneous sources
    # ==================================================

    df = reconcile_sources(
        sales_file=sales_file,
        product_usage_file=product_usage_file,
        renewal_file=renewal_file,
        support_file=support_file
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
    # 6. Regional comparison
    # ==================================================

    comparison_rows = []

    comparison_date = pd.to_datetime(date)

    for comparison_region in df["region"].unique():

        if comparison_region == region:
            continue

        comparison_current = df[
            (df["region"] == comparison_region) &
            (df["date"] == comparison_date)
        ]

        comparison_previous = df[
            (df["region"] == comparison_region) &
            (df["date"] < comparison_date)
        ]

        if comparison_current.empty or comparison_previous.empty:
            continue

        current_revenue = float(
            comparison_current.iloc[0]["revenue"]
        )

        previous_revenue = float(
            comparison_previous.sort_values("date").iloc[-1]["revenue"]
        )

        if previous_revenue == 0:
            comparison_change = 0.0
        else:
            comparison_change = (
                (current_revenue - previous_revenue)
                / previous_revenue
        ) * 100

        comparison_rows.append({
            "region": comparison_region,
            "previous_revenue": previous_revenue,
            "current_revenue": current_revenue,
            "percentage_change": comparison_change
        })

    regional_comparison = comparison_rows

    # ==================================================
    # 7. Check significance
    # ==================================================

    is_significant = bool(
        anomaly.iloc[0]["is_significant"]
    )


    if pd.isna(kpi_change):
        return {
            "error": (
                f"No valid KPI change could be calculated for "
                f"{region} during {date}. "
                "A previous period is required for comparison."
            ),
            "abstained": True
        }

    if abs(kpi_change) < 5:
        return {
            "error": (
                f"No significant KPI change detected for "
                f"{region} during {date}. "
                f"The change was {kpi_change:.2f}%, "
                "below the 5% investigation threshold."
            ),
            "abstained": True
        }

    # ==================================================
    # 8. Analyze driver changes
    # ==================================================

    drivers = analyze_driver_changes(
        df,
        region,
        date
    )


    # ==================================================
    # 9. Select top three observed drivers
    # ==================================================

    top_drivers = drivers.head(3).copy()


    # ==================================================
    # 10. Retrieve customer feedback
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
    # 11. Match evidence to each driver
    # ==================================================

    driver_evidence = {}

    all_evidence = []


    for driver in top_drivers["driver"]:

        # Use driver-specific keywords based on the
        # actual language present in customer feedback.
        driver_keyword_map = {
            "product_usage": [
                "product usage",
                "product performance"
            ],

            "support_resolution_hours": [
                "support tickets",
                "support response",
                "support delays",
                "support",
                "slower",
                "longer to resolve"
            ],

            "renewal_rate": [
                "renewal",
                "renew"
            ]
        }

        driver_keywords = driver_keyword_map.get(
            driver,
            [
                word.lower()
                for word in driver.split("_")
            ]
        )

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
    # 12. Remove duplicate evidence
    # ==================================================

    all_evidence = list(
        dict.fromkeys(all_evidence)
    )


    # ==================================================
    # 13. Add evidence to each driver
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
            "historical_observations": driver_row[
                "historical_observations"
            ],
            
            "correlation_reliability": driver_row[
                "correlation_reliability"
            ],
            
            "correlation_p_value": driver_row[
                "correlation_p_value"
            ],

            "correlation_significance": driver_row[
                "correlation_significance"
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
    # 14. Calculate evidence strength
    # ==================================================
    
    qualitative_evidence_count = sum(
        1
        for driver in driver_records
        if driver["supporting_evidence"]
    )

    historical_observations = min(
        (
            driver["historical_observations"]
            for driver in driver_records
        ),
        default=0
    )
    
    
    confidence = calculate_confidence(
        kpi_change,
        len(driver_records),
        len(all_evidence),
        qualitative_evidence_count,
        historical_observations
    )
    
        # ==================================================
    # 14B. Sparse-history safety gate
    # ==================================================
    #
    # Do not allow the LLM to generate driver conclusions
    # when there is insufficient historical evidence.
    #
    # This is deterministic business logic, not an LLM decision.
    #

    MIN_HISTORICAL_OBSERVATIONS = 3

    if historical_observations < MIN_HISTORICAL_OBSERVATIONS:

        return {
            "region": region,
            "date": date,
            "kpi": "Revenue",
            "kpi_change": kpi_change,
            "regional_comparison": regional_comparison,
            "drivers": driver_records,
            "evidence": all_evidence,
            "confidence": "Limited",
            "analysis_abstained": True,
            "explanation": (
                "The revenue movement was detected, but there is "
                "insufficient historical data to reliably identify "
                "explanatory drivers."
            ),
            "uncertainty": (
                f"Only {historical_observations} historical observations "
                "were available for driver analysis. This is insufficient "
                "to establish a reliable historical relationship. "
                "The system therefore abstains from generating an "
                "AI-based driver explanation."
            ),
            "recommended_action": (
                "Collect additional historical observations before "
                "using driver relationships for decision-making, "
                "and conduct human review of the current revenue movement."
            )
        }

    # ==================================================
    # 15. Build LLM prompt
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
- correlation_reliability
- correlation_p_value
- correlation_significance
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

- correlation_reliability describes the reliability
  of the historical correlation based only on the
  number of available pre-period observations.
- Do not describe Limited or Very Limited correlations
  as strong evidence.
- correlation_p_value represents the p-value of the
  historical Pearson correlation.
- correlation_significance indicates whether the
  correlation passes the 0.05 significance threshold.
- Statistical significance does not establish causation.

IMPORTANT STATISTICAL INTERPRETATION RULES:

- The supplied correlation_significance field is authoritative.
- Do not recalculate or override the supplied significance classification.
- If correlation_significance is "Statistically significant",
  describe it as statistically significant.
- If correlation_significance is "Not statistically significant",
  describe it as not statistically significant.
- Always mention historical_observations and
  correlation_reliability when discussing correlations.
- Statistical significance does not establish causation.
- Limited or Very Limited correlation reliability must be clearly stated.

Evidence strength:

{confidence}

Rules:

- Do not claim causation.
- Preserve driver-specific statistical results exactly.
  Do not merge, average, or generalize p-values or
  statistical-significance labels across drivers.
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
    # 16. Generate structured AI insight
    # ==================================================

    insight = generate_insight(
        prompt
    )


    # ==================================================
    # 17. Return complete analysis
    # ==================================================

    return {
        "region": region,
        "date": date,
        "kpi": "Revenue",
        "kpi_change": kpi_change,
        "regional_comparison": regional_comparison,
        "drivers": driver_records,
        "evidence": all_evidence,
        "confidence": confidence,
        "analysis_abstained": False,
        "explanation": insight["explanation"],
        "uncertainty": insight["uncertainty"],
        "recommended_action": insight[
            "recommended_action"
        ]
    }