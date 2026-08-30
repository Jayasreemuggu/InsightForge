import pandas as pd
import time

from backend.analytics.kpi import calculate_monthly_revenue
from backend.analytics.change_detection import calculate_percentage_change
from backend.analytics.anomaly_detection import detect_significant_changes
from backend.analytics.contribution import calculate_driver_contribution
from backend.analytics.driver_analysis import analyze_driver_changes
from backend.analytics.confidence import calculate_confidence
from backend.evidence.retrieval import retrieve_feedback
from backend.evidence.ranking import rank_evidence
from backend.reconciliation import reconcile_sources
from backend.feedback import get_relevant_feedback
from backend.llm.gemini_service import generate_insight


def run_analysis(
    sales_file: str,
    feedback_file: str,
    region: str,
    date: str,
    persona: str,
    pipeline_start = time.perf_counter() 
):
    total_start = time.perf_counter()

    def log_time(label, start):
        elapsed = time.perf_counter() - start
        print(f"[LATENCY] {label}: {elapsed:.3f}s")
        return elapsed

    # ==================================================
    # Retrieve previous analyst/business feedback
    # ==================================================
    t = time.perf_counter()
    previous_feedback = get_relevant_feedback(
        region=region,
        date=date,
        kpi="Revenue",
        persona=persona
    )

    log_time("Initial feedback retrieval", t)
    
    print("PREVIOUS FEEDBACK:")
    print(previous_feedback)

    # ==================================================
    # 1. Calculate KPI
    # ==================================================
    t = time.perf_counter()
    df = calculate_monthly_revenue(
        sales_file
    )
    
    log_time("KPI calculation", t)
    print(f"[PERF] calculate_monthly_revenue: {time.perf_counter() - t:.3f}s")

    # ==================================================
    # 2. Calculate KPI percentage change
    # ==================================================
    t = time.perf_counter()
    df = calculate_percentage_change(
        df
    )
    log_time("Percentage change", t)
    print(f"[PERF] percentage_change: {time.perf_counter() - t:.3f}s")

    # ==================================================
    # 3. Detect significant changes
    # ==================================================
    t = time.perf_counter()
    df = detect_significant_changes(
        df
    )
    log_time("Change detection", t)
    print(f"[PERF] anomaly_detection: {time.perf_counter() - t:.3f}s")


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
    # 8. Analyze driver changes
    # ==================================================
    t = time.perf_counter()
    sales_df = pd.read_csv(
        sales_file
    )

    # ==================================================
    # Sparse-history detection
    # ==================================================

    historical_observations = len(
        sales_df[
            (sales_df["region"] == region) &
            (pd.to_datetime(sales_df["date"]) < pd.to_datetime(date))
        ]
    )

    log_time("Sales CSV loading", t)

    t = time.perf_counter()
    drivers = analyze_driver_changes(
        sales_df,
        region,
        date
    )
    log_time("Driver analysis", t)
    print(f"[PERF] driver_analysis: {time.perf_counter() - t:.3f}s")

    # ==================================================
    # 9. Retrieve analyst/business feedback
    # ==================================================
    t = time.perf_counter()
    learned_feedback = get_relevant_feedback(
        region=region,
        date=date,
        kpi="Revenue",
        persona=persona
    )
    log_time("Learned feedback retrieval", t)

    # ==================================================
    # 10. Select top three observed drivers
    # ==================================================

    top_drivers = drivers.head(3).copy()

    top_drivers = calculate_driver_contribution(
        top_drivers
    )

    # ==================================================
    # 10A. Apply learned analyst/business feedback
    # ==================================================

    if learned_feedback:
        for feedback in learned_feedback:

            if feedback["feedback_type"] != "correction":
                continue

            correction_text = (
                feedback.get("correction", "")
                .lower()
            )

            # If previous feedback says that
            # support resolution hours should not
            # be treated as a strong driver,
            # remove it from the top-driver ranking.
            if (
                "support resolution hours" in correction_text
                and
                "not be treated" in correction_text
            ):
                top_drivers = top_drivers[
                    top_drivers["driver"]
                    != "support_resolution_hours"
                ].copy()

        # Keep maximum three drivers
        top_drivers = top_drivers.head(3).copy()
    

    # ==================================================
    # 10B. Retrieve customer feedback
    # ==================================================
    t = time.perf_counter()
    feedback_df = pd.read_csv(
        feedback_file
    )
    log_time("Customer feedback loading/filtering", t)

    feedback_df["date"] = pd.to_datetime(
        feedback_df["date"]
    )

    # ==================================================
    # 10C. Reconcile heterogeneous sources
    # ==================================================

    reconciliation = reconcile_sources(
        sales_df=sales_df,
        feedback_df=feedback_df,
        region=region,
        date=date
    )

    feedback_df["analysis_month"] = (
        feedback_df["date"].dt.to_period("M")
    )

    period_feedback = feedback_df[
        (feedback_df["region"] == region) &
        (feedback_df["analysis_month"] == pd.to_datetime(date).to_period("M"))
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

            "contribution_weight": driver_row[
                "contribution_weight"
            ],

            "contribution_percentage": driver_row[
                "contribution_percentage"
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

    confidence = calculate_confidence(
        kpi_change,
        len(driver_records),
        len(all_evidence),
        qualitative_evidence_count,
        historical_observations
    )

    # ==================================================
    # Sparse-history abstention
    # ==================================================

    abstained = False

    if historical_observations < 3:
        abstained = True
        confidence = "Low"

    # ==================================================
    # 15. Build LLM prompt
    # ==================================================

    prompt = f"""
        You are InsightForge, an evidence-driven
        business intelligence assistant.
        
        Persona: {persona}

        Persona-specific guidance:

        - Executive: provide a concise business summary,
          key business impact, and one practical decision/action.

        - Analyst: provide detailed quantitative analysis,
          ranked drivers, percentage changes, correlations,
          significance, evidence, and recommended analytical
          follow-up.

        - Manager: focus on operational drivers,
          controllable business levers, ownership, and
          practical next steps.

        Adjust the explanation and recommended action
        according to the persona, while preserving all
        quantitative facts and uncertainty.

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
        - Correlations based on few observations should still
        be treated cautiously even if the p-value is below 0.05.

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
    # 16. Generate structured AI insight
    # ==================================================
    t = time.perf_counter()
    insight = generate_insight(
        prompt,
        persona=persona
    )
    log_time("Gemini/LLM generation", t)
    print(f"[PERF] generate_insight: {time.perf_counter() - t:.3f}s")

    # ==================================================
    # 17. Role-based entitlement filtering
    # ==================================================

    normalized_persona = str(persona).strip().lower()

    if normalized_persona not in {
        "executive",
        "manager",
        "analyst"
    }:
        normalized_persona = "executive"

    # Executive: high-level business information only
    if normalized_persona == "executive":

        role_drivers = []

        for driver in driver_records[:3]:
            role_drivers.append({
                "driver": driver["driver"],
                "percentage_change": driver["percentage_change"],
                "driver_score": driver["driver_score"]
            })

        role_evidence = all_evidence[:3]

    # Manager: operational drivers + evidence
    elif normalized_persona == "manager":

        role_drivers = []

        for driver in driver_records[:5]:
            role_drivers.append({
                "driver": driver["driver"],
                "previous_value": driver["previous_value"],
                "current_value": driver["current_value"],
                "percentage_change": driver["percentage_change"],
                "driver_score": driver["driver_score"],
                "supporting_evidence": driver.get(
                    "supporting_evidence", []
                )
            })

        role_evidence = all_evidence

    # Analyst: full statistical information
    else:

        role_drivers = driver_records
        role_evidence = all_evidence

    # ==================================================
    # 18. Return complete analysis
    # ==================================================
    log_time("TOTAL run_analysis", total_start)
    print(
        f"[PERF] TOTAL PIPELINE: "
        f"{time.perf_counter() - pipeline_start:.3f}s"
    )
    
    return {
        "region": region,
        "date": date,
        "kpi": "Revenue",
        "reconciliation": reconciliation,
        "kpi_change": kpi_change,
        "regional_comparison": regional_comparison,
        "drivers": driver_records,
        "persona": normalized_persona,
        "role_drivers": role_drivers,
        "role_evidence": role_evidence,
        "evidence": all_evidence,
        "confidence": confidence,
        "abstained": abstained,
        "explanation": insight["explanation"],
        "uncertainty": insight["uncertainty"],
        "recommended_action": insight[
            "recommended_action"
        ]
    }