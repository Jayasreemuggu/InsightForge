import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd
import requests

from backend.analysis_pipeline import run_analysis
from backend.analytics.llm_breakdown import get_llm_non_llm_breakdown


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="InsightForge",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("InsightForge")

st.subheader(
    "Evidence-Driven KPI Investigation"
)

st.caption(
    "Detect significant KPI changes, identify observed drivers, "
    "connect customer evidence, and generate an evidence-grounded AI insight."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Investigation")

sales_df = pd.read_csv("data/sales.csv")

sales_df["date"] = pd.to_datetime(
    sales_df["date"]
)

available_regions = (
    sales_df["region"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

region = st.sidebar.selectbox(
    "Region",
    available_regions
)

available_dates = (
    sales_df["date"]
    .drop_duplicates()
    .sort_values()
    .dt.strftime("%Y-%m-%d")
    .tolist()
)

date = st.sidebar.selectbox(
    "Period",
    available_dates,
    format_func=lambda x:
        pd.to_datetime(x).strftime("%B %Y")
)

persona = st.sidebar.selectbox(
    "Persona",
    [
        "Executive",
        "Manager",
        "Analyst"
    ]
)

analyze_button = st.sidebar.button(
    "Analyze KPI",
    width="stretch"
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    with st.spinner("Investigating KPI change..."):

        result = run_analysis(
            "data/sales.csv",
            "data/customer_feedback.csv",
            region,
            date,
            persona=persona
        )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    if result.get("abstained", False):

        st.warning("Investigation abstained")

        st.info(
            result.get(
                "error",
                "The KPI change does not provide sufficient information for investigation."
            )
        )

        st.caption(
            "InsightForge did not generate driver analysis or an AI explanation "
            "because the required comparison data was unavailable or the KPI "
            "movement did not meet the investigation threshold."
        )

    elif "error" in result:

        st.error(result["error"])

    else:

        st.success("Analysis completed")

        # ====================================================
        # KPI OVERVIEW
        # ====================================================

        st.header("KPI Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "KPI",
                result["kpi"]
            )

        with col2:
            st.metric(
                "Region",
                result["region"]
            )

        with col3:
            st.metric(
                "Revenue Change",
                f"{result['kpi_change']:+.2f}%"
            )

        with col4:
            st.metric(
                "Evidence Strength",
                result["confidence"]
            )


        # ====================================================
        # INVESTIGATION SUMMARY
        # ====================================================

        st.divider()

        st.header("Investigation Summary")

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.markdown(
                f"""
                **Investigated Period**

                {pd.to_datetime(result["date"]).strftime("%B %Y")}
                """
            )

        with summary_col2:

            change = float(result["kpi_change"])

            if change > 0:
                movement = "Revenue increased"
            elif change < 0:
                movement = "Revenue decreased"
            else:
                movement = "Revenue remained unchanged"

            st.markdown(
                f"""
                **KPI Movement**

                {movement} by **{abs(change):.2f}%**
                """
            )


        # ====================================================
        # REVENUE TREND
        # ====================================================

        st.divider()

        st.header("Revenue Trend")

        trend_df = pd.read_csv(
            "data/sales.csv"
        )

        trend_df["date"] = pd.to_datetime(
            trend_df["date"]
        )

        region_trend = (
            trend_df[
                trend_df["region"] == result["region"]
            ][
                ["date", "revenue"]
            ]
            .sort_values("date")
            .copy()
        )

        region_trend["month_number"] = (
            region_trend["date"].dt.month
        )

        region_trend["month"] = (
            region_trend["date"].dt.strftime("%b")
        )

        month_order = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec"
        ]

        region_trend["month"] = pd.Categorical(
            region_trend["month"],
            categories=month_order,
            ordered=True
        )

        region_trend = region_trend.sort_values(
            "month_number"
        )

        chart_data = (
            region_trend[
                ["month", "revenue"]
            ]
            .set_index("month")
        )

        st.line_chart(
            chart_data["revenue"],
            width="stretch"
        )

        investigated_date = pd.to_datetime(
            result["date"]
        )

        investigated_row = region_trend[
            region_trend["date"] == investigated_date
        ]

        if not investigated_row.empty:

            investigated_revenue = float(
                investigated_row.iloc[0]["revenue"]
            )

            investigated_month = (
                investigated_date.strftime("%B %Y")
            )

            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:

                st.metric(
                    "Investigated Month Revenue",
                    f"₹{investigated_revenue:,.0f}"
                )

            with metric_col2:

                st.metric(
                    "Change vs Previous Month",
                    f"{result['kpi_change']:+.2f}%"
                )

            st.caption(
                f"Investigated period: {investigated_month}"
            )


        # ====================================================
        # TOP OBSERVED DRIVERS
        # ====================================================

        st.divider()

        st.header("Top Observed Drivers")

        driver_df = pd.DataFrame(
            result["drivers"]
        )

        driver_df["Driver"] = (
            driver_df["driver"]
            .astype(str)
            .str.replace(
                "_",
                " ",
                regex=False
            )
            .str.title()
        )


        # ====================================================
        # DRIVER CARDS
        # ====================================================

        driver_columns = st.columns(
            len(driver_df)
        )

        for i, (_, driver) in enumerate(
            driver_df.iterrows()
        ):

            change = float(
                driver["percentage_change"]
            )

            display_name = driver["Driver"]

            if change > 0:
                direction = "↑ Increase"
            elif change < 0:
                direction = "↓ Decrease"
            else:
                direction = "→ No Change"

            with driver_columns[i]:

                st.write(
                    f"**{display_name}**"
                )

                st.markdown(
                    f"### {change:+.2f}%"
                )

                st.caption(
                    direction
                )


        # ====================================================
        # DRIVER CHANGE COMPARISON
        # ====================================================

        st.subheader(
            "Driver Change Comparison"
        )

        driver_chart = driver_df[
            [
                "Driver",
                "percentage_change"
            ]
        ].copy()

        # Shorter labels for the chart
        driver_chart["Driver"] = driver_chart["Driver"].replace({
            "Support Resolution Hours": "Support Resolution",
            "Product Usage": "Product Usage",
            "Renewal Rate": "Renewal Rate"
        })

        driver_chart = driver_chart.sort_values(
            "percentage_change"
        )

        driver_chart = driver_chart.set_index(
            "Driver"
        )

        st.bar_chart(
            driver_chart["percentage_change"],
            horizontal=True,
            width="stretch",
            height=280
        )

        st.caption(
            "Positive values indicate an increase; "
            "negative values indicate a decrease."
        )
        
        # ====================================================
        # REGIONAL COMPARISON
        # ====================================================

        st.divider()

        st.header(
            "Regional Comparison"
        )

        st.caption(
            "Compares the investigated region's revenue movement "
            "with other available regions for the same period."
        )

        regional_comparison = result.get(
            "regional_comparison",
            []
        )

        if regional_comparison:

            comparison_df = pd.DataFrame(
                regional_comparison
            )

            comparison_df = comparison_df.rename(
                columns={
                    "region": "Region",
                    "previous_revenue": "Previous Revenue",
                    "current_revenue": "Current Revenue",
                    "percentage_change": "Change (%)"
                }
            )

            comparison_df["Previous Revenue"] = (
                comparison_df["Previous Revenue"]
                .round(2)
            )

            comparison_df["Current Revenue"] = (
                comparison_df["Current Revenue"]
                .round(2)
            )

            comparison_df["Change (%)"] = (
                comparison_df["Change (%)"]
                .round(2)
            )

            st.dataframe(
                comparison_df,
                width="stretch",
                hide_index=True
            )

        else:

            st.caption(
                "No comparison region data available "
                "for this period."
            )

        # ====================================================
        # DRIVER DETAILS
        # ====================================================

        st.subheader(
            "Driver Details"
        )

        display_rows = []

        for driver in result["drivers"]:

            driver_name = (
                driver["driver"]
                .replace("_", " ")
                .title()
            )

            display_rows.append(
                {
                    "Driver": driver_name,

                    "Previous Value": driver.get(
                        "previous_value",
                        "-"
                    ),

                    "Current Value": driver.get(
                        "current_value",
                        "-"
                    ),

                    "Change (%)": round(
                        float(
                            driver.get(
                                "percentage_change",
                                0
                            )
                        ),
                        2
                    ),

                    "Correlation": round(
                        float(
                            driver.get(
                                "correlation",
                                0
                            )
                        ),
                        3
                    ),

                    "Historical Observations": driver.get(
                        "historical_observations",
                        0
                    ),

                    "Correlation Reliability": driver.get(
                        "correlation_reliability",
                        "Unknown"
                    ),

                    "Correlation p-value": round(
                        float(
                            driver.get(
                                "correlation_p_value",
                                1.0
                            )
                        ),
                        4
                    ),

                    "Correlation Significance": driver.get(
                        "correlation_significance",
                        "Unknown"
                    ),

                    "Driver Score": round(
                        float(
                            driver.get(
                                "driver_score",
                                0
                            )
                        ),
                        2
                    )
                }
            )

        display_df = pd.DataFrame(
            display_rows
        )

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            "Correlation and driver score represent observed "
            "historical associations. They do not establish causation."
        )


        # ====================================================
        # INVESTIGATION EVIDENCE CHAIN
        # ====================================================

        st.divider()

        st.header(
            "Investigation Evidence Chain"
        )

        st.caption(
            "How the observed KPI change was investigated "
            "from quantitative signals to supporting evidence."
        )

        chain_cols = st.columns(4)

        with chain_cols[0]:

            st.metric(
                "1. KPI Change",
                f"{result['kpi_change']:+.2f}%"
            )

            st.caption(
                "Significant movement detected"
            )

        with chain_cols[1]:

            st.metric(
                "2. Drivers",
                str(len(result["drivers"]))
            )

            st.caption(
                "Observed associated drivers"
            )

        with chain_cols[2]:

            evidence_count = sum(
                len(
                    driver.get(
                        "supporting_evidence",
                        []
                    )
                )
                for driver in result["drivers"]
            )

            st.metric(
                "3. Evidence",
                str(evidence_count)
            )

            st.caption(
                "Customer feedback matched"
            )

        with chain_cols[3]:

            st.metric(
                "4. Evidence Strength",
                result["confidence"]
            )

            st.caption(
                "Overall evidence assessment"
            )


        # ====================================================
        # SUPPORTING EVIDENCE
        # ====================================================

        st.divider()

        st.header("Supporting Evidence")

        st.caption(
            "Customer feedback matched to the observed drivers."
        )

        for driver in result["drivers"]:

            driver_name = (
                driver["driver"]
                .replace("_", " ")
                .title()
            )

            st.subheader(driver_name)

            supporting_evidence = driver.get(
                "supporting_evidence",
                []
            )

            if supporting_evidence:

                for evidence in supporting_evidence:

                    feedback = evidence.get(
                        "feedback",
                        ""
                    )

                    evidence_strength = evidence.get(
                        "evidence_strength",
                        "Unknown"
                    )

                    evidence_score = evidence.get(
                        "evidence_score",
                        "N/A"
                    )

                    matched_keywords = evidence.get(
                        "matched_keywords",
                        []
                    )

                    matched_signals = " · ".join(
                        matched_keywords
                    )

                    st.markdown(
                        f"""
                        <div style="
                            border: 1px solid #444;
                            border-radius: 10px;
                            padding: 18px 20px;
                            margin: 10px 0 16px 0;
                            background-color: rgba(255,255,255,0.02);
                        ">

                            <div style="
                                font-size: 13px;
                                font-weight: 600;
                                margin-bottom: 10px;
                            ">
                                Customer Feedback
                            </div>

                            <div style="
                                border-left: 3px solid #666;
                                padding-left: 14px;
                                margin-bottom: 18px;
                                font-size: 15px;
                                line-height: 1.5;
                            ">
                                {feedback}
                            </div>

                            <div style="
                                display: flex;
                                gap: 80px;
                                margin-bottom: 16px;
                            ">

                                <div>
                                    <div style="
                                        font-size: 12px;
                                        color: #999;
                                        margin-bottom: 5px;
                                    ">
                                        Evidence Strength
                                    </div>

                                    <div style="
                                        font-size: 15px;
                                        font-weight: 600;
                                    ">
                                        {evidence_strength}
                                    </div>
                                </div>

                                <div>
                                    <div style="
                                        font-size: 12px;
                                        color: #999;
                                        margin-bottom: 5px;
                                    ">
                                        Evidence Score
                                    </div>

                                    <div style="
                                        font-size: 15px;
                                        font-weight: 600;
                                    ">
                                        {evidence_score}
                                    </div>
                                </div>

                            </div>

                            <div style="
                                font-size: 12px;
                                color: #999;
                            ">
                                <strong style="color: #aaa;">
                                    Matched Signals:
                                </strong>
                                {matched_signals}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.caption(
                    "No direct qualitative evidence found for this driver."
                )
                
        # ====================================================
        # AI EXPLANATION
        # ====================================================

        

        st.header("AI Explanation")

        if result.get("analysis_abstained", False):

            st.warning(
                "Analysis Abstained — Insufficient Historical Evidence"
            )

            st.markdown(
                result["explanation"]
            )

        else:

            explanation = result["explanation"].strip()

            explanation = explanation.replace(
                "product_usage",
                "Product Usage"
            ).replace(
                "renewal_rate",
                "Renewal Rate"
            ).replace(
                "support_resolution_hours",
                "Support Resolution Hours"
            )

            st.markdown(explanation)

        # ====================================================
        # UNCERTAINTY
        # ====================================================

        st.subheader(
            "Uncertainty"
        )

        st.warning(
            result["uncertainty"]
        )


        # ====================================================
        # RECOMMENDED ACTION
        # ====================================================

        st.subheader(
            "Recommended Action"
        )

        st.success(
            result["recommended_action"]
        )


        # ====================================================
        # DISCLAIMER
        # ====================================================

        st.caption(
            "Evidence strength is a heuristic based on "
            "the available KPI change, driver count, and "
            "supporting evidence. It is not statistical "
            "confidence. Observed associations do not "
            "establish causation."
        )

        # ====================================================
        # LLM VS NON-LLM PROCESSING
        # ====================================================

        st.divider()

        st.header("LLM vs Non-LLM Processing")

        st.caption(
            "Quantitative analysis remains deterministic. "
            "The LLM is used only for language-based interpretation."
        )

        breakdown = get_llm_non_llm_breakdown()

        non_llm = breakdown["non_llm"]
        llm = breakdown["llm"]

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #444;
                    border-radius: 12px;
                    padding: 22px;
                    min-height: 430px;
                ">

                    <div style="
                        font-size: 22px;
                        font-weight: 650;
                        margin-bottom: 6px;
                    ">
                        Non-LLM Processing
                    </div>

                    <div style="
                        color: #999;
                        font-size: 13px;
                        margin-bottom: 20px;
                    ">
                        Deterministic business analysis
                    </div>

                    <div style="
                        font-size: 30px;
                        font-weight: 700;
                        margin-bottom: 18px;
                    ">
                        {non_llm["component_count"]}
                    </div>

                    <div style="
                        color: #999;
                        font-size: 12px;
                        margin-bottom: 18px;
                    ">
                        deterministic components
                    </div>
                """,
                unsafe_allow_html=True
            )

            for component in non_llm["components"]:
                st.markdown(
                    f"""
                    <div style="
                        padding: 7px 0;
                        font-size: 14px;
                        border-bottom: 1px solid rgba(255,255,255,0.06);
                    ">
                        • {component}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


        with col2:

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #444;
                    border-radius: 12px;
                    padding: 22px;
                    min-height: 430px;
                ">

                    <div style="
                        font-size: 22px;
                        font-weight: 650;
                        margin-bottom: 6px;
                    ">
                        LLM Processing
                    </div>

                    <div style="
                        color: #999;
                        font-size: 13px;
                        margin-bottom: 20px;
                    ">
                        Natural-language interpretation
                    </div>

                    <div style="
                        font-size: 30px;
                        font-weight: 700;
                        margin-bottom: 18px;
                    ">
                        {llm["component_count"]}
                    </div>

                    <div style="
                        color: #999;
                        font-size: 12px;
                        margin-bottom: 18px;
                    ">
                        LLM components
                    </div>
                """,
                unsafe_allow_html=True
            )

            for component in llm["components"]:
                st.markdown(
                    f"""
                    <div style="
                        padding: 10px 0;
                        font-size: 14px;
                        border-bottom: 1px solid rgba(255,255,255,0.06);
                    ">
                        • {component}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        # ====================================================
        # RUNTIME TELEMETRY
        # ====================================================

        st.divider()

        st.header("Runtime Telemetry")

        st.caption(
            "Runtime measurements for the LLM interaction used in this investigation."
        )

        telemetry = result.get("telemetry", {})

        if telemetry:

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Model",
                    telemetry.get("model", "Unknown")
                )

            with col2:
                st.metric(
                    "LLM Calls",
                    telemetry.get("llm_calls", 0)
                )

            with col3:
                latency = telemetry.get(
                    "latency_ms",
                    None
                )

                if latency is not None:
                    st.metric(
                        "Latency",
                        f"{latency:.2f} ms"
                    )
                else:
                    st.metric(
                        "Latency",
                        "N/A"
                    )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Input Tokens",
                    telemetry.get(
                        "input_tokens",
                        "N/A"
                    )
                )

            with col2:
                st.metric(
                    "Output Tokens",
                    telemetry.get(
                        "output_tokens",
                        "N/A"
                    )
                )

            with col3:
                st.metric(
                    "Total Tokens",
                    telemetry.get(
                        "total_tokens",
                        "N/A"
                    )
                )

            estimated_cost = telemetry.get(
                "estimated_cost",
                None
            )

            if estimated_cost is not None:
                st.metric(
                    "Estimated Cost",
                    f"${estimated_cost:.6f}"
                )
            else:
                st.metric(
                    "Estimated Cost",
                    "N/A"
                )

            if telemetry.get("error"):
                st.warning(
                    f"LLM Error: {telemetry['error']}"
                )

        else:

            st.info(
                "Runtime telemetry is not available for this investigation."
            )
                
        # ====================================================
        # ANALYST / BUSINESS FEEDBACK
        # ====================================================

        st.divider()

        st.header("Analyst / Business Feedback")

        st.caption(
            "Feedback is stored and used to refine future investigations "
            "for the same KPI, region, period, and persona."
        )

        feedback_type = st.selectbox(
            "Feedback Type",
            [
                "useful",
                "not_useful",
                "correct",
                "incorrect",
                "correction"
            ],
            key="feedback_type"
        )

        rating = st.slider(
            "Insight Rating",
            min_value=1,
            max_value=5,
            value=4,
            key="feedback_rating"
        )

        correction = st.text_area(
            "Correction",
            placeholder=(
                "Example: Support resolution hours should not "
                "be treated as a strong driver."
            ),
            key="feedback_correction"
        )

        comment = st.text_area(
            "Comment",
            placeholder=(
                "Explain why the insight should be accepted "
                "or corrected."
            ),
            key="feedback_comment"
        )

        if st.button(
            "Submit Feedback",
            key="submit_feedback"
        ):

            feedback_payload = {
                "region": result["region"],
                "date": result["date"],
                "kpi": result["kpi"],
                "persona": result["persona"],
                "feedback_type": feedback_type,
                "rating": rating,
                "correction": correction,
                "comment": comment
            }

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/feedback",
                    json=feedback_payload
                )

                if response.status_code == 200:

                    st.success(
                        "Feedback recorded successfully. "
                        "Future analyses can use this feedback."
                    )

                else:

                    st.error(
                        f"Feedback submission failed: "
                        f"{response.text}"
                    )

            except Exception as e:

                st.error(
                    f"Could not connect to InsightForge API: {e}"
                )

# ============================================================
# INITIAL STATE
# ============================================================

else:

    st.info(
        "Select a region and period, then click "
        "**Analyze KPI** to investigate a business change."
    )

    st.markdown(
        """
        ### Investigation Workflow

        **1. Detect** → Identify significant revenue movement

        **2. Analyze** → Find the strongest observed drivers

        **3. Retrieve** → Find relevant customer feedback

        **4. Rank** → Prioritize supporting evidence

        **5. Explain** → Generate an evidence-grounded AI explanation

        **6. Recommend** → Produce one practical next action
        """
    )